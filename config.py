# Application settings
APP_NAME = "Pharmacy Management System"
APP_VERSION = "1.0.0"
COMPANY_NAME = "Your Pharmacy Name"
COMPANY_ADDRESS = "123 Main Street"
COMPANY_PHONE = "+1234567890"
COMPANY_EMAIL = "contact@yourpharmacy.com"

# Database settings
DATABASE_URL = "sqlite:///./pharmacy.db"
BACKUP_DIRECTORY = "./backups"
BACKUP_FREQUENCY = 24  # hours

# User interface settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FONT_FAMILY = "Arial"
FONT_SIZE = 10
THEME = "light"  # or "dark"

# Business settings
CURRENCY = "EGP"
CURRENCY_SYMBOL = "£"
CURRENCY_NAME = "جنيه"
CURRENCY_NAME_PLURAL = "جنيهات"
TAX_RATE = 0.14  # 14% VAT in Egypt
LOW_STOCK_THRESHOLD = 10
EXPIRY_WARNING_DAYS = 90
CRITICAL_STOCK_LEVEL = 5

# Sales settings
ALLOW_CREDIT_SALES = True
DEFAULT_PAYMENT_METHOD = "cash"
AVAILABLE_PAYMENT_METHODS = ["cash", "credit_card", "debit_card"]
INVOICE_PREFIX = "INV"
RECEIPT_FOOTER = "Thank you for your business!"

# Purchase settings
PURCHASE_ORDER_PREFIX = "PO"
DEFAULT_SUPPLIER_TERMS = 30  # days

# Report settings
REPORT_DIRECTORY = "./reports"
DEFAULT_REPORT_FORMAT = "xlsx"
REPORT_TYPES = {
    "sales": ["daily", "weekly", "monthly", "annual"],
    "inventory": ["current", "low_stock", "expiring"],
    "financial": ["profit_loss", "tax", "expenses"]
}

# Security settings
PASSWORD_MIN_LENGTH = 8
REQUIRE_SPECIAL_CHARS = True
SESSION_TIMEOUT = 30  # minutes
MAX_LOGIN_ATTEMPTS = 3

# Logging settings
LOG_DIRECTORY = "./logs"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_ROTATION = "1 week"

# Email settings
SMTP_SERVER = "smtp.yourserver.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@yourserver.com"
SMTP_PASSWORD = "your_password"
ENABLE_EMAIL_NOTIFICATIONS = False

# Backup settings
ENABLE_AUTO_BACKUP = True
BACKUP_TIME = "23:00"  # 24-hour format
KEEP_BACKUP_DAYS = 30
