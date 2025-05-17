from database.db_connection import DatabaseConnection

def create_tables():
    db = DatabaseConnection()
    conn = db.connect()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')    # Create Medicines table with extended features    # Create Medicines table with all required columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
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
    ''')# Create Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date DATETIME NOT NULL,
            subtotal REAL NOT NULL DEFAULT 0,
            discount_percentage REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            vat_rate REAL DEFAULT 0.15,
            vat_amount REAL DEFAULT 0,
            total REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    ''')
    
    # Create Sale Items table
    cursor.execute('''
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
    ''')

    # Create Suppliers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            address TEXT,
            email TEXT
        )
    ''')

    # Create Purchase Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER,
            order_date DATE NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')

    # Create Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            loyalty_points INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Customer Purchases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            sale_id INTEGER NOT NULL,
            points_earned INTEGER DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (sale_id) REFERENCES sales (id)
        )
    ''')

    conn.commit()
    db.close()

if __name__ == "__main__":
    create_tables()
