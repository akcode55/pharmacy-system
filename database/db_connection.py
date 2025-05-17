import sqlite3
import os
from pathlib import Path

class DatabaseConnection:
    """
    A class to handle database connections and operations.
    """
    def __init__(self, db_name='pharmacy.db'):
        # Use Path for cross-platform compatibility
        self.db_path = Path(os.path.dirname(os.path.abspath(__file__))) / db_name
        self.connection = None
    
    def connect(self):
        """Connect to the database and return the connection object."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(str(self.db_path))
            print(f"Successfully connected to database: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close the database connection if it exists."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, parameters=None):
        try:
            cursor = self.connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None
