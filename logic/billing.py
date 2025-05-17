from database.db_connection import DatabaseConnection
from datetime import datetime

class BillingSystem:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.db = DatabaseConnection()
        self.VAT_RATE = 0.15  # 15% VAT
        
        # Try to verify and fix the sales table structure
        self._verify_database_structure()
        
    def _verify_database_structure(self):
        """Verify that the database tables exist and have the right structure."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            # Check if the sales table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
            if cursor.fetchone() is None:
                # Create sales table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sales (
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
                print("Sales table created")
                
            # Check if sale_items table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sale_items'")
            if cursor.fetchone() is None:
                # Create sale_items table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sale_items (
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
                print("Sale_items table created")
                
            # Check if the sales table has all required columns
            try:
                cursor.execute("PRAGMA table_info(sales)")
                columns = [column[1] for column in cursor.fetchall()]
                
                required_columns = ['subtotal', 'discount_percentage', 'discount_amount', 
                                  'vat_rate', 'vat_amount', 'status']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"Sales table is missing columns: {missing_columns}")
                    # We need to rebuild the table
                    
                    try:
                        # Get existing data if possible
                        cursor.execute("SELECT id, sale_date, total FROM sales")
                        existing_sales = cursor.fetchall()
                    except:
                        existing_sales = []
                    
                    # Recreate the sales table
                    cursor.execute("DROP TABLE IF EXISTS sales_old")
                    cursor.execute("ALTER TABLE sales RENAME TO sales_old")
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
                    
                    # Restore existing data
                    for sale in existing_sales:
                        sale_id, sale_date, total = sale
                        subtotal = total / 1.15  # Estimate the original subtotal
                        vat_amount = total - subtotal
                        cursor.execute("""
                            INSERT INTO sales (id, sale_date, subtotal, vat_amount, total)
                            VALUES (?, ?, ?, ?, ?)
                        """, (sale_id, sale_date, subtotal, vat_amount, total))
                    
                    print("Sales table recreated with proper structure")
            except Exception as e:
                print(f"Error checking sales table structure: {e}")
            
            conn.commit()
        except Exception as e:
            print(f"Error verifying database structure: {e}")
        finally:
            conn.close()
        
    def calculate_total_with_tax_and_discount(self, subtotal, discount_percentage=0):
        """Calculate final total with VAT and discount."""
        # Apply discount first
        discount_amount = (subtotal * discount_percentage / 100) if discount_percentage else 0
        after_discount = subtotal - discount_amount
        
        # Apply VAT
        vat_amount = after_discount * self.VAT_RATE
        total = after_discount + vat_amount
        
        return {
            'subtotal': subtotal,
            'discount_percentage': discount_percentage,
            'discount_amount': discount_amount,
            'vat_rate': self.VAT_RATE,
            'vat_amount': vat_amount,
            'total': total
        }
        
    def create_sale(self, items, discount_percentage=0):
        """Create a sale with multiple items and apply discount if any."""
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            # Calculate subtotal and verify stock for all items first
            subtotal = 0
            for item in items:
                medicine_id = item['medicine_id']
                quantity = item['quantity']
                
                # Get medicine details
                cursor.execute('SELECT price, quantity FROM medicines WHERE id = ?', (medicine_id,))
                medicine = cursor.fetchone()
                
                if not medicine:
                    raise Exception(f"الدواء غير موجود: {medicine_id}")
                    
                price, current_stock = medicine
                
                if current_stock < quantity:
                    raise Exception(f"الكمية غير كافية للدواء: {medicine_id}")
                    
                item_total = price * quantity
                subtotal += item_total
            
            # Calculate final totals with tax and discount
            totals = self.calculate_total_with_tax_and_discount(subtotal, discount_percentage)
            
            # Create sale - use minimal columns for maximum compatibility
            try:
                # First try to create table if it doesn't exist
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
                
                # Create sale_items table if it doesn't exist
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
                
                # Insert sale with minimal required columns
                cursor.execute('''
                    INSERT INTO sales (sale_date, total) 
                    VALUES (datetime('now'), ?)
                ''', (totals['total'],))
                
                sale_id = cursor.lastrowid
            except Exception as insert_error:
                print(f"Error inserting sale: {insert_error}")
                # Last resort fallback - create a minimal sales table from scratch
                try:
                    cursor.execute("DROP TABLE IF EXISTS sales")
                    cursor.execute("""
                        CREATE TABLE sales (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sale_date DATETIME NOT NULL,
                            total REAL NOT NULL
                        )
                    """)
                    
                    cursor.execute("INSERT INTO sales (sale_date, total) VALUES (datetime('now'), ?)",
                                  (totals['total'],))
                    
                    sale_id = cursor.lastrowid
                except Exception as last_error:
                    raise Exception(f"فشل في إنشاء الفاتورة: {last_error}")
            
            # Create sale items and update stock
            for item in items:
                medicine_id = item['medicine_id']
                quantity = item['quantity']
                
                # Get current price
                cursor.execute('SELECT price FROM medicines WHERE id = ?', (medicine_id,))
                price = cursor.fetchone()[0]
                
                # Try to add sale item with required fields only
                try:
                    cursor.execute('''
                        INSERT INTO sale_items (sale_id, medicine_id, quantity)
                        VALUES (?, ?, ?)
                    ''', (sale_id, medicine_id, quantity))
                except Exception as item_error:
                    print(f"Error inserting sale item: {item_error}")
                    # Last resort - create minimal table
                    cursor.execute("DROP TABLE IF EXISTS sale_items")
                    cursor.execute("""
                        CREATE TABLE sale_items (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sale_id INTEGER NOT NULL,
                            medicine_id INTEGER NOT NULL,
                            quantity INTEGER NOT NULL
                        )
                    """)
                    
                    cursor.execute('''
                        INSERT INTO sale_items (sale_id, medicine_id, quantity)
                        VALUES (?, ?, ?)
                    ''', (sale_id, medicine_id, quantity))
                
                # Update stock
                cursor.execute('''
                    UPDATE medicines
                    SET quantity = quantity - ?
                    WHERE id = ?
                ''', (quantity, medicine_id))
            
            conn.commit()
            return True, totals['total']
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating sale: {e}")
            return False, 0
        finally:
            self.db.close()
            
    def get_daily_sales(self, date=None):
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            # Make sure the tables exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_date DATETIME NOT NULL,
                    total REAL DEFAULT 0
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL
                )
            """)
            
            # Use a very basic query that should work with any schema
            try:
                cursor.execute('''
                    SELECT s.id, s.sale_date, s.total, 
                           si.medicine_id, si.quantity,
                           m.name as medicine_name
                    FROM sales s
                    JOIN sale_items si ON s.id = si.sale_id
                    JOIN medicines m ON si.medicine_id = m.id
                    WHERE date(s.sale_date) = ?
                    ORDER BY s.sale_date DESC
                ''', (date,))
                
                # Process the result to add zero values for missing columns
                result = []
                for row in cursor.fetchall():
                    sale_id, sale_date, total, medicine_id, quantity, medicine_name = row
                    
                    # Calculate estimated values for missing columns
                    subtotal = total / 1.15 if total else 0
                    vat_amount = total - subtotal if total else 0
                    unit_price = subtotal / quantity if quantity else 0
                    total_price = unit_price * quantity if quantity else 0
                    
                    # Create a processed row with all needed fields
                    processed_row = (
                        sale_id, sale_date, subtotal, 0, # discount_amount
                        vat_amount, total, 'completed', # status
                        medicine_id, quantity, unit_price, total_price,
                        medicine_name
                    )
                    result.append(processed_row)
                
                return result
            except Exception as e:
                print(f"Error in daily sales query: {e}")
                return []
                
        except Exception as e:
            print(f"Error getting daily sales: {e}")
            return []
        finally:
            self.db.close()
            
    def calculate_total_sales(self, start_date, end_date):
        conn = self.db.connect()
        cursor = conn.cursor()
        
        try:
            # Make sure the sales table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_date DATETIME NOT NULL,
                    total REAL DEFAULT 0
                )
            """)
            
            # Use a very simple query without any filters
            cursor.execute('''
                SELECT SUM(total)
                FROM sales
                WHERE date(sale_date) BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            result = cursor.fetchone()
            return result[0] or 0
        except Exception as e:
            print(f"Error calculating total sales: {e}")
            return 0
        finally:
            self.db.close()
