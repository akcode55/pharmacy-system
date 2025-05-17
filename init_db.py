from datetime import datetime, timedelta
from database.db_connection import engine, get_db
from database.models import Base, User, Medicine
from utils.encryption import hash_password

def init_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    # Create admin user if not exists
    if not db.query(User).filter(User.username == 'admin').first():
        admin = User(
            username='admin',
            full_name='System Administrator',
            hashed_password=hash_password('admin123'),
            is_admin=True
        )
        db.add(admin)
    
    # Add sample medicines
    sample_medicines = [
        {
            'name': 'Paracetamol 500mg',
            'description': 'Pain relief and fever reduction',
            'manufacturer': 'Generic Pharma',
            'unit_price': 5.99,
            'quantity': 100,
            'expiry_date': datetime.now() + timedelta(days=365),
            'batch_number': 'PARA001',
            'reorder_level': 20
        },
        {
            'name': 'Amoxicillin 250mg',
            'description': 'Antibiotic for bacterial infections',
            'manufacturer': 'MediCorp',
            'unit_price': 12.99,
            'quantity': 50,
            'expiry_date': datetime.now() + timedelta(days=180),
            'batch_number': 'AMOX001',
            'reorder_level': 15
        },
        {
            'name': 'Ibuprofen 400mg',
            'description': 'Anti-inflammatory pain relief',
            'manufacturer': 'HealthPharm',
            'unit_price': 7.99,
            'quantity': 75,
            'expiry_date': datetime.now() + timedelta(days=730),
            'batch_number': 'IBU001',
            'reorder_level': 25
        }
    ]
    
    for med_data in sample_medicines:
        if not db.query(Medicine).filter(Medicine.name == med_data['name']).first():
            medicine = Medicine(**med_data)
            db.add(medicine)
    
    # Commit changes
    db.commit()

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("Database initialized successfully!")
