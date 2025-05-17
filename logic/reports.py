from database.db_connection import DatabaseConnection
import csv
from datetime import datetime, timedelta

class ReportGenerator:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.db = DatabaseConnection()
        
    def generate_sales_report(self, start_date, end_date, export_path=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    s.sale_date,
                    m.name,
                    s.quantity,
                    s.total_price
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.id
                WHERE date(s.sale_date) BETWEEN ? AND ?
                ORDER BY s.sale_date
            ''', (start_date, end_date))
            
            results = cursor.fetchall()
            
            if export_path:
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['التاريخ', 'اسم الدواء', 'الكمية', 'السعر الإجمالي'])
                    writer.writerows(results)
                    
            return results
            
        except Exception as e:
            print(f"Error generating sales report: {e}")
            return []
        finally:
            self.db.close()
            
    def generate_inventory_report(self, export_path=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    name,
                    quantity,
                    price,
                    expiry_date,
                    manufacturer
                FROM medicines
                ORDER BY name
            ''')
            
            results = cursor.fetchall()
            
            if export_path:
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['اسم الدواء', 'الكمية', 'السعر', 'تاريخ الانتهاء', 'الشركة المصنعة'])
                    writer.writerows(results)
                    
            return results
            
        except Exception as e:
            print(f"Error generating inventory report: {e}")
            return []
        finally:
            self.db.close()
            
    def generate_expiry_alert_report(self, days=90, export_path=None):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT 
                    name,
                    quantity,
                    expiry_date,
                    manufacturer
                FROM medicines
                WHERE date(expiry_date) <= date('now', '+' || ? || ' days')
                ORDER BY expiry_date
            ''', (days,))
            
            results = cursor.fetchall()
            
            if export_path:
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['اسم الدواء', 'الكمية', 'تاريخ الانتهاء', 'الشركة المصنعة'])
                    writer.writerows(results)
                    
            return results
            
        except Exception as e:
            print(f"Error generating expiry alert report: {e}")
            return []
        finally:
            self.db.close()
