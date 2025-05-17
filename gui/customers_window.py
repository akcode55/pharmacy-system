import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import DatabaseConnection

class CustomersWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("إدارة العملاء")
        self.window.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add buttons
        ttk.Button(self.buttons_frame, text="إضافة عميل جديد", command=self.add_customer).pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.buttons_frame, text="تحديث", command=self.refresh_customers).pack(side=tk.RIGHT, padx=5)
        
        # Create search frame
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.search_frame, text="بحث:").pack(side=tk.RIGHT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_customers)
        ttk.Entry(self.search_frame, textvariable=self.search_var).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(self.main_frame, columns=("id", "name", "phone", "email", "points"), show="headings")
        self.tree.heading("id", text="الرقم")
        self.tree.heading("name", text="الاسم")
        self.tree.heading("phone", text="الهاتف")
        self.tree.heading("email", text="البريد الإلكتروني")
        self.tree.heading("points", text="نقاط الولاء")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("phone", width=150)
        self.tree.column("email", width=200)
        self.tree.column("points", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double click event
        self.tree.bind("<Double-1>", self.edit_customer)
        
        # Load initial data
        self.refresh_customers()
    
    def refresh_customers(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load customers from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, name, phone, email, loyalty_points FROM customers ORDER BY name")
            for customer in cursor.fetchall():
                self.tree.insert("", tk.END, values=customer)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات العملاء: {str(e)}")
        finally:
            db.close()
    
    def search_customers(self, *args):
        search_term = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.refresh_customers()
            return
        
        # Search in database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, phone, email, loyalty_points 
                FROM customers 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
                ORDER BY name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            for customer in cursor.fetchall():
                self.tree.insert("", tk.END, values=customer)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء البحث: {str(e)}")
        finally:
            db.close()
    
    def add_customer(self):
        # Create add customer dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("إضافة عميل جديد")
        dialog.geometry("400x300")
        
        # Create form
        ttk.Label(dialog, text="الاسم:").pack(pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="الهاتف:").pack(pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=phone_var).pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="البريد الإلكتروني:").pack(pady=5)
        email_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=email_var).pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="العنوان:").pack(pady=5)
        address_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=address_var).pack(fill=tk.X, padx=5)
        
        def save_customer():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("خطأ", "الرجاء إدخال اسم العميل")
                return
            
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO customers (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                """, (name, phone_var.get().strip(), email_var.get().strip(), address_var.get().strip()))
                conn.commit()
                messagebox.showinfo("نجاح", "تم إضافة العميل بنجاح")
                dialog.destroy()
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء إضافة العميل: {str(e)}")
            finally:
                db.close()
        
        ttk.Button(dialog, text="حفظ", command=save_customer).pack(pady=20)
    
    def edit_customer(self, event):
        # Get selected item
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Get customer data
        customer_id = self.tree.item(selected_item[0])['values'][0]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.window)
        dialog.title("تعديل بيانات العميل")
        dialog.geometry("400x300")
        
        # Load customer data
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name, phone, email, address FROM customers WHERE id = ?", (customer_id,))
            customer = cursor.fetchone()
            
            if not customer:
                messagebox.showerror("خطأ", "لم يتم العثور على العميل")
                dialog.destroy()
                return
            
            # Create form
            ttk.Label(dialog, text="الاسم:").pack(pady=5)
            name_var = tk.StringVar(value=customer[0])
            ttk.Entry(dialog, textvariable=name_var).pack(fill=tk.X, padx=5)
            
            ttk.Label(dialog, text="الهاتف:").pack(pady=5)
            phone_var = tk.StringVar(value=customer[1] or "")
            ttk.Entry(dialog, textvariable=phone_var).pack(fill=tk.X, padx=5)
            
            ttk.Label(dialog, text="البريد الإلكتروني:").pack(pady=5)
            email_var = tk.StringVar(value=customer[2] or "")
            ttk.Entry(dialog, textvariable=email_var).pack(fill=tk.X, padx=5)
            
            ttk.Label(dialog, text="العنوان:").pack(pady=5)
            address_var = tk.StringVar(value=customer[3] or "")
            ttk.Entry(dialog, textvariable=address_var).pack(fill=tk.X, padx=5)
            
            def update_customer():
                name = name_var.get().strip()
                if not name:
                    messagebox.showerror("خطأ", "الرجاء إدخال اسم العميل")
                    return
                
                try:
                    cursor.execute("""
                        UPDATE customers 
                        SET name = ?, phone = ?, email = ?, address = ?
                        WHERE id = ?
                    """, (name, phone_var.get().strip(), email_var.get().strip(), 
                         address_var.get().strip(), customer_id))
                    conn.commit()
                    messagebox.showinfo("نجاح", "تم تحديث بيانات العميل بنجاح")
                    dialog.destroy()
                    self.refresh_customers()
                except Exception as e:
                    messagebox.showerror("خطأ", f"حدث خطأ أثناء تحديث بيانات العميل: {str(e)}")
            
            ttk.Button(dialog, text="حفظ التغييرات", command=update_customer).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات العميل: {str(e)}")
            dialog.destroy()
        finally:
            db.close() 