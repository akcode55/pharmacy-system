"""
Script to delete the database file directly
"""
import os
from pathlib import Path

# Database path
db_path = Path('database/pharmacy.db')

# Delete if exists
if db_path.exists():
    try:
        os.remove(db_path)
        print(f"Database file deleted: {db_path}")
    except Exception as e:
        print(f"Error deleting database: {e}")
else:
    print("Database file doesn't exist") 