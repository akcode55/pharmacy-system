import hashlib
import os

def hash_password(password):
    """Hash a password using SHA-256."""
    salt = os.environ.get('PHARMACY_SALT', 'default_salt_value')
    salted = password + salt
    return hashlib.sha256(salted.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify a password against its hash."""
    return hash_password(password) == hashed_password
