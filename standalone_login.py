"""
Standalone login script for testing login functionality
"""
import tkinter as tk
import sys
import os
import sqlite3
import hashlib
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create a simple login window
root = tk.Tk()
root.title("Test Login")
root.geometry("300x200")

# Create input fields
tk.Label(root, text="Username:").pack(pady=5)
username_var = tk.StringVar()
username_entry = tk.Entry(root, textvariable=username_var)
username_entry.pack(pady=5)

tk.Label(root, text="Password:").pack(pady=5)
password_var = tk.StringVar()
password_entry = tk.Entry(root, textvariable=password_var, show="*")
password_entry.pack(pady=5)

# Status message
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, fg="red")
status_label.pack(pady=10)

# Login function
def login():
    username = username_var.get().strip()
    password = password_var.get().strip()
    
    if not username or not password:
        status_var.set("Please enter username and password")
        return
    
    # Hash the password
    salt = os.environ.get('PHARMACY_SALT', 'default_salt_value')
    salted = password + salt
    hashed_password = hashlib.sha256(salted.encode()).hexdigest()
    
    # Find database file
    db_path = Path('database/pharmacy.db')
    
    if not db_path.exists():
        status_var.set(f"Database not found at {db_path}")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Execute query
        cursor.execute("""
            SELECT id, username, role 
            FROM users 
            WHERE username = ? AND password = ? AND is_active = 1
        """, (username, hashed_password))
        
        user = cursor.fetchone()
        
        if user:
            status_var.set(f"Login successful! Role: {user[2]}")
        else:
            # Try with plain password for debugging
            cursor.execute("""
                SELECT id, username, role, password
                FROM users 
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            if user:
                status_var.set(f"Password mismatch. Stored: {user[3][:10]}...")
            else:
                status_var.set("User not found or not active")
        
    except Exception as e:
        status_var.set(f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

# Add login button
login_button = tk.Button(root, text="Login", command=login)
login_button.pack(pady=10)

# Add credentials hint
hint_label = tk.Label(root, text="Try: admin / admin123", fg="blue")
hint_label.pack(pady=5)

# Start application
if __name__ == "__main__":
    root.mainloop() 