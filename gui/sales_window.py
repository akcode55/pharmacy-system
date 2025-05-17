import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import DatabaseConnection
from logic.billing import BillingSystem
from datetime import datetime

class SalesWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("نظام المبيعات")
        self.window.geometry("900x700")

        # إنشاء نظام الفواتير
        self.billing_system = BillingSystem(self.window)

        # إنشاء الإطار الرئيسي
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # إنشاء إطار الأزرار
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(0, 10))

        # إضافة الأزرار
        ttk.Button(self.buttons_frame, text="فاتورة جديدة", command=self.new_sale).pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.buttons_frame, text="تحديث", command=self.refresh_sales).pack(side=tk.RIGHT, padx=5)

        # إنشاء إطار البحث
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))

        # إضافة حقل التاريخ
        ttk.Label(self.search_frame, text="التاريخ:").pack(side=tk.RIGHT, padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(self.search_frame, textvariable=self.date_var, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.search_frame, text="عرض", command=self.refresh_sales).pack(side=tk.RIGHT, padx=5)

        # إنشاء إطار الجدول
        self.table_frame = ttk.LabelFrame(self.main_frame, text="المبيعات اليومية")
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # إنشاء جدول المبيعات
        self.sales_tree = ttk.Treeview(self.table_frame, columns=("id", "date", "items", "subtotal", "discount", "vat", "total"), show="headings")
        self.sales_tree.heading("id", text="رقم الفاتورة")
        self.sales_tree.heading("date", text="التاريخ")
        self.sales_tree.heading("items", text="عدد الأصناف")
        self.sales_tree.heading("subtotal", text="المجموع الفرعي")
        self.sales_tree.heading("discount", text="الخصم")
        self.sales_tree.heading("vat", text="الضريبة")
        self.sales_tree.heading("total", text="الإجمالي")

        self.sales_tree.column("id", width=80)
        self.sales_tree.column("date", width=150)
        self.sales_tree.column("items", width=100)
        self.sales_tree.column("subtotal", width=120)
        self.sales_tree.column("discount", width=120)
        self.sales_tree.column("vat", width=120)
        self.sales_tree.column("total", width=120)

        self.sales_tree.pack(fill=tk.BOTH, expand=True)

        # إضافة شريط التمرير
        scrollbar = ttk.Scrollbar(self.sales_tree, orient=tk.VERTICAL, command=self.sales_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)

        # ربط حدث النقر المزدوج
        self.sales_tree.bind("<Double-1>", self.view_sale_details)

        # إنشاء إطار الإحصائيات
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="إحصائيات المبيعات")
        self.stats_frame.pack(fill=tk.X, pady=10)

        # إضافة حقول الإحصائيات
        self.total_sales_var = tk.StringVar(value="0.00")
        self.total_items_var = tk.StringVar(value="0")

        stats_inner_frame = ttk.Frame(self.stats_frame)
        stats_inner_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(stats_inner_frame, text="إجمالي المبيعات:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(stats_inner_frame, textvariable=self.total_sales_var, font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(stats_inner_frame, text="عدد الفواتير:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        ttk.Label(stats_inner_frame, textvariable=self.total_items_var, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # تحميل البيانات الأولية
        self.refresh_sales()

    def refresh_sales(self):
        # مسح العناصر الموجودة
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        # تحميل المبيعات من قاعدة البيانات
        date = self.date_var.get().strip()

        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # الحصول على المبيعات
            cursor.execute("""
                SELECT s.id, s.sale_date, s.subtotal, s.discount_amount,
                       s.vat_amount, s.total, COUNT(si.id) as item_count
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                WHERE date(s.sale_date) = ?
                GROUP BY s.id
                ORDER BY s.sale_date DESC
            """, (date,))

            sales = cursor.fetchall()

            # إضافة المبيعات إلى الجدول
            total_sales = 0
            for sale in sales:
                sale_id, sale_date, subtotal, discount, vat, total, item_count = sale
                self.sales_tree.insert("", tk.END, values=(
                    sale_id,
                    sale_date,
                    item_count,
                    f"{subtotal:.2f}",
                    f"{discount:.2f}",
                    f"{vat:.2f}",
                    f"{total:.2f}"
                ))
                total_sales += total

            # تحديث الإحصائيات
            from utils.helpers import format_currency_with_name
            self.total_sales_var.set(format_currency_with_name(total_sales))
            self.total_items_var.set(str(len(sales)))

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات المبيعات: {str(e)}")
        finally:
            db.close()

    def view_sale_details(self, event):
        # الحصول على العنصر المحدد
        selected_item = self.sales_tree.selection()
        if not selected_item:
            return

        # الحصول على بيانات المبيعات
        sale_id = self.sales_tree.item(selected_item[0])['values'][0]

        # إنشاء نافذة التفاصيل
        details_window = tk.Toplevel(self.window)
        details_window.title(f"تفاصيل الفاتورة #{sale_id}")
        details_window.geometry("700x500")

        # إنشاء الإطار الرئيسي
        main_frame = ttk.Frame(details_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # إنشاء جدول التفاصيل
        details_tree = ttk.Treeview(main_frame, columns=("id", "name", "quantity", "price", "total"), show="headings")
        details_tree.heading("id", text="الرقم")
        details_tree.heading("name", text="اسم الدواء")
        details_tree.heading("quantity", text="الكمية")
        details_tree.heading("price", text="السعر")
        details_tree.heading("total", text="الإجمالي")

        details_tree.column("id", width=50)
        details_tree.column("name", width=250)
        details_tree.column("quantity", width=100)
        details_tree.column("price", width=100)
        details_tree.column("total", width=100)

        details_tree.pack(fill=tk.BOTH, expand=True)

        # إضافة شريط التمرير
        scrollbar = ttk.Scrollbar(details_tree, orient=tk.VERTICAL, command=details_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        details_tree.configure(yscrollcommand=scrollbar.set)

        # تحميل تفاصيل المبيعات
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # الحصول على تفاصيل المبيعات
            cursor.execute("""
                SELECT si.id, m.name, si.quantity, si.unit_price, si.total_price
                FROM sale_items si
                JOIN medicines m ON si.medicine_id = m.id
                WHERE si.sale_id = ?
                ORDER BY si.id
            """, (sale_id,))

            items = cursor.fetchall()

            # إضافة العناصر إلى الجدول
            for item in items:
                item_id, name, quantity, price, total = item
                details_tree.insert("", tk.END, values=(
                    item_id,
                    name,
                    quantity,
                    f"{price:.2f}",
                    f"{total:.2f}"
                ))

            # الحصول على تفاصيل الفاتورة
            cursor.execute("""
                SELECT sale_date, subtotal, discount_percentage, discount_amount,
                       vat_rate, vat_amount, total
                FROM sales
                WHERE id = ?
            """, (sale_id,))

            sale = cursor.fetchone()
            if sale:
                sale_date, subtotal, discount_percentage, discount_amount, vat_rate, vat_amount, total = sale

                # إنشاء إطار التفاصيل
                details_frame = ttk.LabelFrame(main_frame, text="تفاصيل الفاتورة")
                details_frame.pack(fill=tk.X, pady=10)

                details_inner_frame = ttk.Frame(details_frame)
                details_inner_frame.pack(fill=tk.X, padx=10, pady=10)

                # الصف الأول
                ttk.Label(details_inner_frame, text="تاريخ الفاتورة:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
                ttk.Label(details_inner_frame, text=sale_date).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

                ttk.Label(details_inner_frame, text="المجموع الفرعي:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
                from utils.helpers import format_currency_with_name
                ttk.Label(details_inner_frame, text=format_currency_with_name(subtotal)).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

                # الصف الثاني
                ttk.Label(details_inner_frame, text="نسبة الخصم:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
                ttk.Label(details_inner_frame, text=f"{discount_percentage:.2f}%").grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

                ttk.Label(details_inner_frame, text="قيمة الخصم:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
                ttk.Label(details_inner_frame, text=format_currency_with_name(discount_amount)).grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

                # الصف الثالث
                ttk.Label(details_inner_frame, text="نسبة الضريبة:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
                ttk.Label(details_inner_frame, text=f"{vat_rate*100:.2f}%").grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

                ttk.Label(details_inner_frame, text="قيمة الضريبة:").grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)
                ttk.Label(details_inner_frame, text=format_currency_with_name(vat_amount)).grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)

                # الصف الرابع
                ttk.Label(details_inner_frame, text="الإجمالي:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
                ttk.Label(details_inner_frame, text=format_currency_with_name(total), font=("Arial", 12, "bold")).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

                # زر الطباعة
                ttk.Button(details_inner_frame, text="طباعة الفاتورة", command=lambda: self.print_invoice(sale_id)).grid(row=3, column=3, padx=5, pady=5, sticky=tk.E)

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل تفاصيل الفاتورة: {str(e)}")
        finally:
            db.close()

    def new_sale(self):
        # إنشاء نافذة فاتورة جديدة
        sale_window = tk.Toplevel(self.window)
        sale_window.title("فاتورة جديدة")
        sale_window.geometry("800x600")

        # إنشاء الإطار الرئيسي
        main_frame = ttk.Frame(sale_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # إنشاء إطار البحث عن الأدوية
        search_frame = ttk.LabelFrame(main_frame, text="إضافة دواء")
        search_frame.pack(fill=tk.X, pady=5)

        search_inner_frame = ttk.Frame(search_frame)
        search_inner_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(search_inner_frame, text="بحث:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        search_var = tk.StringVar()
        ttk.Entry(search_inner_frame, textvariable=search_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(search_inner_frame, text="الكمية:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(search_inner_frame, from_=1, to=1000, textvariable=quantity_var, width=5).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # قائمة الأدوية
        medicine_list = ttk.Treeview(search_inner_frame, columns=("id", "name", "price", "stock"), show="headings", height=5)
        medicine_list.heading("id", text="الرقم")
        medicine_list.heading("name", text="اسم الدواء")
        medicine_list.heading("price", text="السعر")
        medicine_list.heading("stock", text="المخزون")

        medicine_list.column("id", width=50)
        medicine_list.column("name", width=250)
        medicine_list.column("price", width=100)
        medicine_list.column("stock", width=100)

        medicine_list.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=tk.EW)

        # شريط التمرير
        scrollbar = ttk.Scrollbar(search_inner_frame, orient=tk.VERTICAL, command=medicine_list.yview)
        scrollbar.grid(row=1, column=4, sticky=tk.NS)
        medicine_list.configure(yscrollcommand=scrollbar.set)

        # زر إضافة الدواء
        ttk.Button(search_inner_frame, text="إضافة للفاتورة", command=lambda: add_to_cart()).grid(row=2, column=3, padx=5, pady=5, sticky=tk.E)

        # إنشاء إطار عناصر الفاتورة
        cart_frame = ttk.LabelFrame(main_frame, text="عناصر الفاتورة")
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # جدول عناصر الفاتورة
        cart_tree = ttk.Treeview(cart_frame, columns=("id", "name", "quantity", "price", "total"), show="headings")
        cart_tree.heading("id", text="الرقم")
        cart_tree.heading("name", text="اسم الدواء")
        cart_tree.heading("quantity", text="الكمية")
        cart_tree.heading("price", text="السعر")
        cart_tree.heading("total", text="الإجمالي")

        cart_tree.column("id", width=50)
        cart_tree.column("name", width=250)
        cart_tree.column("quantity", width=100)
        cart_tree.column("price", width=100)
        cart_tree.column("total", width=100)

        cart_tree.pack(fill=tk.BOTH, expand=True)

        # شريط التمرير
        cart_scrollbar = ttk.Scrollbar(cart_tree, orient=tk.VERTICAL, command=cart_tree.yview)
        cart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        cart_tree.configure(yscrollcommand=cart_scrollbar.set)

        # إنشاء إطار الإجماليات
        totals_frame = ttk.Frame(main_frame)
        totals_frame.pack(fill=tk.X, pady=10)

        # إضافة حقول الإجماليات
        ttk.Label(totals_frame, text="المجموع الفرعي:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        subtotal_var = tk.StringVar(value="0.00")
        ttk.Label(totals_frame, textvariable=subtotal_var).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(totals_frame, text="نسبة الخصم (%):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        discount_var = tk.DoubleVar(value=0)
        ttk.Spinbox(totals_frame, from_=0, to=100, textvariable=discount_var, width=5,
                   command=lambda: calculate_totals()).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(totals_frame, text="قيمة الخصم:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        discount_amount_var = tk.StringVar(value="0.00")
        ttk.Label(totals_frame, textvariable=discount_amount_var).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(totals_frame, text="قيمة الضريبة:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)
        vat_var = tk.StringVar(value="0.00")
        ttk.Label(totals_frame, textvariable=vat_var).grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(totals_frame, text="الإجمالي:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        total_var = tk.StringVar(value="0.00")
        ttk.Label(totals_frame, textvariable=total_var, font=("Arial", 12, "bold")).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # إضافة أزرار الإجراءات
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(buttons_frame, text="حذف العنصر المحدد", command=lambda: remove_item()).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="إلغاء", command=sale_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="حفظ الفاتورة", command=lambda: save_sale()).pack(side=tk.RIGHT, padx=5)

        # قائمة لتخزين العناصر المضافة
        cart_items = []

        # دالة البحث عن الأدوية
        def search_medicines(*args):
            search_term = search_var.get().strip()

            # مسح القائمة الحالية
            for item in medicine_list.get_children():
                medicine_list.delete(item)

            if not search_term:
                return

            # البحث في قاعدة البيانات
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    SELECT id, name, price, quantity
                    FROM medicines
                    WHERE name LIKE ? AND quantity > 0
                    ORDER BY name
                    LIMIT 10
                """, ("%" + search_term + "%",))

                for medicine in cursor.fetchall():
                    # تنسيق السعر لعرضه بشكل صحيح
                    formatted_medicine = list(medicine)
                    formatted_medicine[2] = float(medicine[2])  # تأكد من أن السعر رقم عشري
                    medicine_list.insert("", tk.END, values=formatted_medicine)
            except Exception as e:
                messagebox.showerror("خطأ", "حدث خطأ أثناء البحث: " + str(e))
            finally:
                db.close()

        # ربط دالة البحث بتغيير النص
        search_var.trace('w', search_medicines)

        # دالة إضافة دواء للفاتورة
        def add_to_cart():
            selected = medicine_list.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "الرجاء اختيار دواء من القائمة")
                return

            # الحصول على بيانات الدواء المحدد
            medicine_data = medicine_list.item(selected[0])['values']
            medicine_id = medicine_data[0]
            medicine_name = medicine_data[1]
            medicine_price = float(medicine_data[2])  # تحويل السعر إلى رقم عشري
            medicine_stock = medicine_data[3]

            # التحقق من الكمية
            quantity = quantity_var.get()
            if quantity <= 0:
                messagebox.showwarning("تنبيه", "الرجاء إدخال كمية صحيحة")
                return

            if quantity > medicine_stock:
                messagebox.showwarning("تنبيه", "الكمية المتوفرة ({}) أقل من الكمية المطلوبة ({})".format(medicine_stock, quantity))
                return

            # التحقق مما إذا كان الدواء موجودًا بالفعل في الفاتورة
            for i, item in enumerate(cart_items):
                if item['medicine_id'] == medicine_id:
                    # تحديث الكمية إذا كان الدواء موجودًا بالفعل
                    new_quantity = item['quantity'] + quantity
                    if new_quantity > medicine_stock:
                        messagebox.showwarning("تنبيه", "الكمية المتوفرة ({}) أقل من الكمية المطلوبة ({})".format(medicine_stock, new_quantity))
                        return

                    cart_items[i]['quantity'] = new_quantity
                    cart_items[i]['total'] = new_quantity * medicine_price

                    # تحديث العرض
                    refresh_cart()
                    calculate_totals()
                    return

            # إضافة الدواء إلى الفاتورة
            item = {
                'medicine_id': medicine_id,
                'name': medicine_name,
                'quantity': quantity,
                'price': medicine_price,
                'total': quantity * medicine_price
            }

            cart_items.append(item)

            # تحديث العرض
            refresh_cart()
            calculate_totals()

        # دالة تحديث عرض عناصر الفاتورة
        def refresh_cart():
            # مسح العناصر الحالية
            for item in cart_tree.get_children():
                cart_tree.delete(item)

            # إضافة العناصر الجديدة
            for i, item in enumerate(cart_items):
                price_str = "{:.2f}".format(item['price'])
                total_str = "{:.2f}".format(item['total'])
                cart_tree.insert("", tk.END, values=(
                    item['medicine_id'],
                    item['name'],
                    item['quantity'],
                    price_str,
                    total_str
                ))

        # دالة حساب الإجماليات
        def calculate_totals():
            subtotal = sum(item['total'] for item in cart_items)
            discount_percentage = discount_var.get()

            # حساب الإجماليات باستخدام نظام الفواتير
            totals = self.billing_system.calculate_total_with_tax_and_discount(subtotal, discount_percentage)

            # تحديث المتغيرات
            subtotal_var.set("{:.2f} ريال".format(totals['subtotal']))
            discount_amount_var.set("{:.2f} ريال".format(totals['discount_amount']))
            vat_var.set("{:.2f} ريال".format(totals['vat_amount']))
            total_var.set("{:.2f} ريال".format(totals['total']))

        # دالة حذف عنصر من الفاتورة
        def remove_item():
            selected = cart_tree.selection()
            if not selected:
                messagebox.showwarning("تنبيه", "الرجاء اختيار عنصر من الفاتورة")
                return

            # الحصول على بيانات العنصر المحدد
            item_data = cart_tree.item(selected[0])['values']
            medicine_id = item_data[0]

            # حذف العنصر من القائمة
            for i, item in enumerate(cart_items):
                if item['medicine_id'] == medicine_id:
                    del cart_items[i]
                    break

            # تحديث العرض
            refresh_cart()
            calculate_totals()

        # دالة حفظ الفاتورة
        def save_sale():
            if not cart_items:
                messagebox.showwarning("تنبيه", "لا توجد أصناف في الفاتورة")
                return

            discount_percentage = discount_var.get()

            # استخدام نظام الفواتير لإنشاء الفاتورة
            success, total = self.billing_system.create_sale(cart_items, discount_percentage)

            if success:
                from utils.helpers import format_currency_with_name
                messagebox.showinfo("نجاح", "تم حفظ الفاتورة بنجاح بقيمة {}".format(format_currency_with_name(total)))
                sale_window.destroy()
                self.refresh_sales()
            else:
                messagebox.showerror("خطأ", "حدث خطأ أثناء حفظ الفاتورة")

    def print_invoice(self, sale_id):
        """طباعة الفاتورة"""
        # الحصول على بيانات الفاتورة
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # الحصول على تفاصيل الفاتورة
            cursor.execute("""
                SELECT s.id, s.sale_date, s.subtotal, s.discount_percentage, s.discount_amount,
                       s.vat_rate, s.vat_amount, s.total
                FROM sales s
                WHERE s.id = ?
            """, (sale_id,))

            sale = cursor.fetchone()
            if not sale:
                messagebox.showerror("خطأ", "لم يتم العثور على الفاتورة")
                return

            sale_id, sale_date, subtotal, discount_percentage, discount_amount, vat_rate, vat_amount, total = sale

            # الحصول على عناصر الفاتورة
            cursor.execute("""
                SELECT si.id, m.name, si.quantity, si.unit_price, si.total_price
                FROM sale_items si
                JOIN medicines m ON si.medicine_id = m.id
                WHERE si.sale_id = ?
                ORDER BY si.id
            """, (sale_id,))

            items = cursor.fetchall()

            # إنشاء نافذة الطباعة
            print_window = tk.Toplevel(self.window)
            print_window.title(f"طباعة الفاتورة #{sale_id}")
            print_window.geometry("600x800")

            # إنشاء إطار الطباعة
            print_frame = ttk.Frame(print_window)
            print_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # إضافة عنواء الفاتورة
            ttk.Label(print_frame, text="صيدلية الشفاء", font=("Arial", 16, "bold")).pack(pady=5)
            ttk.Label(print_frame, text="فاتورة مبيعات", font=("Arial", 14)).pack(pady=5)
            ttk.Separator(print_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

            # إضافة تفاصيل الفاتورة
            details_frame = ttk.Frame(print_frame)
            details_frame.pack(fill=tk.X, pady=5)

            ttk.Label(details_frame, text=f"رقم الفاتورة: {sale_id}", font=("Arial", 12)).pack(side=tk.RIGHT, padx=10)
            ttk.Label(details_frame, text=f"التاريخ: {sale_date}", font=("Arial", 12)).pack(side=tk.RIGHT, padx=10)

            # إضافة جدول العناصر
            items_frame = ttk.Frame(print_frame)
            items_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            # إنشاء عناوين الجدول
            headers_frame = ttk.Frame(items_frame)
            headers_frame.pack(fill=tk.X)

            ttk.Label(headers_frame, text="الرقم", width=5, font=("Arial", 10, "bold"), relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
            ttk.Label(headers_frame, text="اسم الدواء", width=25, font=("Arial", 10, "bold"), relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
            ttk.Label(headers_frame, text="الكمية", width=8, font=("Arial", 10, "bold"), relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
            ttk.Label(headers_frame, text="السعر", width=10, font=("Arial", 10, "bold"), relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
            ttk.Label(headers_frame, text="الإجمالي", width=10, font=("Arial", 10, "bold"), relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)

            # إضافة العناصر
            for i, item in enumerate(items, 1):
                item_id, name, quantity, price, item_total = item
                item_frame = ttk.Frame(items_frame)
                item_frame.pack(fill=tk.X)

                ttk.Label(item_frame, text=str(i), width=5, relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
                ttk.Label(item_frame, text=name, width=25, relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
                ttk.Label(item_frame, text=str(quantity), width=8, relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
                ttk.Label(item_frame, text=f"{price:.2f}", width=10, relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)
                ttk.Label(item_frame, text=f"{item_total:.2f}", width=10, relief=tk.RIDGE).pack(side=tk.RIGHT, padx=1, pady=1)

            # إضافة الإجماليات
            ttk.Separator(print_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

            totals_frame = ttk.Frame(print_frame)
            totals_frame.pack(fill=tk.X, pady=5)

            # إنشاء جدول الإجماليات
            ttk.Label(totals_frame, text="المجموع الفرعي:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
            from utils.helpers import format_currency_with_name
            ttk.Label(totals_frame, text=format_currency_with_name(subtotal)).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

            ttk.Label(totals_frame, text=f"الخصم ({discount_percentage:.2f}%):", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
            ttk.Label(totals_frame, text=format_currency_with_name(discount_amount)).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

            ttk.Label(totals_frame, text=f"الضريبة ({vat_rate*100:.2f}%):", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
            ttk.Label(totals_frame, text=format_currency_with_name(vat_amount)).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            ttk.Separator(totals_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)

            ttk.Label(totals_frame, text="الإجمالي:", font=("Arial", 12, "bold")).grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
            ttk.Label(totals_frame, text=format_currency_with_name(total), font=("Arial", 12, "bold")).grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

            # إضافة التذييل
            ttk.Separator(print_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            ttk.Label(print_frame, text="شكراً لزيارتكم", font=("Arial", 12)).pack(pady=5)

            # إضافة أزرار الطباعة
            buttons_frame = ttk.Frame(print_frame)
            buttons_frame.pack(fill=tk.X, pady=10)

            ttk.Button(buttons_frame, text="طباعة", command=lambda: self.send_to_printer(print_frame)).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="إغلاق", command=print_window.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحضير الفاتورة للطباعة: {str(e)}")
        finally:
            db.close()

    def send_to_printer(self, frame):
        """إرسال الفاتورة للطابعة"""
        try:
            # هنا يمكن إضافة كود للطباعة الفعلية
            # يمكن استخدام مكتبات مثل win32print أو pdfkit
            messagebox.showinfo("طباعة", "تم إرسال الفاتورة للطباعة")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")

    def export_sales_report(self):
        """تصدير تقرير المبيعات"""
        from datetime import datetime
        import csv
        import os

        # الحصول على التاريخ
        date = self.date_var.get().strip()

        # إنشاء اسم الملف
        filename = f"sales_report_{date}.csv"

        # فتح مربع حوار لاختيار مكان حفظ الملف
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=filename
        )

        if not filepath:
            return

        # الحصول على بيانات المبيعات
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # الحصول على المبيعات
            cursor.execute("""
                SELECT s.id, s.sale_date, s.subtotal, s.discount_amount,
                       s.vat_amount, s.total, COUNT(si.id) as item_count
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                WHERE date(s.sale_date) = ?
                GROUP BY s.id
                ORDER BY s.sale_date DESC
            """, (date,))

            sales = cursor.fetchall()

            # كتابة البيانات إلى ملف CSV
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # كتابة العناوين
                writer.writerow(['رقم الفاتورة', 'التاريخ', 'عدد الأصناف', 'المجموع الفرعي', 'الخصم', 'الضريبة', 'الإجمالي'])

                # كتابة البيانات
                total_sales = 0
                for sale in sales:
                    sale_id, sale_date, subtotal, discount, vat, total, item_count = sale
                    writer.writerow([
                        sale_id,
                        sale_date,
                        item_count,
                        f"{subtotal:.2f}",
                        f"{discount:.2f}",
                        f"{vat:.2f}",
                        f"{total:.2f}"
                    ])
                    total_sales += total

                # كتابة الإجمالي
                writer.writerow([])
                writer.writerow(['الإجمالي', '', '', '', '', '', f"{total_sales:.2f}"])

            messagebox.showinfo("تصدير التقرير", f"تم تصدير تقرير المبيعات بنجاح إلى:\n{filepath}")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير تقرير المبيعات: {str(e)}")
        finally:
            db.close()

    def generate_monthly_report(self):
        """إنشاء تقرير شهري للمبيعات"""
        # إنشاء نافذة التقرير الشهري
        report_window = tk.Toplevel(self.window)
        report_window.title("تقرير المبيعات الشهري")
        report_window.geometry("800x600")

        # إنشاء الإطار الرئيسي
        main_frame = ttk.Frame(report_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # إنشاء إطار اختيار الشهر
        date_frame = ttk.LabelFrame(main_frame, text="اختيار الشهر")
        date_frame.pack(fill=tk.X, pady=5)

        date_inner_frame = ttk.Frame(date_frame)
        date_inner_frame.pack(fill=tk.X, padx=10, pady=10)

        # إضافة حقول اختيار الشهر والسنة
        ttk.Label(date_inner_frame, text="الشهر:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        month_var = tk.IntVar(value=datetime.now().month)
        month_combo = ttk.Combobox(date_inner_frame, textvariable=month_var, width=5)
        month_combo['values'] = list(range(1, 13))
        month_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(date_inner_frame, text="السنة:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        year_var = tk.IntVar(value=datetime.now().year)
        year_combo = ttk.Combobox(date_inner_frame, textvariable=year_var, width=6)
        year_combo['values'] = list(range(datetime.now().year - 5, datetime.now().year + 1))
        year_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Button(date_inner_frame, text="عرض", command=lambda: load_monthly_report()).grid(row=0, column=4, padx=5, pady=5)

        # إنشاء إطار الرسم البياني
        chart_frame = ttk.LabelFrame(main_frame, text="الرسم البياني للمبيعات")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # إنشاء إطار الإحصائيات
        stats_frame = ttk.LabelFrame(main_frame, text="إحصائيات الشهر")
        stats_frame.pack(fill=tk.X, pady=5)

        stats_inner_frame = ttk.Frame(stats_frame)
        stats_inner_frame.pack(fill=tk.X, padx=10, pady=10)

        # إضافة حقول الإحصائيات
        total_sales_var = tk.StringVar(value="0.00")
        total_items_var = tk.StringVar(value="0")
        avg_sales_var = tk.StringVar(value="0.00")

        ttk.Label(stats_inner_frame, text="إجمالي المبيعات:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(stats_inner_frame, textvariable=total_sales_var, font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(stats_inner_frame, text="عدد الفواتير:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        ttk.Label(stats_inner_frame, textvariable=total_items_var, font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(stats_inner_frame, text="متوسط المبيعات اليومي:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(stats_inner_frame, textvariable=avg_sales_var, font=("Arial", 12, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # إضافة أزرار الإجراءات
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(buttons_frame, text="تصدير التقرير", command=lambda: export_monthly_report()).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="إغلاق", command=report_window.destroy).pack(side=tk.LEFT, padx=5)

        # دالة تحميل التقرير الشهري
        def load_monthly_report():
            month = month_var.get()
            year = year_var.get()

            # التحقق من صحة البيانات
            if month < 1 or month > 12 or year < 2000:
                messagebox.showwarning("تنبيه", "الرجاء إدخال شهر وسنة صحيحين")
                return

            # الحصول على بيانات المبيعات
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()

            try:
                # الحصول على المبيعات اليومية للشهر
                cursor.execute("""
                    SELECT date(s.sale_date) as day, SUM(s.total) as daily_total, COUNT(s.id) as invoice_count
                    FROM sales s
                    WHERE strftime('%m', s.sale_date) = ? AND strftime('%Y', s.sale_date) = ?
                    GROUP BY date(s.sale_date)
                    ORDER BY day
                """, (f"{month:02d}", f"{year}"))

                daily_sales = cursor.fetchall()

                # حساب الإحصائيات
                total_sales = 0
                total_invoices = 0

                for day, daily_total, invoice_count in daily_sales:
                    total_sales += daily_total
                    total_invoices += invoice_count

                # تحديث الإحصائيات
                total_sales_var.set(f"{total_sales:.2f} ريال")
                total_items_var.set(str(total_invoices))

                # حساب متوسط المبيعات اليومي
                if len(daily_sales) > 0:
                    avg_sales = total_sales / len(daily_sales)
                    avg_sales_var.set(f"{avg_sales:.2f} ريال")
                else:
                    avg_sales_var.set("0.00 ريال")

                # هنا يمكن إضافة كود لعرض الرسم البياني
                # يمكن استخدام مكتبات مثل matplotlib أو plotly

                # مثال بسيط لعرض البيانات في جدول
                for widget in chart_frame.winfo_children():
                    widget.destroy()

                if len(daily_sales) > 0:
                    # إنشاء جدول لعرض المبيعات اليومية
                    daily_tree = ttk.Treeview(chart_frame, columns=("day", "total", "count"), show="headings")
                    daily_tree.heading("day", text="اليوم")
                    daily_tree.heading("total", text="إجمالي المبيعات")
                    daily_tree.heading("count", text="عدد الفواتير")

                    daily_tree.column("day", width=150)
                    daily_tree.column("total", width=150)
                    daily_tree.column("count", width=150)

                    daily_tree.pack(fill=tk.BOTH, expand=True)

                    # إضافة شريط التمرير
                    scrollbar = ttk.Scrollbar(daily_tree, orient=tk.VERTICAL, command=daily_tree.yview)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    daily_tree.configure(yscrollcommand=scrollbar.set)

                    # إضافة البيانات
                    for day, daily_total, invoice_count in daily_sales:
                        daily_tree.insert("", tk.END, values=(
                            day,
                            f"{daily_total:.2f}",
                            invoice_count
                        ))
                else:
                    ttk.Label(chart_frame, text="لا توجد بيانات للشهر المحدد", font=("Arial", 14)).pack(pady=50)

            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات المبيعات الشهرية: {str(e)}")
            finally:
                db.close()

        # دالة تصدير التقرير الشهري
        def export_monthly_report():
            month = month_var.get()
            year = year_var.get()

            # التحقق من صحة البيانات
            if month < 1 or month > 12 or year < 2000:
                messagebox.showwarning("تنبيه", "الرجاء إدخال شهر وسنة صحيحين")
                return

            # إنشاء اسم الملف
            filename = f"monthly_sales_report_{year}_{month:02d}.csv"

            # فتح مربع حوار لاختيار مكان حفظ الملف
            from tkinter import filedialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename
            )

            if not filepath:
                return

            # الحصول على بيانات المبيعات
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()

            try:
                # الحصول على المبيعات اليومية للشهر
                cursor.execute("""
                    SELECT date(s.sale_date) as day, SUM(s.total) as daily_total, COUNT(s.id) as invoice_count
                    FROM sales s
                    WHERE strftime('%m', s.sale_date) = ? AND strftime('%Y', s.sale_date) = ?
                    GROUP BY date(s.sale_date)
                    ORDER BY day
                """, (f"{month:02d}", f"{year}"))

                daily_sales = cursor.fetchall()

                # كتابة البيانات إلى ملف CSV
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)

                    # كتابة العناوين
                    writer.writerow(['اليوم', 'إجمالي المبيعات', 'عدد الفواتير'])

                    # كتابة البيانات
                    total_sales = 0
                    total_invoices = 0

                    for day, daily_total, invoice_count in daily_sales:
                        writer.writerow([
                            day,
                            f"{daily_total:.2f}",
                            invoice_count
                        ])
                        total_sales += daily_total
                        total_invoices += invoice_count

                    # كتابة الإجمالي
                    writer.writerow([])
                    writer.writerow(['الإجمالي', f"{total_sales:.2f}", total_invoices])

                    # كتابة المتوسط
                    if len(daily_sales) > 0:
                        avg_sales = total_sales / len(daily_sales)
                        writer.writerow(['المتوسط اليومي', f"{avg_sales:.2f}", f"{total_invoices/len(daily_sales):.2f}"])

                messagebox.showinfo("تصدير التقرير", f"تم تصدير تقرير المبيعات الشهري بنجاح إلى:\n{filepath}")

            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير تقرير المبيعات الشهري: {str(e)}")
            finally:
                db.close()

        # تحميل البيانات الأولية
        load_monthly_report()