from database.db_connection import DatabaseConnection
from datetime import datetime

class InventoryManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.db = DatabaseConnection()
        
    def add_medicine(self, name, description, price, quantity, expiry_date, manufacturer, barcode=None, category=None, min_stock_level=10):
        """Add a new medicine to the inventory with extended details."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO medicines (
                    name, description, price, quantity, expiry_date, manufacturer,
                    barcode, category, min_stock_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, price, quantity, expiry_date, manufacturer,
                 barcode, category, min_stock_level))
            conn.commit()
            return True, cursor.lastrowid
        except Exception as e:
            print(f"Error adding medicine: {e}")
            return False
        finally:
            self.db.close()
            
    def update_stock(self, medicine_id, new_quantity):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE medicines
                SET quantity = ?
                WHERE id = ?
            ''', (new_quantity, medicine_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
        finally:
            self.db.close()
            
    def get_low_stock_items(self, threshold=10):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM medicines
                WHERE quantity <= ?
            ''', (threshold,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting low stock items: {e}")
            return []
        finally:
            self.db.close()
            
    def get_expiring_items(self, days=30):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM medicines
                WHERE date(expiry_date) <= date('now', '+' || ? || ' days')
            ''', (days,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting expiring items: {e}")
            return []
        finally:
            self.db.close()
            
    def search_medicine(self, keyword):
        """Search for medicines by name, barcode, or category."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM medicines
                WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ?
                AND is_active = 1
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error searching medicines: {e}")
            return []
        finally:
            self.db.close()
            
    def update_medicine(self, medicine_id, update_data):
        """Update medicine details."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        valid_fields = [
            'name', 'description', 'price', 'quantity', 'expiry_date',
            'manufacturer', 'barcode', 'category', 'min_stock_level',
            'location', 'is_active'
        ]
        
        try:
            # Build update query dynamically based on provided fields
            update_fields = []
            update_values = []
            
            for field in valid_fields:
                if field in update_data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(update_data[field])
            
            if not update_fields:
                return False, "لم يتم تحديد أي حقول للتحديث"
                
            update_values.append(medicine_id)  # For WHERE clause
            
            query = f'''
                UPDATE medicines
                SET {', '.join(update_fields)}
                WHERE id = ?
            '''
            
            cursor.execute(query, update_values)
            conn.commit()
            
            return True, "تم تحديث بيانات الدواء بنجاح"
        except Exception as e:
            print(f"Error updating medicine: {e}")
            return False, str(e)
        finally:
            self.db.close()
            
    def delete_medicine(self, medicine_id):
        """Soft delete a medicine by setting is_active to 0."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE medicines
                SET is_active = 0
                WHERE id = ?
            ''', (medicine_id,))
            conn.commit()
            return True, "تم حذف الدواء بنجاح"
        except Exception as e:
            print(f"Error deleting medicine: {e}")
            return False, str(e)
        finally:
            self.db.close()
            
    def get_medicine_details(self, medicine_id):
        """Get detailed information about a specific medicine."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM medicines WHERE id = ?', (medicine_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error getting medicine details: {e}")
            return None
        finally:
            self.db.close()
            
    def check_expiry_alerts(self, days_threshold=90):
        """Get medicines that will expire within the specified number of days."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT *
                FROM medicines
                WHERE date(expiry_date) <= date('now', '+' || ? || ' days')
                AND date(expiry_date) >= date('now')
                AND is_active = 1
                ORDER BY expiry_date
            ''', (days_threshold,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error checking expiry alerts: {e}")
            return []
        finally:
            self.db.close()
            
    def check_stock_alerts(self):
        """Get medicines that are below their minimum stock level."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT *
                FROM medicines
                WHERE quantity <= min_stock_level
                AND is_active = 1
                ORDER BY quantity ASC
            ''')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error checking stock alerts: {e}")
            return []
        finally:
            self.db.close()
