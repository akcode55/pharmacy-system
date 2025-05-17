"""
A clean starter script for the pharmacy system
This avoids importing any modules until necessary
"""

if __name__ == "__main__":
    import sys
    import os
    import tkinter as tk
    
    # Set up the database tables
    def create_sales_tables():
        import sqlite3
        from pathlib import Path
        
        db_path = Path('./database/pharmacy.db')
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create sales table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_date DATETIME NOT NULL,
                    subtotal REAL DEFAULT 0,
                    discount_percentage REAL DEFAULT 0,
                    discount_amount REAL DEFAULT 0,
                    vat_rate REAL DEFAULT 0.15,
                    vat_amount REAL DEFAULT 0,
                    total REAL DEFAULT 0,
                    status TEXT DEFAULT 'completed'
                )
            """)
            
            # Create sale_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL DEFAULT 0,
                    total_price REAL DEFAULT 0
                )
            """)
            
            conn.commit()
            print("Sales tables created successfully")
        except Exception as e:
            print(f"Error creating sales tables: {e}")
        finally:
            conn.close()
    
    # Create database tables
    create_sales_tables()
    
    # Create the main window
    root = tk.Tk()
    root.title("نظام إدارة الصيدلية")
    
    # Create login window
    from gui.login_window import LoginWindow
    app = LoginWindow(root)
    
    # Start the application
    root.mainloop() 