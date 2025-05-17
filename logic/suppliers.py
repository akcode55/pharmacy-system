from database.db_connection import DatabaseConnection
from datetime import datetime

class SupplierManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.db = DatabaseConnection()
        
    def add_supplier(self, name, contact, address, email):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO suppliers (name, contact, address, email)
                VALUES (?, ?, ?, ?)
            ''', (name, contact, address, email))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding supplier: {e}")
            return False
        finally:
            self.db.close()
            
    def update_supplier(self, supplier_id, name, contact, address, email):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE suppliers
                SET name = ?, contact = ?, address = ?, email = ?
                WHERE id = ?
            ''', (name, contact, address, email, supplier_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return False
        finally:
            self.db.close()
            
    def delete_supplier(self, supplier_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            # Check if supplier has any purchase orders
            cursor.execute('SELECT COUNT(*) FROM purchase_orders WHERE supplier_id = ?', (supplier_id,))
            if cursor.fetchone()[0] > 0:
                return False, "لا يمكن حذف المورد لوجود طلبات شراء مرتبطة به"
            
            cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
            conn.commit()
            return True, "تم حذف المورد بنجاح"
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False, str(e)
        finally:
            self.db.close()
            
    def create_purchase_order(self, supplier_id, items, total_amount):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            # Create purchase order
            cursor.execute('''
                INSERT INTO purchase_orders (supplier_id, order_date, total_amount, status)
                VALUES (?, datetime('now'), ?, 'pending')
            ''', (supplier_id, total_amount))
            
            order_id = cursor.lastrowid
            
            # Create purchase order items
            cursor.executemany('''
                INSERT INTO purchase_order_items (order_id, medicine_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', [(order_id, item['medicine_id'], item['quantity'], item['price']) for item in items])
            
            conn.commit()
            return True, order_id
        except Exception as e:
            print(f"Error creating purchase order: {e}")
            return False, None
        finally:
            self.db.close()
            
    def get_all_suppliers(self):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM suppliers ORDER BY name')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting suppliers: {e}")
            return []
        finally:
            self.db.close()
            
    def get_supplier_orders(self, supplier_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    po.*,
                    s.name as supplier_name
                FROM purchase_orders po
                JOIN suppliers s ON po.supplier_id = s.id
                WHERE supplier_id = ?
                ORDER BY order_date DESC
            ''', (supplier_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting supplier orders: {e}")
            return []
        finally:
            self.db.close()
