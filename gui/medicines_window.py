import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import DatabaseConnection
from utils.helpers import (
    format_date_arabic, validate_price, validate_quantity, 
    parse_date, log_stock_update
)

class MedicinesWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("إدارة الأدوية")
        self.window.geometry("1000x600")
        
        self.user_data = None
        
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(self.buttons_frame, text="إضافة دواء جديد", command=self.add_medicine).pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.buttons_frame, text="تحديث", command=self.refresh_medicines).pack(side=tk.RIGHT, padx=5)

        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.search_frame, text="بحث:").pack(side=tk.RIGHT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_medicines)
        ttk.Entry(self.search_frame, textvariable=self.search_var).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        self.tree = ttk.Treeview(self.main_frame, 
                                 columns=("id", "name", "price", "quantity", "expiry_date", "manufacturer", "category", "location"),
                                show="headings")
        
        for col, name, width in [
            ("id", "الرقم", 50),
            ("name", "اسم الدواء", 200),
            ("price", "السعر", 100),
            ("quantity", "الكمية", 100),
            ("expiry_date", "تاريخ الصلاحية", 120),
            ("manufacturer", "الشركة المصنعة", 150),
            ("category", "الفئة", 100),
            ("location", "الموقع", 100)
        ]:
            self.tree.heading(col, text=name)
            self.tree.column(col, width=width)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<Double-1>", self.edit_medicine)
        
        self.refresh_medicines()
        self.check_alerts()
    
    def set_user_data(self, user_data):
        self.user_data = user_data

    def refresh_medicines(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, price, quantity, expiry_date, 
                       manufacturer, category, location, min_stock_level
                FROM medicines 
                WHERE is_active = 1 
                ORDER BY name
            """)
            for medicine in cursor.fetchall():
                expiry_date = format_date_arabic(medicine[4])
                price = f"{medicine[2]:.2f}"
                values = (medicine[0], medicine[1], price, medicine[3], 
                         expiry_date, medicine[5], medicine[6], medicine[7])
                
                if medicine[3] <= medicine[8]:
                    self.tree.insert("", tk.END, values=values, tags=('low_stock',))
                else:
                    self.tree.insert("", tk.END, values=values)
            
            self.tree.tag_configure('low_stock', background='#ffcccc')
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات الأدوية: {str(e)}")
        finally:
            db.close()
    
    def search_medicines(self, *args):
        search_term = self.search_var.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.refresh_medicines()
            return
        
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, name, price, quantity, expiry_date, 
                       manufacturer, category, location, min_stock_level
                FROM medicines 
                WHERE is_active = 1 
                AND (name LIKE ? OR manufacturer LIKE ? OR category LIKE ? OR barcode LIKE ?)
                ORDER BY name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            for medicine in cursor.fetchall():
                expiry_date = format_date_arabic(medicine[4])
                price = f"{medicine[2]:.2f}"
                values = (medicine[0], medicine[1], price, medicine[3], 
                         expiry_date, medicine[5], medicine[6], medicine[7])
                
                if medicine[3] <= medicine[8]:
                    self.tree.insert("", tk.END, values=values, tags=('low_stock',))
                else:
                    self.tree.insert("", tk.END, values=values)
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء البحث: {str(e)}")
        finally:
            db.close()
    
    def add_medicine(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("إضافة دواء جديد")
        dialog.geometry("500x700")
        
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        fields = {
            "اسم الدواء: *": "name",
            "الوصف:": "description",
            "السعر: *": "price",
            "الكمية: *": "quantity",
            "تاريخ الصلاحية (DD/MM/YYYY): *": "expiry_date",
            "الشركة المصنعة:": "manufacturer",
            "الباركود:": "barcode",
            "الفئة:": "category",
            "الموقع:": "location",
            "الحد الأدنى للمخزون:": "min_stock_level"
        }

        vars = {}

        for label, key in fields.items():
            ttk.Label(form_frame, text=label).pack(pady=5)
            var = tk.StringVar()
            if key == "min_stock_level":
                var.set("10")
            ttk.Entry(form_frame, textvariable=var).pack(fill=tk.X)
            vars[key] = var

        status_label = ttk.Label(form_frame, text="")
        status_label.pack(pady=5)
        
        def save_medicine():
            try:
                # التحقق من البيانات المدخلة
                name = vars["name"].get().strip()
                price_valid, price = validate_price(vars["price"].get().strip())
                qty_valid, quantity = validate_quantity(vars["quantity"].get().strip())
                date_valid, expiry_date_db = parse_date(vars["expiry_date"].get().strip())

                if not name:
                    status_label.config(text="الرجاء إدخال اسم الدواء", foreground="red")
                    return
                if not price_valid:
                    status_label.config(text="الرجاء إدخال سعر صحيح", foreground="red")
                    return
                if not qty_valid:
                    status_label.config(text="الرجاء إدخال كمية صحيحة", foreground="red")
                    return
                if not date_valid:
                    status_label.config(text="صيغة التاريخ غير صحيحة. استخدم DD/MM/YYYY", foreground="red")
                    return

                min_stock_valid, min_stock = validate_quantity(vars["min_stock_level"].get().strip())
                if not min_stock_valid:
                    min_stock = 10

                # حفظ البيانات في قاعدة البيانات
                db = DatabaseConnection()
                conn = db.connect()
                cursor = conn.cursor()
                
                try:
                    cursor.execute("""
                        INSERT INTO medicines (
                            name, description, price, quantity, expiry_date,
                            manufacturer, barcode, category, location, min_stock_level
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                        name, vars["description"].get().strip(), price, quantity,
                        expiry_date_db, vars["manufacturer"].get().strip(),
                        vars["barcode"].get().strip(), vars["category"].get().strip(),
                        vars["location"].get().strip(), min_stock
                        ))
                    
                    medicine_id = cursor.lastrowid

                    if self.user_data:
                        log_stock_update(
                            db, medicine_id, 0, quantity,
                            self.user_data.get('username', 'unknown'), "إضافة دواء جديد"
                        )

                    conn.commit()
                    messagebox.showinfo("نجاح", "تمت إضافة الدواء بنجاح")
                    dialog.destroy()
                    self.refresh_medicines()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("خطأ", f"حدث خطأ أثناء الإضافة: {str(e)}")
                finally:
                    db.close()
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ في التحقق من البيانات: {str(e)}")
        
        ttk.Button(form_frame, text="حفظ", command=save_medicine).pack(pady=20)
    
    def edit_medicine(self, event):
        messagebox.showinfo("تحرير", "هنا سيتم تنفيذ نافذة تحرير الدواء عند الضغط المزدوج.")
    
    def check_alerts(self):
        # يمكنك تطوير هذه الدالة لاحقًا لتنبيه المستخدم بانخفاض الكمية أو قرب انتهاء الصلاحية
        pass
