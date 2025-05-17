import sys
import os

print("Starting main.py")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import ttk

print("Importing login_window")
from gui.login_window import LoginWindow
print("Importing create_tables")
from database.models import create_tables
print("Importing update_schema")
from database.update_schema import update_database_schema
print("Importing DatabaseConnection")
from database.db_connection import DatabaseConnection
from datetime import datetime
from gui.custom_theme import BACKGROUND_COLOR

def initialize_database():
    # Create database tables if they don't exist
    create_tables()

    # Make sure the sales table has the proper structure
    try:
        db = DatabaseConnection()
        conn = db.connect()
        cursor = conn.cursor()

        # Check if sales table exists with proper structure
        try:
            cursor.execute("PRAGMA table_info(sales)")
            columns = [column[1] for column in cursor.fetchall()]

            required_columns = ['subtotal', 'discount_percentage', 'discount_amount',
                              'vat_rate', 'vat_amount']
            missing_columns = [col for col in required_columns if col not in columns]

            if missing_columns:
                print(f"Sales table is missing columns: {missing_columns}")
                # Recreate the sales table with proper structure
                cursor.execute("DROP TABLE IF EXISTS sales")
                cursor.execute("""
                    CREATE TABLE sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sale_date DATETIME NOT NULL,
                        subtotal REAL NOT NULL DEFAULT 0,
                        discount_percentage REAL DEFAULT 0,
                        discount_amount REAL DEFAULT 0,
                        vat_rate REAL DEFAULT 0.15,
                        vat_amount REAL DEFAULT 0,
                        total REAL NOT NULL DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'completed'
                    )
                """)
                print("Sales table recreated with proper structure")

                # Also check and recreate sale_items table
                cursor.execute("DROP TABLE IF EXISTS sale_items")
                cursor.execute("""
                    CREATE TABLE sale_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sale_id INTEGER NOT NULL,
                        medicine_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        unit_price REAL NOT NULL,
                        total_price REAL NOT NULL,
                        FOREIGN KEY (sale_id) REFERENCES sales (id),
                        FOREIGN KEY (medicine_id) REFERENCES medicines (id)
                    )
                """)
                print("Sale_items table recreated with proper structure")

                conn.commit()
        except Exception as e:
            print(f"Error checking sales table: {e}")

    except Exception as e:
        print(f"Error during database initialization: {e}")
    finally:
        db.close()

    # Update database schema if needed
    update_result, update_message = update_database_schema()
    if not update_result:
        print(f"تحذير: {update_message}")

    # Create default admin user if it doesn't exist
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()

    from utils.encryption import hash_password

    try:
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            hashed_password = hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', ('admin', hashed_password, 'admin'))
            conn.commit()
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

def main():
    # Initialize database and create admin user
    initialize_database()

    # Create main window
    root = tk.Tk()
    root.title("نظام إدارة الصيدلية")

    # Set RTL (Right-to-Left) orientation for Arabic
    root.tk.call('tk', 'scaling', 1.0)

    # Set window background color
    root.configure(bg=BACKGROUND_COLOR)

    # Create login window
    app = LoginWindow(root)

    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
