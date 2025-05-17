"""
هذا الملف مخصص لإعادة إنشاء قاعدة البيانات بشكل كامل
يقوم بحذف وإعادة إنشاء قاعدة البيانات والجداول
"""

import os
import sqlite3
from pathlib import Path

def rebuild_database():
    # الحصول على مسار قاعدة البيانات
    db_path = Path(__file__).parent / 'pharmacy.db'
    
    # حذف قاعدة البيانات إذا كانت موجودة
    if db_path.exists():
        print(f"حذف قاعدة البيانات الموجودة: {db_path}")
        try:
            os.remove(db_path)
            print("تم حذف قاعدة البيانات بنجاح")
        except Exception as e:
            print(f"حدث خطأ أثناء محاولة حذف قاعدة البيانات: {str(e)}")
            return False
    
    # إنشاء قاعدة البيانات من جديد وإنشاء الجداول
    from database.models import create_tables
    
    try:
        print("جاري إنشاء قاعدة البيانات والجداول...")
        create_tables()
        print("تم إنشاء قاعدة البيانات والجداول بنجاح")
        
        # إنشاء مستخدم الإدارة الافتراضي
        from utils.encryption import hash_password
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        try:
            hashed_password = hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', ('admin', hashed_password, 'admin'))
            conn.commit()
            print("تم إنشاء مستخدم الإدارة الافتراضي (admin/admin123)")
        except Exception as e:
            print(f"خطأ عند إنشاء مستخدم الإدارة: {e}")
        finally:
            conn.close()
            
        return True
    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء قاعدة البيانات: {str(e)}")
        return False

if __name__ == "__main__":
    rebuild_database() 