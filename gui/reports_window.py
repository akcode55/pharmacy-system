import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import csv
import sqlite3
from database.db_connection import DatabaseConnection
from gui.sales_window import SalesWindow

class ReportsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("التقارير")
        self.window.geometry("800x600")

        # Create main frame
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for different reports
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs for different reports
        self.sales_report_tab = ttk.Frame(self.notebook)
        self.inventory_report_tab = ttk.Frame(self.notebook)
        self.expiry_report_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.sales_report_tab, text="تقارير المبيعات")
        self.notebook.add(self.inventory_report_tab, text="تقارير المخزون")
        self.notebook.add(self.expiry_report_tab, text="تقارير الصلاحية")

        # Setup sales report tab
        self.setup_sales_report_tab()

        # Setup inventory report tab
        self.setup_inventory_report_tab()

        # Setup expiry report tab
        self.setup_expiry_report_tab()

    def setup_sales_report_tab(self):
        # Create frame for report options
        options_frame = ttk.LabelFrame(self.sales_report_tab, text="خيارات التقرير")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add report type selection
        ttk.Label(options_frame, text="نوع التقرير:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.sales_report_type = tk.StringVar(value="daily")

        report_type_frame = ttk.Frame(options_frame)
        report_type_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Radiobutton(report_type_frame, text="يومي", variable=self.sales_report_type,
                       value="daily").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(report_type_frame, text="شهري", variable=self.sales_report_type,
                       value="monthly").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(report_type_frame, text="فترة محددة", variable=self.sales_report_type,
                       value="custom").pack(side=tk.RIGHT, padx=5)

        # Add date selection
        date_frame = ttk.Frame(options_frame)
        date_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        # Daily report date
        self.daily_frame = ttk.Frame(date_frame)
        ttk.Label(self.daily_frame, text="التاريخ:").pack(side=tk.RIGHT, padx=5)
        self.daily_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.daily_frame, textvariable=self.daily_date, width=12).pack(side=tk.RIGHT, padx=5)

        # Monthly report date
        self.monthly_frame = ttk.Frame(date_frame)
        ttk.Label(self.monthly_frame, text="الشهر:").pack(side=tk.RIGHT, padx=5)
        self.month_var = tk.IntVar(value=datetime.now().month)
        month_combo = ttk.Combobox(self.monthly_frame, textvariable=self.month_var, width=3)
        month_combo['values'] = list(range(1, 13))
        month_combo.pack(side=tk.RIGHT, padx=5)

        ttk.Label(self.monthly_frame, text="السنة:").pack(side=tk.RIGHT, padx=5)
        self.year_var = tk.IntVar(value=datetime.now().year)
        year_combo = ttk.Combobox(self.monthly_frame, textvariable=self.year_var, width=5)
        year_combo['values'] = list(range(datetime.now().year - 5, datetime.now().year + 1))
        year_combo.pack(side=tk.RIGHT, padx=5)

        # Custom date range
        self.custom_frame = ttk.Frame(date_frame)
        ttk.Label(self.custom_frame, text="من:").pack(side=tk.RIGHT, padx=5)
        self.from_date = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_frame, textvariable=self.from_date, width=12).pack(side=tk.RIGHT, padx=5)

        ttk.Label(self.custom_frame, text="إلى:").pack(side=tk.RIGHT, padx=5)
        self.to_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.custom_frame, textvariable=self.to_date, width=12).pack(side=tk.RIGHT, padx=5)

        # Show the appropriate date frame based on selection
        self.daily_frame.pack(fill=tk.X, pady=5)

        # Function to switch date frames
        def switch_date_frame():
            # Hide all frames
            self.daily_frame.pack_forget()
            self.monthly_frame.pack_forget()
            self.custom_frame.pack_forget()

            # Show selected frame
            if self.sales_report_type.get() == "daily":
                self.daily_frame.pack(fill=tk.X, pady=5)
            elif self.sales_report_type.get() == "monthly":
                self.monthly_frame.pack(fill=tk.X, pady=5)
            else:
                self.custom_frame.pack(fill=tk.X, pady=5)

        # Bind the switch function to report type changes
        self.sales_report_type.trace('w', lambda *args: switch_date_frame())

        # Buttons frame
        buttons_frame = ttk.Frame(options_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(buttons_frame, text="عرض التقرير",
                  command=self.display_sales_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="تصدير التقرير",
                  command=self.export_sales_report).pack(side=tk.RIGHT, padx=5)

        # Create frame for report display
        self.report_frame = ttk.LabelFrame(self.sales_report_tab, text="بيانات التقرير")
        self.report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for report data
        self.report_tree = ttk.Treeview(self.report_frame)
        self.report_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.report_frame, orient=tk.VERTICAL, command=self.report_tree.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.report_tree.configure(yscrollcommand=scrollbar.set)

        # Create frame for report summary
        self.summary_frame = ttk.LabelFrame(self.sales_report_tab, text="ملخص التقرير")
        self.summary_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add summary labels
        self.total_sales_var = tk.StringVar(value="0")
        self.total_items_var = tk.StringVar(value="0")
        self.avg_sale_var = tk.StringVar(value="0")

        summary_grid = ttk.Frame(self.summary_frame)
        summary_grid.pack(padx=10, pady=10)

        ttk.Label(summary_grid, text="إجمالي المبيعات:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(summary_grid, textvariable=self.total_sales_var, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(summary_grid, text="عدد الفواتير:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        ttk.Label(summary_grid, textvariable=self.total_items_var, font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(summary_grid, text="متوسط قيمة الفاتورة:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(summary_grid, textvariable=self.avg_sale_var, font=("Arial", 10, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    def setup_inventory_report_tab(self):
        # Create frame for report options
        options_frame = ttk.LabelFrame(self.inventory_report_tab, text="خيارات التقرير")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add report type selection
        ttk.Label(options_frame, text="نوع التقرير:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.inventory_report_type = tk.StringVar(value="all")

        report_type_frame = ttk.Frame(options_frame)
        report_type_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Radiobutton(report_type_frame, text="جميع الأدوية", variable=self.inventory_report_type,
                       value="all").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(report_type_frame, text="مخزون منخفض", variable=self.inventory_report_type,
                       value="low_stock").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(report_type_frame, text="نفدت من المخزون", variable=self.inventory_report_type,
                       value="out_of_stock").pack(side=tk.RIGHT, padx=5)

        # Buttons frame
        buttons_frame = ttk.Frame(options_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(buttons_frame, text="عرض التقرير",
                  command=self.display_inventory_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="تصدير التقرير",
                  command=self.export_inventory_report).pack(side=tk.RIGHT, padx=5)

        # Create frame for report display
        self.inventory_report_frame = ttk.LabelFrame(self.inventory_report_tab, text="بيانات التقرير")
        self.inventory_report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for report data
        self.inventory_tree = ttk.Treeview(self.inventory_report_frame)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_report_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        # Create frame for report summary
        self.inventory_summary_frame = ttk.LabelFrame(self.inventory_report_tab, text="ملخص التقرير")
        self.inventory_summary_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add summary labels
        self.total_items_count_var = tk.StringVar(value="0")
        self.total_value_var = tk.StringVar(value="0")
        self.low_stock_count_var = tk.StringVar(value="0")

        summary_grid = ttk.Frame(self.inventory_summary_frame)
        summary_grid.pack(padx=10, pady=10)

        ttk.Label(summary_grid, text="إجمالي عدد الأدوية:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(summary_grid, textvariable=self.total_items_count_var, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(summary_grid, text="إجمالي قيمة المخزون:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        ttk.Label(summary_grid, textvariable=self.total_value_var, font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(summary_grid, text="أدوية منخفضة المخزون:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        ttk.Label(summary_grid, textvariable=self.low_stock_count_var, font=("Arial", 10, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    def setup_expiry_report_tab(self):
        # Create frame for report options
        options_frame = ttk.LabelFrame(self.expiry_report_tab, text="خيارات التقرير")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add report type selection
        ttk.Label(options_frame, text="عرض الأدوية التي ستنتهي خلال:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.expiry_period = tk.StringVar(value="30")

        period_frame = ttk.Frame(options_frame)
        period_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Radiobutton(period_frame, text="30 يوم", variable=self.expiry_period,
                       value="30").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(period_frame, text="60 يوم", variable=self.expiry_period,
                       value="60").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(period_frame, text="90 يوم", variable=self.expiry_period,
                       value="90").pack(side=tk.RIGHT, padx=5)
        ttk.Radiobutton(period_frame, text="مخصص", variable=self.expiry_period,
                       value="custom").pack(side=tk.RIGHT, padx=5)

        # Custom days entry
        self.custom_expiry_frame = ttk.Frame(options_frame)
        self.custom_expiry_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        ttk.Label(self.custom_expiry_frame, text="عدد الأيام:").pack(side=tk.RIGHT, padx=5)
        self.custom_days = tk.StringVar(value="30")
        ttk.Entry(self.custom_expiry_frame, textvariable=self.custom_days, width=5).pack(side=tk.RIGHT, padx=5)

        # Function to show/hide custom days entry
        def toggle_custom_days(*args):
            if self.expiry_period.get() == "custom":
                self.custom_expiry_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
            else:
                self.custom_expiry_frame.grid_forget()

        # Bind the toggle function to expiry period changes
        self.expiry_period.trace('w', toggle_custom_days)

        # Hide custom days entry initially if not selected
        if self.expiry_period.get() != "custom":
            self.custom_expiry_frame.grid_forget()

        # Buttons frame
        buttons_frame = ttk.Frame(options_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        ttk.Button(buttons_frame, text="عرض التقرير",
                  command=self.display_expiry_report).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="تصدير التقرير",
                  command=self.export_expiry_report).pack(side=tk.RIGHT, padx=5)

        # Create frame for report display
        self.expiry_report_frame = ttk.LabelFrame(self.expiry_report_tab, text="بيانات التقرير")
        self.expiry_report_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for report data
        self.expiry_tree = ttk.Treeview(self.expiry_report_frame)
        self.expiry_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.expiry_report_frame, orient=tk.VERTICAL, command=self.expiry_tree.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.expiry_tree.configure(yscrollcommand=scrollbar.set)

    def display_sales_report(self):
        """Display sales report based on selected options"""
        # Clear previous data
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        report_type = self.sales_report_type.get()

        # Get date range based on report type
        start_date = None
        end_date = None

        if report_type == "daily":
            date_str = self.daily_date.get()
            start_date = date_str
            end_date = date_str

        elif report_type == "monthly":
            month = self.month_var.get()
            year = self.year_var.get()

            # Validate date
            if month < 1 or month > 12 or year < 2000:
                messagebox.showwarning("تحذير", "الرجاء إدخال شهر وسنة صحيحين")
                return

            # Get first and last day of month
            start_date = f"{year}-{month:02d}-01"

            # Get last day of month
            if month == 12:
                next_month_year = year + 1
                next_month = 1
            else:
                next_month_year = year
                next_month = month + 1

            # Last day is the day before the first day of next month
            last_day = (datetime.strptime(f"{next_month_year}-{next_month:02d}-01", "%Y-%m-%d") - timedelta(days=1)).day
            end_date = f"{year}-{month:02d}-{last_day:02d}"

        elif report_type == "custom":
            start_date = self.from_date.get()
            end_date = self.to_date.get()

        # Configure treeview based on report type
        self.report_tree["columns"] = []
        for col in self.report_tree["columns"]:
            self.report_tree.heading(col, text="")

        if report_type == "daily":
            # Daily report shows individual sales
            self.report_tree["columns"] = ("id", "time", "items", "subtotal", "discount", "vat", "total")
            self.report_tree.heading("id", text="رقم الفاتورة")
            self.report_tree.heading("time", text="الوقت")
            self.report_tree.heading("items", text="عدد الأصناف")
            self.report_tree.heading("subtotal", text="المجموع الفرعي")
            self.report_tree.heading("discount", text="الخصم")
            self.report_tree.heading("vat", text="الضريبة")
            self.report_tree.heading("total", text="الإجمالي")

            self.report_tree.column("id", width=80)
            self.report_tree.column("time", width=150)
            self.report_tree.column("items", width=100)
            self.report_tree.column("subtotal", width=120)
            self.report_tree.column("discount", width=120)
            self.report_tree.column("vat", width=120)
            self.report_tree.column("total", width=120)

        elif report_type in ["monthly", "custom"]:
            # Monthly or custom report shows daily totals
            self.report_tree["columns"] = ("date", "sales_count", "total_amount")
            self.report_tree.heading("date", text="التاريخ")
            self.report_tree.heading("sales_count", text="عدد الفواتير")
            self.report_tree.heading("total_amount", text="إجمالي المبيعات")

            self.report_tree.column("date", width=150)
            self.report_tree.column("sales_count", width=150)
            self.report_tree.column("total_amount", width=150)

        # Get data from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            if report_type == "daily":
                # Get daily sales
                cursor.execute("""
                    SELECT s.id, s.sale_date, s.subtotal, s.discount_amount,
                           s.vat_amount, s.total, COUNT(si.id) as item_count
                    FROM sales s
                    LEFT JOIN sale_items si ON s.id = si.sale_id
                    WHERE date(s.sale_date) = ?
                    GROUP BY s.id
                    ORDER BY s.sale_date DESC
                """, (start_date,))

                sales = cursor.fetchall()

                # Add sales to treeview
                total_sales = 0
                total_items = 0
                for sale in sales:
                    sale_id, sale_date, subtotal, discount, vat, total, item_count = sale

                    # Convert full datetime to just time
                    try:
                        time_part = datetime.strptime(sale_date, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                    except:
                        time_part = sale_date

                    self.report_tree.insert("", tk.END, values=(
                        sale_id,
                        time_part,
                        item_count,
                        f"{subtotal:.2f}",
                        f"{discount:.2f}",
                        f"{vat:.2f}",
                        f"{total:.2f}"
                    ))
                    total_sales += total
                    total_items += 1

                # Update summary
                from utils.helpers import format_currency_with_name
                self.total_sales_var.set(format_currency_with_name(total_sales))
                self.total_items_var.set(str(total_items))

                # Calculate average sale value
                avg_sale = total_sales / total_items if total_items > 0 else 0
                self.avg_sale_var.set(format_currency_with_name(avg_sale))

            elif report_type in ["monthly", "custom"]:
                # Get daily totals
                cursor.execute("""
                    SELECT date(s.sale_date) as day, COUNT(s.id) as sales_count, SUM(s.total) as total_amount
                    FROM sales s
                    WHERE date(s.sale_date) BETWEEN ? AND ?
                    GROUP BY day
                    ORDER BY day
                """, (start_date, end_date))

                daily_totals = cursor.fetchall()

                # Add daily totals to treeview
                total_sales = 0
                total_items = 0
                for daily in daily_totals:
                    day, sales_count, daily_total = daily
                    self.report_tree.insert("", tk.END, values=(
                        day,
                        sales_count,
                        format_currency_with_name(daily_total)
                    ))
                    total_sales += daily_total
                    total_items += sales_count

                # Update summary
                from utils.helpers import format_currency_with_name
                self.total_sales_var.set(format_currency_with_name(total_sales))
                self.total_items_var.set(str(total_items))

                # Calculate average sale value
                avg_sale = total_sales / total_items if total_items > 0 else 0
                self.avg_sale_var.set(format_currency_with_name(avg_sale))

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات المبيعات: {str(e)}")
        finally:
            db.close()

    def export_sales_report(self):
        """Export sales report to CSV file"""
        report_type = self.sales_report_type.get()

        # Get date range based on report type
        start_date = None
        end_date = None
        filename_date = ""

        if report_type == "daily":
            date_str = self.daily_date.get()
            start_date = date_str
            end_date = date_str
            filename_date = date_str

        elif report_type == "monthly":
            month = self.month_var.get()
            year = self.year_var.get()

            # Validate date
            if month < 1 or month > 12 or year < 2000:
                messagebox.showwarning("تحذير", "الرجاء إدخال شهر وسنة صحيحين")
                return

            # Get first and last day of month
            start_date = f"{year}-{month:02d}-01"

            # Get last day of month
            if month == 12:
                next_month_year = year + 1
                next_month = 1
            else:
                next_month_year = year
                next_month = month + 1

            # Last day is the day before the first day of next month
            last_day = (datetime.strptime(f"{next_month_year}-{next_month:02d}-01", "%Y-%m-%d") - timedelta(days=1)).day
            end_date = f"{year}-{month:02d}-{last_day:02d}"
            filename_date = f"{year}_{month:02d}"

        elif report_type == "custom":
            start_date = self.from_date.get()
            end_date = self.to_date.get()
            filename_date = f"{start_date}_to_{end_date}"

        # Generate filename
        if report_type == "daily":
            filename = f"sales_report_daily_{filename_date}.csv"
        elif report_type == "monthly":
            filename = f"sales_report_monthly_{filename_date}.csv"
        else:
            filename = f"sales_report_custom_{filename_date}.csv"

        # Ask user where to save file
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=filename
        )

        if not filepath:
            return

        # Get data from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                if report_type == "daily":
                    # Write headers
                    writer.writerow(['رقم الفاتورة', 'التاريخ', 'عدد الأصناف', 'المجموع الفرعي',
                                    'الخصم', 'الضريبة', 'الإجمالي'])

                    # Get daily sales
                    cursor.execute("""
                        SELECT s.id, s.sale_date, s.subtotal, s.discount_amount,
                               s.vat_amount, s.total, COUNT(si.id) as item_count
                        FROM sales s
                        LEFT JOIN sale_items si ON s.id = si.sale_id
                        WHERE date(s.sale_date) = ?
                        GROUP BY s.id
                        ORDER BY s.sale_date DESC
                    """, (start_date,))

                    sales = cursor.fetchall()

                    # Write data
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

                    # Write summary
                    writer.writerow([])
                    writer.writerow(['الإجمالي', '', '', '', '', '', f"{total_sales:.2f}"])

                elif report_type in ["monthly", "custom"]:
                    # Write headers
                    writer.writerow(['التاريخ', 'عدد الفواتير', 'إجمالي المبيعات'])

                    # Get daily totals
                    cursor.execute("""
                        SELECT date(s.sale_date) as day, COUNT(s.id) as sales_count, SUM(s.total) as total_amount
                        FROM sales s
                        WHERE date(s.sale_date) BETWEEN ? AND ?
                        GROUP BY day
                        ORDER BY day
                    """, (start_date, end_date))

                    daily_totals = cursor.fetchall()

                    # Write data
                    total_sales = 0
                    total_count = 0
                    for daily in daily_totals:
                        day, sales_count, daily_total = daily
                        writer.writerow([
                            day,
                            sales_count,
                            f"{daily_total:.2f}"
                        ])
                        total_sales += daily_total
                        total_count += sales_count

                    # Write summary
                    writer.writerow([])
                    writer.writerow(['الإجمالي', total_count, f"{total_sales:.2f}"])

            messagebox.showinfo("تصدير التقرير", f"تم تصدير التقرير بنجاح إلى:\n{filepath}")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير التقرير: {str(e)}")
        finally:
            db.close()

    def display_inventory_report(self):
        """Display inventory report based on selected options"""
        # Clear previous data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        report_type = self.inventory_report_type.get()

        # Configure treeview columns
        self.inventory_tree["columns"] = ("id", "name", "quantity", "price", "value", "min_level", "status")
        self.inventory_tree.heading("id", text="الرقم")
        self.inventory_tree.heading("name", text="اسم الدواء")
        self.inventory_tree.heading("quantity", text="الكمية")
        self.inventory_tree.heading("price", text="السعر")
        self.inventory_tree.heading("value", text="القيمة")
        self.inventory_tree.heading("min_level", text="الحد الأدنى")
        self.inventory_tree.heading("status", text="الحالة")

        self.inventory_tree.column("id", width=50)
        self.inventory_tree.column("name", width=200)
        self.inventory_tree.column("quantity", width=80)
        self.inventory_tree.column("price", width=80)
        self.inventory_tree.column("value", width=100)
        self.inventory_tree.column("min_level", width=80)
        self.inventory_tree.column("status", width=100)

        # Get data from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # Build query based on report type
            query = """
                SELECT id, name, quantity, price, min_stock_level
                FROM medicines
                WHERE 1=1
            """

            if report_type == "low_stock":
                query += " AND quantity <= min_stock_level AND quantity > 0"
            elif report_type == "out_of_stock":
                query += " AND quantity = 0"

            query += " ORDER BY name"

            cursor.execute(query)
            medicines = cursor.fetchall()

            # Add medicines to treeview
            total_items = 0
            total_value = 0
            low_stock_count = 0

            for med in medicines:
                med_id, name, quantity, price, min_level = med

                # Calculate value
                value = quantity * price

                # Determine status
                if quantity == 0:
                    status = "نفذت"
                    status_color = "red"
                elif quantity <= min_level:
                    status = "منخفض"
                    status_color = "orange"
                else:
                    status = "جيد"
                    status_color = "green"

                # Insert into treeview
                item_id = self.inventory_tree.insert("", tk.END, values=(
                    med_id,
                    name,
                    quantity,
                    f"{price:.2f}",
                    f"{value:.2f}",
                    min_level,
                    status
                ))

                # Set item color based on status
                self.inventory_tree.item(item_id, tags=(status,))

                # Update totals
                total_items += 1
                total_value += value
                if quantity <= min_level and quantity > 0:
                    low_stock_count += 1

            # Configure tag colors
            self.inventory_tree.tag_configure("نفذت", foreground="red")
            self.inventory_tree.tag_configure("منخفض", foreground="orange")
            self.inventory_tree.tag_configure("جيد", foreground="green")

            # Update summary
            from utils.helpers import format_currency_with_name
            self.total_items_count_var.set(str(total_items))
            self.total_value_var.set(format_currency_with_name(total_value))
            self.low_stock_count_var.set(str(low_stock_count))

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات المخزون: {str(e)}")
        finally:
            db.close()

    def export_inventory_report(self):
        """Export inventory report to CSV file"""
        report_type = self.inventory_report_type.get()

        # Generate filename
        if report_type == "all":
            filename = "inventory_report_all.csv"
        elif report_type == "low_stock":
            filename = "inventory_report_low_stock.csv"
        else:
            filename = "inventory_report_out_of_stock.csv"

        # Ask user where to save file
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=filename
        )

        if not filepath:
            return

        # Get data from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # Write headers
                writer.writerow(['الرقم', 'اسم الدواء', 'الكمية', 'السعر', 'القيمة', 'الحد الأدنى', 'الحالة'])

                # Build query based on report type
                query = """
                    SELECT id, name, quantity, price, min_stock_level
                    FROM medicines
                    WHERE 1=1
                """

                if report_type == "low_stock":
                    query += " AND quantity <= min_stock_level AND quantity > 0"
                elif report_type == "out_of_stock":
                    query += " AND quantity = 0"

                query += " ORDER BY name"

                cursor.execute(query)
                medicines = cursor.fetchall()

                # Write data
                total_value = 0
                for med in medicines:
                    med_id, name, quantity, price, min_level = med

                    # Calculate value
                    value = quantity * price

                    # Determine status
                    if quantity == 0:
                        status = "نفذت"
                    elif quantity <= min_level:
                        status = "منخفض"
                    else:
                        status = "جيد"

                    # Write row
                    writer.writerow([
                        med_id,
                        name,
                        quantity,
                        f"{price:.2f}",
                        f"{value:.2f}",
                        min_level,
                        status
                    ])

                    total_value += value

                # Write summary
                writer.writerow([])
                writer.writerow(['الإجمالي', '', '', '', f"{total_value:.2f}", '', ''])

            messagebox.showinfo("تصدير التقرير", f"تم تصدير تقرير المخزون بنجاح إلى:\n{filepath}")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير التقرير: {str(e)}")
        finally:
            db.close()

    def display_expiry_report(self):
        """Display expiry report based on selected options"""
        # Clear previous data
        for item in self.expiry_tree.get_children():
            self.expiry_tree.delete(item)

        # Get days period
        if self.expiry_period.get() == "custom":
            try:
                days = int(self.custom_days.get())
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال عدد أيام صحيح")
                return
        else:
            days = int(self.expiry_period.get())

        # Calculate expiry date threshold
        today = datetime.now().date()
        threshold_date = today + timedelta(days=days)

        # Configure treeview columns
        self.expiry_tree["columns"] = ("id", "name", "expiry_date", "days_remaining", "quantity", "price", "value")
        self.expiry_tree.heading("id", text="الرقم")
        self.expiry_tree.heading("name", text="اسم الدواء")
        self.expiry_tree.heading("expiry_date", text="تاريخ انتهاء الصلاحية")
        self.expiry_tree.heading("days_remaining", text="الأيام المتبقية")
        self.expiry_tree.heading("quantity", text="الكمية")
        self.expiry_tree.heading("price", text="السعر")
        self.expiry_tree.heading("value", text="القيمة")

        self.expiry_tree.column("id", width=50)
        self.expiry_tree.column("name", width=180)
        self.expiry_tree.column("expiry_date", width=120)
        self.expiry_tree.column("days_remaining", width=100)
        self.expiry_tree.column("quantity", width=80)
        self.expiry_tree.column("price", width=80)
        self.expiry_tree.column("value", width=100)

        # Get data from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            # Get medicines that will expire within the period
            cursor.execute("""
                SELECT id, name, expiry_date, quantity, price
                FROM medicines
                WHERE quantity > 0 AND date(expiry_date) <= date(?)
                ORDER BY expiry_date
            """, (threshold_date.isoformat(),))

            medicines = cursor.fetchall()

            # Add medicines to treeview
            total_items = 0
            total_value = 0
            expired_count = 0

            for med in medicines:
                med_id, name, expiry_date_str, quantity, price = med

                try:
                    # Parse expiry date
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

                    # Calculate days remaining
                    days_remaining = (expiry_date - today).days

                    # Calculate value
                    value = quantity * price

                    # Insert into treeview with appropriate tag
                    if days_remaining < 0:
                        tag = "expired"
                        status_text = f"منتهي ({abs(days_remaining)} يوم)"
                        expired_count += 1
                    else:
                        tag = "expiring"
                        status_text = f"{days_remaining} يوم"

                    item_id = self.expiry_tree.insert("", tk.END, values=(
                        med_id,
                        name,
                        expiry_date_str,
                        status_text,
                        quantity,
                        f"{price:.2f}",
                        f"{value:.2f}"
                    ))

                    # Set item color based on status
                    self.expiry_tree.item(item_id, tags=(tag,))

                    # Update totals
                    total_items += 1
                    total_value += value

                except Exception as e:
                    print(f"Error processing medicine {med_id}: {e}")

            # Configure tag colors
            self.expiry_tree.tag_configure("expired", foreground="red")
            self.expiry_tree.tag_configure("expiring", foreground="orange")

            # If no items found
            if total_items == 0:
                messagebox.showinfo("معلومات", f"لا توجد أدوية ستنتهي صلاحيتها خلال {days} يوم")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تحميل بيانات الصلاحية: {str(e)}")
        finally:
            db.close()

    def export_expiry_report(self):
        """Export expiry report to CSV file"""
        # Get days period
        if self.expiry_period.get() == "custom":
            try:
                days = int(self.custom_days.get())
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال عدد أيام صحيح")
                return
        else:
            days = int(self.expiry_period.get())

        # Calculate expiry date threshold
        today = datetime.now().date()
        threshold_date = today + timedelta(days=days)

        # Generate filename
        filename = f"expiry_report_{days}_days.csv"

        # Ask user where to save file
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=filename
        )

        if not filepath:
            return

        # Get data from database
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # Write headers
                writer.writerow(['الرقم', 'اسم الدواء', 'تاريخ انتهاء الصلاحية', 'الأيام المتبقية',
                                'الكمية', 'السعر', 'القيمة'])

                # Get medicines that will expire within the period
                cursor.execute("""
                    SELECT id, name, expiry_date, quantity, price
                    FROM medicines
                    WHERE quantity > 0 AND date(expiry_date) <= date(?)
                    ORDER BY expiry_date
                """, (threshold_date.isoformat(),))

                medicines = cursor.fetchall()

                # Write data
                total_value = 0
                expired_count = 0

                for med in medicines:
                    med_id, name, expiry_date_str, quantity, price = med

                    try:
                        # Parse expiry date
                        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

                        # Calculate days remaining
                        days_remaining = (expiry_date - today).days

                        # Calculate value
                        value = quantity * price

                        # Status text
                        if days_remaining < 0:
                            status_text = f"منتهي ({abs(days_remaining)} يوم)"
                            expired_count += 1
                        else:
                            status_text = f"{days_remaining} يوم"

                        # Write row
                        writer.writerow([
                            med_id,
                            name,
                            expiry_date_str,
                            status_text,
                            quantity,
                            f"{price:.2f}",
                            f"{value:.2f}"
                        ])

                        total_value += value

                    except Exception as e:
                        print(f"Error processing medicine {med_id}: {e}")

                # Write summary
                writer.writerow([])
                writer.writerow(['الإجمالي', '', '', '', '', '', f"{total_value:.2f}"])
                writer.writerow(['أدوية منتهية الصلاحية', expired_count, '', '', '', '', ''])

            messagebox.showinfo("تصدير التقرير", f"تم تصدير تقرير الصلاحية بنجاح إلى:\n{filepath}")

        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير التقرير: {str(e)}")
        finally:
            db.close()