from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from logic.inventory import InventoryManager

class AddMedicineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventory_manager = InventoryManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Add New Medicine')
        self.setModal(True)
        layout = QVBoxLayout()

        # Name
        name_layout = QHBoxLayout()
        name_label = QLabel('Name:')
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Description
        desc_layout = QHBoxLayout()
        desc_label = QLabel('Description:')
        self.desc_input = QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # Manufacturer
        mfg_layout = QHBoxLayout()
        mfg_label = QLabel('Manufacturer:')
        self.mfg_input = QLineEdit()
        mfg_layout.addWidget(mfg_label)
        mfg_layout.addWidget(self.mfg_input)
        layout.addLayout(mfg_layout)

        # Unit Price
        price_layout = QHBoxLayout()
        price_label = QLabel('Unit Price:')
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(9999.99)
        price_layout.addWidget(price_label)
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)

        # Quantity
        qty_layout = QHBoxLayout()
        qty_label = QLabel('Quantity:')
        self.qty_input = QSpinBox()
        self.qty_input.setMaximum(9999)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_input)
        layout.addLayout(qty_layout)

        # Expiry Date
        exp_layout = QHBoxLayout()
        exp_label = QLabel('Expiry Date:')
        self.exp_input = QDateEdit()
        self.exp_input.setDate(QDate.currentDate().addYears(1))
        exp_layout.addWidget(exp_label)
        exp_layout.addWidget(self.exp_input)
        layout.addLayout(exp_layout)

        # Batch Number
        batch_layout = QHBoxLayout()
        batch_label = QLabel('Batch Number:')
        self.batch_input = QLineEdit()
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(self.batch_input)
        layout.addLayout(batch_layout)

        # Reorder Level
        reorder_layout = QHBoxLayout()
        reorder_label = QLabel('Reorder Level:')
        self.reorder_input = QSpinBox()
        self.reorder_input.setMaximum(999)
        self.reorder_input.setValue(10)
        reorder_layout.addWidget(reorder_label)
        reorder_layout.addWidget(self.reorder_input)
        layout.addLayout(reorder_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_medicine)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_medicine(self):
        """Save the new medicine to the database."""
        try:
            medicine = self.inventory_manager.add_medicine(
                name=self.name_input.text(),
                description=self.desc_input.text(),
                manufacturer=self.mfg_input.text(),
                unit_price=self.price_input.value(),
                quantity=self.qty_input.value(),
                expiry_date=self.exp_input.date().toPyDate(),
                batch_number=self.batch_input.text(),
                reorder_level=self.reorder_input.value()
            )
            
            if medicine:
                QMessageBox.information(self, 'Success', 'Medicine added successfully!')
                self.accept()
            else:
                QMessageBox.critical(self, 'Error', 'Failed to add medicine')
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error adding medicine: {str(e)}')
