import tkinter as tk
from tkinter import ttk, messagebox
from gui.customers_window import CustomersWindow
from gui.medicines_window import MedicinesWindow
from gui.sales_window import SalesWindow
from gui.reports_window import ReportsWindow
from database.db_connection import DatabaseConnection
from gui.custom_theme import create_sidebar, create_stat_box, create_header, BACKGROUND_COLOR

class MainWindow:
    def __init__(self, parent, user_data):
        self.window = parent
        self.window.title("نظام إدارة الصيدلية")
        self.window.geometry("1024x768")

        # Store user data
        self.user_data = user_data

        # Set window background color
        self.window.configure(bg=BACKGROUND_COLOR)

        # Create main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar with buttons - only include implemented features
        buttons_config = [
            {'text': 'لوحة التحكم', 'command': self.refresh_dashboard},
            {'text': 'المبيعات', 'command': self.open_sales_window},
            {'text': 'الأدوية', 'command': self.open_medicines_window},
            {'text': 'العملاء', 'command': self.open_customers_window},
            {'text': 'التقارير', 'command': self.open_reports_window}
        ]
        self.sidebar = create_sidebar(self.main_container, buttons_config)

        # Set the window icon (if available)
        try:
            self.window.iconbitmap('assets/icon.ico')
        except:
            pass  # Icon file not found, continue without it

        # Create content area
        self.content_area = ttk.Frame(self.main_container)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create header
        self.header = create_header(self.content_area, "لوحة التحكم",
                                   user_data['username'], user_data['role'])

        # Create dashboard frame
        self.dashboard_frame = ttk.Frame(self.content_area)
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add dashboard widgets
        self.create_dashboard()

    def create_menu(self):
        menubar = tk.Menu(self.window)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="تسجيل الخروج", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.window.quit)
        menubar.add_cascade(label="ملف", menu=file_menu)

        # Customers menu
        customers_menu = tk.Menu(menubar, tearoff=0)
        customers_menu.add_command(label="إدارة العملاء", command=self.open_customers_window)
        customers_menu.add_command(label="إضافة عميل جديد", command=self.add_new_customer)
        menubar.add_cascade(label="العملاء", menu=customers_menu)

        # Medicines menu
        medicines_menu = tk.Menu(menubar, tearoff=0)
        medicines_menu.add_command(label="إدارة الأدوية", command=self.open_medicines_window)
        medicines_menu.add_command(label="إضافة دواء جديد", command=self.add_new_medicine)
        menubar.add_cascade(label="الأدوية", menu=medicines_menu)

        # Sales menu
        sales_menu = tk.Menu(menubar, tearoff=0)
        sales_menu.add_command(label="المبيعات", command=self.open_sales_window)
        sales_menu.add_command(label="فاتورة جديدة", command=self.new_sale)
        menubar.add_cascade(label="المبيعات", menu=sales_menu)

        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="تقرير المبيعات", command=self.sales_report)
        reports_menu.add_command(label="تقرير المخزون", command=self.inventory_report)
        reports_menu.add_command(label="تقرير العملاء", command=self.customers_report)
        menubar.add_cascade(label="التقارير", menu=reports_menu)

        self.window.config(menu=menubar)

    def create_dashboard(self):
        # Clear previous widgets
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()

        # Create title
        title_frame = ttk.Frame(self.dashboard_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(title_frame, text="إحصائيات النظام",
                 font=("Arial", 14, "bold")).pack(anchor='e')

        # Create dashboard widgets
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill=tk.X, pady=10)

        # Configure grid columns to be equal width
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # Get statistics from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # Get total customers
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]

            # Get total medicines
            cursor.execute("SELECT COUNT(*) FROM medicines")
            total_medicines = cursor.fetchone()[0]

            # Get low stock medicines
            cursor.execute("""
                SELECT COUNT(*) FROM medicines
                WHERE quantity <= min_stock_level
            """)
            low_stock = cursor.fetchone()[0]

            # Get today's sales
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total), 0)
                FROM sales
                WHERE date(sale_date) = date('now')
            """)
            today_sales = cursor.fetchone()

            # Create stat boxes with icons
            from utils.helpers import format_currency_with_name
            self.create_stat_box(stats_frame, "إجمالي العملاء", total_customers, 0)
            self.create_stat_box(stats_frame, "إجمالي الأدوية", total_medicines, 1)
            self.create_stat_box(stats_frame, "أدوية منخفضة المخزون", low_stock, 2)
            self.create_stat_box(stats_frame, "مبيعات اليوم", f"{today_sales[0]} ({format_currency_with_name(today_sales[1])})", 3)

            # Add recent activity section
            self.create_recent_activity()

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل الإحصائيات: {str(e)}")
        finally:
            db.close()

    def create_recent_activity(self):
        """Create a section for recent activities"""
        # Create frame for recent activities
        recent_frame = ttk.LabelFrame(self.dashboard_frame, text="آخر النشاطات")
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        # Create columns for different activities
        activities_container = ttk.Frame(recent_frame)
        activities_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid columns
        activities_container.columnconfigure(0, weight=1)
        activities_container.columnconfigure(1, weight=1)

        # Recent sales
        sales_frame = ttk.Frame(activities_container)
        sales_frame.grid(row=0, column=0, sticky="nsew", padx=10)

        ttk.Label(sales_frame, text="آخر المبيعات", font=("Arial", 12, "bold")).pack(anchor='e', pady=(0, 10))

        # Get recent sales
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT s.id, c.name, s.total, s.sale_date
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                ORDER BY s.sale_date DESC
                LIMIT 5
            """)

            sales = cursor.fetchall()

            if sales:
                for sale in sales:
                    _, customer, total, _ = sale  # Unpacking values, ignoring unused ones
                    if not customer:
                        customer = "عميل نقدي"

                    sale_frame = ttk.Frame(sales_frame)
                    sale_frame.pack(fill=tk.X, pady=2)

                    from utils.helpers import format_currency_with_name
                    ttk.Label(sale_frame, text=f"{customer}", font=("Arial", 10, "bold")).pack(side=tk.RIGHT)
                    ttk.Label(sale_frame, text=format_currency_with_name(total)).pack(side=tk.LEFT)
            else:
                ttk.Label(sales_frame, text="لا توجد مبيعات حديثة").pack(pady=10)

        except Exception as e:
            ttk.Label(sales_frame, text=f"خطأ: {str(e)}").pack(pady=10)
        finally:
            db.close()

    def create_stat_box(self, parent, title, value, column):
        return create_stat_box(parent, title, value, column)

    def open_customers_window(self):
        CustomersWindow(self.window)

    def open_medicines_window(self):
        """فتح نافذة إدارة الأدوية مع تمرير بيانات المستخدم."""
        from gui.medicines_window import MedicinesWindow
        medicines_window = MedicinesWindow(self.window)
        medicines_window.set_user_data(self.user_data)  # إضافة بيانات المستخدم لتتبع التغييرات

    def open_sales_window(self):
        """فتح نافذة المبيعات"""
        SalesWindow(self.window)

    def open_reports_window(self):
        """فتح نافذة التقارير"""
        ReportsWindow(self.window)

    def refresh_dashboard(self):
        """تحديث لوحة المعلومات"""
        self.create_dashboard()

    def open_purchases_window(self):
        """فتح نافذة المشتريات"""
        messagebox.showinfo("قريباً", "هذه الميزة قيد التطوير")

    def open_suppliers_window(self):
        """فتح نافذة الموردين"""
        messagebox.showinfo("قريباً", "هذه الميزة قيد التطوير")

    def open_employees_window(self):
        """فتح نافذة الموظفين"""
        messagebox.showinfo("قريباً", "هذه الميزة قيد التطوير")

    def open_settings(self):
        """فتح نافذة الإعدادات"""
        messagebox.showinfo("قريباً", "هذه الميزة قيد التطوير")

    def add_new_customer(self):
        self.open_customers_window()

    def add_new_medicine(self):
        self.open_medicines_window()

    def new_sale(self):
        self.open_sales_window()

    def sales_report(self):
        """فتح نافذة تقرير المبيعات"""
        reports_window = ReportsWindow(self.window)
        reports_window.notebook.select(0)  # تحديد تبويب تقارير المبيعات

    def inventory_report(self):
        """فتح نافذة تقرير المخزون"""
        reports_window = ReportsWindow(self.window)
        reports_window.notebook.select(1)  # تحديد تبويب تقارير المخزون

    def customers_report(self):
        """فتح نافذة تقرير العملاء"""
        # Since we don't have a customers report tab yet, open the main reports window
        ReportsWindow(self.window)

    def logout(self):
        if messagebox.askyesno("تأكيد", "هل تريد تسجيل الخروج؟"):
            self.window.destroy()