from database.db_connection import DatabaseConnection

# سكريبت لإضافة عمود min_stock_level إذا لم يكن موجودًا

def add_min_stock_level_column():
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()
    try:
        # تحقق من وجود العمود مسبقاً
        cursor.execute("PRAGMA table_info(medicines);")
        columns = [row[1] for row in cursor.fetchall()]
        if 'min_stock_level' in columns:
            print("العمود min_stock_level موجود بالفعل.")
            return
        # محاولة إضافة العمود
        cursor.execute("ALTER TABLE medicines ADD COLUMN min_stock_level INTEGER DEFAULT 10;")
        conn.commit()
        print("تمت إضافة العمود min_stock_level بنجاح.")
    except Exception as e:
        print(f"خطأ أثناء إضافة العمود: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_min_stock_level_column() 