import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import qrcode
from PIL import Image, ImageTk
import io
import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Change as needed
        password="H@rish@1723",         # Your MySQL password
        database="vending_db"
    )

class VendingMachineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🥤 SIT-College Vending Machine")
        self.root.geometry("850x650")
        self.root.configure(bg="white")

        tk.Label(root, text="SIT‑College Vending", font=("Arial", 22, "bold"), bg="skyblue").pack(fill=tk.X)

        # TreeView
        self.tree = ttk.Treeview(root, columns=("Code", "Name", "Category", "Price"), show="headings", height=10)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(pady=15)

        # Input section
        frm = tk.Frame(root, bg="white"); frm.pack(pady=10)
        tk.Label(frm, text="Item Code:", bg="white").grid(row=0, column=0, padx=5)
        self.code_entry = tk.Entry(frm, font=("Arial", 12), width=10); self.code_entry.grid(row=0, column=1, padx=5)
        tk.Label(frm, text="GPay No:", bg="white").grid(row=1, column=0, padx=5)
        self.gpay_entry = tk.Entry(frm, font=("Arial", 12), width=15); self.gpay_entry.grid(row=1, column=1, padx=5)

        tk.Button(root, text="Purchase & Receipt", bg="green", fg="white",
                  command=self.purchase_with_receipt).pack(pady=10)

        self.status_lbl = tk.Label(root, text="", bg="white", font=("Arial", 12))
        self.status_lbl.pack()

        # QR display label
        self.qr_lbl = tk.Label(root, bg="white")
        self.qr_lbl.pack(pady=10)

        self.load_items()

    def load_items(self):
        self.tree.delete(*self.tree.get_children())
        try:
            db = connect_db(); cursor = db.cursor()
            cursor.execute("SELECT * FROM items")
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Loading failed:\n{e}")

    def purchase_with_receipt(self):
        code = self.code_entry.get().strip().upper()
        gpay = self.gpay_entry.get().strip()

        if not code or not gpay:
            messagebox.showwarning("Input Error", "Enter item code & GPay number")
            return
        if not gpay.isdigit() or len(gpay) != 10:
            messagebox.showwarning("Invalid GPay", "Enter a valid 10-digit GPay mobile number")
            return

        try:
            db = connect_db(); cursor = db.cursor()
            cursor.execute("SELECT name, price FROM items WHERE code=%s", (code,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Not Found", f"No item with code {code}")
                return
            name, price = result
            cursor.execute("INSERT INTO transactions (item_code, amount, gpay_number) VALUES (%s, %s, %s)",
                           (code, price, gpay))
            db.commit()
            db.close()

            self.status_lbl.config(text=f"✅ Purchased: {name} for ₹{price:.2f}", fg="green")
            self.generate_receipt(code, name, price, gpay)
            self.code_entry.delete(0, tk.END); self.gpay_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Purchase Error", str(e))

    def generate_receipt(self, code, name, price, gpay):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use plain dash '-' and ASCII-safe characters
        text = (f"SIT-College Vending Receipt\n"
                f"--------------------------\n"
                f"Item Code: {code}\n"
                f"Item Name: {name}\n"
                f"Price Rs: {price:.2f}\n"
                f"GPay No: {gpay}\n"
                f"Timestamp: {now}\n")

        file = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt")],
                                            title="Save Receipt")
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_lbl.config(text=f"📄 Receipt saved: {file}")

        # QR code (safe ASCII data)
        qr_data = f"{code}|{name}|{price:.2f}|{gpay}|{now}"
        qr = qrcode.make(qr_data)
        qr_thumb = qr.resize((180, 180))
        img = ImageTk.PhotoImage(qr_thumb)
        self.qr_lbl.config(image=img)
        self.qr_lbl.image = img

        # Generate QR code
        qr_data = f"{code}|{name}|{price:.2f}|{gpay}|{now}"
        qr = qrcode.make(qr_data)
        qr_thumb = qr.resize((180, 180))
        img = ImageTk.PhotoImage(qr_thumb)
        self.qr_lbl.config(image=img); self.qr_lbl.image = img

if __name__ == "__main__":
    root = tk.Tk()
    app = VendingMachineApp(root)
    root.mainloop()
