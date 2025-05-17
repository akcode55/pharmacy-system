"""
Script to create admin user directly in the database
"""
import os
import sys
import sqlite3
import hashlib
from pathlib import Path

def create_admin_user():
    # Path to the database
    db_path = Path('database/pharmacy.db')
    
    # Create directory if it doesn't exist
    os.makedirs(db_path.parent, exist_ok=True)
    
    print(f"Database path: {db_path.absolute()}")
    
    # Hash the password
    password = 'admin123'
    salt = os.environ.get('PHARMACY_SALT', 'default_salt_value')
    salted = password + salt
    hashed_password = hashlib.sha256(salted.encode()).hexdigest()
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        user = cursor.fetchone()
        
        if user:
            # Update admin user
            cursor.execute('''
                UPDATE users 
                SET password = ?, role = 'admin', is_active = 1
                WHERE username = 'admin'
            ''', (hashed_password,))
            print("Admin user updated")
        else:
            # Create admin user
            cursor.execute('''
                INSERT INTO users (username, password, role, is_active)
                VALUES (?, ?, 'admin', 1)
            ''', ('admin', hashed_password))
            print("Admin user created")
        
        # Commit changes
        conn.commit()
        
        # Verify admin user
        cursor.execute("SELECT id, username, role, is_active FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin:
            print(f"Admin verification: ID={admin[0]}, Username={admin[1]}, Role={admin[2]}, Active={admin[3]}")
        else:
            print("Failed to verify admin user")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_admin_user() 