from datetime import datetime
import locale

def format_date(date_str):
    """Convert date string to desired format."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return None

def format_date_arabic(date_str):
    """Format date in Arabic style (DD/MM/YYYY)."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except ValueError:
        return None

def format_datetime_arabic(datetime_str):
    """Format datetime in Arabic style (DD/MM/YYYY HH:MM)."""
    try:
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    except ValueError:
        return None

def format_currency(amount):
    """Format currency with two decimal places and Egyptian pound symbol."""
    try:
        from config import CURRENCY_SYMBOL
        return "{}{:.2f}".format(CURRENCY_SYMBOL, float(amount))
    except ImportError:
        # Fallback if config is not available
        return "£{:.2f}".format(float(amount))

def format_currency_with_name(amount):
    """Format currency with two decimal places and Egyptian pound name."""
    try:
        from config import CURRENCY_NAME
        return "{:.2f} {}".format(float(amount), CURRENCY_NAME)
    except ImportError:
        # Fallback if config is not available
        return "{:.2f} جنيه".format(float(amount))

def validate_quantity(quantity):
    """Validate that quantity is a positive integer."""
    try:
        qty = int(quantity)
        return qty >= 0, qty  # Return both validity and parsed value
    except ValueError:
        return False, None

def validate_price(price):
    """Validate that price is a positive number."""
    try:
        price_float = float(price)
        if price_float <= 0:
            return False, None
        return True, price_float  # Return both validity and parsed value
    except ValueError:
        return False, None

def parse_date(date_str):
    """Parse date from multiple formats and return in YYYY-MM-DD format."""
    formats = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']

    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return True, date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue

    # If no format matches
    return False, None

def log_stock_update(db_connection, medicine_id, old_quantity, new_quantity, username, reason=None):
    """Record a stock update in the database for audit purposes."""
    conn = db_connection.connect()
    cursor = conn.cursor()

    try:
        # First check if stock_updates table exists, if not create it
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_updates (
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

        # Insert the log entry
        cursor.execute('''
            INSERT INTO stock_updates (
                medicine_id, old_quantity, new_quantity, update_date, username, reason
            ) VALUES (?, ?, ?, datetime('now'), ?, ?)
        ''', (medicine_id, old_quantity, new_quantity, username, reason))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging stock update: {e}")
        return False
    finally:
        db_connection.close()
