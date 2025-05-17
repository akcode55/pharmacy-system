import tkinter as tk
from tkinter import ttk, messagebox
from database.db_connection import DatabaseConnection
from utils.encryption import hash_password
from gui.main_window import MainWindow
from gui.custom_theme import create_colored_frame, create_colored_label, create_colored_button, PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, TEXT_COLOR, TEXT_COLOR_LIGHT

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة الصيدلية - تسجيل الدخول")
        self.root.geometry("500x400")

        # Set window background color
        self.root.configure(bg=BACKGROUND_COLOR)

        # Create main container
        main_container = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Create left panel (green sidebar)
        left_panel = create_colored_frame(main_container, bg_color=PRIMARY_COLOR, width=200)
        left_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Add logo or system name
        create_colored_label(left_panel, text="نظام إدارة\nالصيدلية",
                           bg_color=PRIMARY_COLOR, fg_color=TEXT_COLOR_LIGHT,
                           font=('Arial', 16, 'bold'),
                           justify='center').pack(pady=(50, 20))

        # Add icon (placeholder)
        icon_frame = create_colored_frame(left_panel, bg_color=PRIMARY_COLOR)
        icon_frame.pack(pady=10)
        create_colored_label(icon_frame, text="🏛️",
                           bg_color=PRIMARY_COLOR, fg_color=TEXT_COLOR_LIGHT,
                           font=('Arial', 36)).pack()

        # Create right panel (login form)
        right_panel = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Welcome message
        create_colored_label(right_panel, text="مرحباً بك",
                           bg_color=BACKGROUND_COLOR, fg_color=TEXT_COLOR,
                           font=('Arial', 16, 'bold')).pack(anchor='e', pady=(40, 5))
        create_colored_label(right_panel, text="قم بتسجيل الدخول إلى حسابك",
                           bg_color=BACKGROUND_COLOR, fg_color=TEXT_COLOR,
                           font=('Arial', 10)).pack(anchor='e', pady=(0, 30))

        # Username
        create_colored_label(right_panel, text="اسم المستخدم",
                           bg_color=BACKGROUND_COLOR, fg_color=TEXT_COLOR,
                           justify='right').pack(anchor='e')
        self.username_entry = tk.Entry(right_panel, justify='right')
        self.username_entry.pack(fill=tk.X, pady=(0, 15))

        # Password
        create_colored_label(right_panel, text="كلمة المرور",
                           bg_color=BACKGROUND_COLOR, fg_color=TEXT_COLOR,
                           justify='right').pack(anchor='e')
        self.password_entry = tk.Entry(right_panel, show="*", justify='right')
        self.password_entry.pack(fill=tk.X, pady=(0, 25))

        # Login button
        login_button = create_colored_button(right_panel, text="تسجيل الدخول",
                                          command=self.login,
                                          bg_color=PRIMARY_COLOR,
                                          fg_color=TEXT_COLOR_LIGHT,
                                          hover_color=SECONDARY_COLOR)
        login_button.pack(fill=tk.X, ipady=5)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("خطأ", "الرجاء إدخال اسم المستخدم وكلمة المرور")
            return

        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        try:
            hashed_password = hash_password(password)
            cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?",
                         (username, hashed_password))
            user = cursor.fetchone()

            if user:
                user_data = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2]
                }
                self.root.withdraw()  # Hide login window
                main_window = tk.Toplevel()
                MainWindow(main_window, user_data)
            else:
                messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء تسجيل الدخول: {str(e)}")
        finally:
            db.close()
