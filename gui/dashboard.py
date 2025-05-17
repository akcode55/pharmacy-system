import tkinter as tk
from tkinter import ttk, messagebox
from logic.inventory import InventoryManager
from logic.billing import BillingSystem
from logic.reports import ReportGenerator
from logic.suppliers import SupplierManager

class Dashboard:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.root.title("نظام إدارة الصيدلية - لوحة التحكم")
        self.root.geometry("1024x768")
        
        # Configure style for RTL
        self.style = ttk.Style()
        self.style.configure('RTL.TLabel', justify='right')
        self.style.configure('RTL.TEntry', justify='right')
        
        # Create main menu
        self.create_menu()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs based on user role
        self.create_inventory_tab()
        self.create_billing_tab()
        self.create_suppliers_tab()
        self.create_reports_tab()
        
        # Disable certain tabs based on user role
        if self.user['role'] != 'admin':
            self.notebook.tab(2, state='disabled')  # Disable suppliers tab for non-admin users
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="تسجيل خروج", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
    def create_inventory_tab(self):
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="المخزون")
        
        # Create inventory management interface
        inventory_manager = InventoryManager(inventory_frame)
        
    def create_billing_tab(self):
        billing_frame = ttk.Frame(self.notebook)
        self.notebook.add(billing_frame, text="المبيعات")
        
        # Create billing interface
        billing_system = BillingSystem(billing_frame)
        
    def create_reports_tab(self):
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="التقارير")
        
        # Create reports interface
        report_generator = ReportGenerator(reports_frame)
        
    def logout(self):
        self.root.destroy()
        # Show login window again
        from gui.login_window import LoginWindow
        root = tk.Tk()
        LoginWindow(root)
        root.mainloop()
