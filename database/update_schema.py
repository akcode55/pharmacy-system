import os
import sys
import sqlite3

# إضافة المجلد الرئيسي للمشروع إلى مسار البحث
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database.db_connection import DatabaseConnection

def update_database_schema():
    """تحديث هيكل قاعدة البيانات دون فقدان البيانات."""
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()
    
    try:
        # التحقق من وجود عمود barcode في جدول medicines
        cursor.execute("PRAGMA table_info(medicines)")
        med_columns = [column[1] for column in cursor.fetchall()]
        
        # إضافة عمود barcode إذا لم يكن موجوداً
        if 'barcode' not in med_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN barcode TEXT")
            print("تم إضافة عمود barcode إلى جدول medicines")
        
        # التحقق من وجود عمود min_stock_level في جدول medicines
        if 'min_stock_level' not in med_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN min_stock_level INTEGER DEFAULT 10")
            print("تم إضافة عمود min_stock_level إلى جدول medicines")
        
        # التحقق من وجود عمود location في جدول medicines
        if 'location' not in med_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN location TEXT")
            print("تم إضافة عمود location إلى جدول medicines")
        
        # التحقق من وجود عمود is_active في جدول medicines
        if 'is_active' not in med_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("تم إضافة عمود is_active إلى جدول medicines")
        
        # التحقق من وجود عمود category في جدول medicines
        if 'category' not in med_columns:
            cursor.execute("ALTER TABLE medicines ADD COLUMN category TEXT")
            print("تم إضافة عمود category إلى جدول medicines")
        
        # التحقق من وجود جدول sales وهيكله
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        sales_table_exists = cursor.fetchone() is not None
        
        if sales_table_exists:
            # التحقق من أعمدة جدول sales
            cursor.execute("PRAGMA table_info(sales)")
            sales_columns = [column[1] for column in cursor.fetchall()]
            
            # التحقق من وجود جميع الأعمدة المطلوبة
            required_sales_columns = ['subtotal', 'discount_percentage', 'discount_amount', 'vat_rate', 'vat_amount', 'status']
            missing_columns = [col for col in required_sales_columns if col not in sales_columns]
            
            if missing_columns:
                print(f"أعمدة مفقودة في جدول sales: {', '.join(missing_columns)}")
                
                # إعادة إنشاء جدول sales بالهيكل الصحيح
                # أولاً، نقوم بحفظ البيانات الموجودة
                cursor.execute("SELECT id, sale_date, total FROM sales")
                existing_sales = cursor.fetchall()
                
                # إنشاء الجدول بالهيكل الجديد
                cursor.execute("DROP TABLE IF EXISTS sales_temp")
                cursor.execute('''
                    CREATE TABLE sales_temp (
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
                ''')
                
                # نقل البيانات المحفوظة إلى الجدول الجديد
                for sale in existing_sales:
                    sale_id, sale_date, total = sale
                    # حساب القيم الافتراضية للأعمدة الجديدة
                    subtotal = total / 1.15  # تقدير مبدئي للمجموع الفرعي
                    vat_amount = total - subtotal
                    
                    cursor.execute('''
                        INSERT INTO sales_temp (id, sale_date, subtotal, vat_amount, total)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (sale_id, sale_date, subtotal, vat_amount, total))
                
                # حذف الجدول القديم وإعادة تسمية الجدول الجديد
                cursor.execute("DROP TABLE sales")
                cursor.execute("ALTER TABLE sales_temp RENAME TO sales")
                
                print("تم إعادة إنشاء جدول sales بالهيكل الصحيح وحفظ البيانات")
        else:
            # إنشاء جدول المبيعات إذا لم يكن موجوداً
            cursor.execute('''
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
            ''')
            print("تم إنشاء جدول sales")
        
        # التحقق من وجود جدول sale_items
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sale_items'")
        sale_items_table_exists = cursor.fetchone() is not None
        
        if not sale_items_table_exists:
            # إنشاء جدول عناصر المبيعات إذا لم يكن موجوداً
            cursor.execute('''
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
            ''')
            print("تم إنشاء جدول sale_items")
        
        conn.commit()
        return True, "تم تحديث قاعدة البيانات بنجاح"
    except Exception as e:
        conn.rollback()
        return False, f"حدث خطأ أثناء تحديث قاعدة البيانات: {str(e)}"
    finally:
        db.close()

# نستخدم هذه الوظيفة في حالة الحاجة إلى التحديث اليدوي
def manual_update():
    """تحديث قاعدة البيانات مباشرة عن طريق اتصال مباشر بها."""
    db_path = os.path.join(current_dir, 'pharmacy.db')
    
    try:
        # الاتصال بقاعدة البيانات مباشرة
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # التحقق من وجود جدول medicines
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='medicines'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            print("جاري إعادة هيكلة جدول medicines بالتعريف الكامل...")
            
            # حفظ البيانات الموجودة
            cursor.execute("SELECT * FROM medicines")
            existing_data = cursor.fetchall()
            
            # احصل على أسماء الأعمدة الحالية
            cursor.execute("PRAGMA table_info(medicines)")
            column_info = cursor.fetchall()
            existing_columns = [info[1] for info in column_info]
            
            # الأعمدة المطلوبة في الجدول الجديد
            required_columns = ['id', 'name', 'description', 'price', 'quantity', 'expiry_date', 
                               'manufacturer', 'barcode', 'category', 'min_stock_level', 
                               'location', 'is_active']
            
            # إنشاء جدول مؤقت بالتعريف الكامل
            cursor.execute("""
                CREATE TABLE medicines_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    expiry_date DATE NOT NULL,
                    manufacturer TEXT,
                    barcode TEXT UNIQUE,
                    category TEXT,
                    min_stock_level INTEGER DEFAULT 10,
                    location TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # نقل البيانات من الجدول القديم إلى الجدول الجديد
            if existing_data:
                # إعداد قائمة الأعمدة المشتركة بين الجدولين
                common_columns = [col for col in existing_columns if col in required_columns]
                insert_columns = ', '.join(common_columns)
                
                # إعداد قيم الأعمدة المفقودة
                for row in existing_data:
                    # إنشاء قائمة القيم بناءً على الأعمدة المشتركة
                    values = []
                    for idx, col in enumerate(existing_columns):
                        if col in common_columns:
                            values.append(row[idx])
                    
                    # إعداد استعلام الإدخال
                    placeholders = ', '.join(['?' for _ in range(len(values))])
                    
                    try:
                        # إدخال البيانات في الجدول الجديد
                        cursor.execute(f"INSERT INTO medicines_new ({insert_columns}) VALUES ({placeholders})", values)
                    except sqlite3.Error as e:
                        print(f"خطأ أثناء نقل الصف: {values} - {str(e)}")
            
            # حذف الجدول القديم وإعادة تسمية الجدول الجديد
            cursor.execute("DROP TABLE medicines")
            cursor.execute("ALTER TABLE medicines_new RENAME TO medicines")
            
            print("تمت إعادة هيكلة جدول medicines بنجاح مع الحفاظ على البيانات الموجودة")
        else:
            # إنشاء جدول medicines من الصفر
            cursor.execute("""
                CREATE TABLE medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    expiry_date DATE NOT NULL,
                    manufacturer TEXT,
                    barcode TEXT UNIQUE,
                    category TEXT,
                    min_stock_level INTEGER DEFAULT 10,
                    location TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            print("تم إنشاء جدول medicines من الصفر")
        
        # التحقق من وجود جدول stock_updates وإنشائه إذا لم يكن موجوداً
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_updates'")
        if cursor.fetchone() is None:
            cursor.execute('''
                CREATE TABLE stock_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_id INTEGER NOT NULL,
                    old_quantity INTEGER NOT NULL,
                    new_quantity INTEGER NOT NULL,
                    update_date DATETIME NOT NULL,
                    username TEXT NOT NULL,
                    reason TEXT,
                    FOREIGN KEY (medicine_id) REFERENCES medicines (id)
                )
            ''')
            print("تم إنشاء جدول stock_updates")
        
        # التحقق من وجود جدول sales وإعادة إنشائه عند الحاجة
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
        sales_exists = cursor.fetchone() is not None
        
        if sales_exists:
            print("إعادة إنشاء جدول sales...")
            # حفظ البيانات الموجودة (إذا كانت موجودة)
            try:
                cursor.execute("SELECT id, sale_date, total FROM sales")
                existing_sales = cursor.fetchall()
            except sqlite3.Error:
                # في حالة عدم وجود الأعمدة المطلوبة
                existing_sales = []

            # إنشاء جدول مؤقت بالتعريف الصحيح
            cursor.execute("DROP TABLE IF EXISTS sales_new")
            cursor.execute("""
                CREATE TABLE sales_new (
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
            
            # نقل البيانات الموجودة إذا كانت هناك بيانات
            for sale in existing_sales:
                try:
                    sale_id, sale_date, total = sale
                    # تقدير المجموع الفرعي وضريبة القيمة المضافة
                    subtotal = total / 1.15
                    vat_amount = total - subtotal
                    
                    cursor.execute("""
                        INSERT INTO sales_new (id, sale_date, subtotal, vat_amount, total)
                        VALUES (?, ?, ?, ?, ?)
                    """, (sale_id, sale_date, subtotal, vat_amount, total))
                except sqlite3.Error as e:
                    print(f"خطأ أثناء نقل بيانات المبيعات: {str(e)}")
            
            # حذف الجدول القديم وإعادة تسمية الجدول الجديد
            cursor.execute("DROP TABLE sales")
            cursor.execute("ALTER TABLE sales_new RENAME TO sales")
            print("تم إعادة إنشاء جدول sales بنجاح")
        else:
            # إنشاء جدول sales من الصفر
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
            print("تم إنشاء جدول sales من الصفر")
        
        # التحقق من وجود جدول sale_items وإنشائه إذا لم يكن موجوداً
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sale_items'")
        if cursor.fetchone() is None:
            cursor.execute('''
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
            ''')
            print("تم إنشاء جدول sale_items")
        
        conn.commit()
        print("تم تحديث قاعدة البيانات بنجاح")
        return True
    except Exception as e:
        print(f"حدث خطأ أثناء تحديث قاعدة البيانات: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# تشغيل التحديث عند استدعاء الملف مباشرة
if __name__ == "__main__":
    manual_update()
