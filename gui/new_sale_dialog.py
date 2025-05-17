from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QPushButton, QMessageBox,
                             QTableWidget, QTableWidgetItem, QComboBox)
from PyQt5.QtCore import Qt
from datetime import datetime
from typing import List, Dict
from logic.billing import BillingManager
from logic.inventory import InventoryManager
from utils.helpers import format_currency, calculate_total

class NewSaleDialog(QDialog):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.billing_manager = BillingManager()
        self.inventory_manager = InventoryManager()
        self.sale_items = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('New Sale')
        self.setModal(True)
        self.setMinimumWidth(600)
        layout = QVBoxLayout()

        # Customer Information
        customer_layout = QHBoxLayout()
        customer_label = QLabel('Customer Name:')
        self.customer_input = QLineEdit()
        customer_layout.addWidget(customer_label)
        customer_layout.addWidget(self.customer_input)
        layout.addLayout(customer_layout)

        # Add Item Section
        item_layout = QHBoxLayout()
        
        # Medicine selection
        self.medicine_combo = QComboBox()
        self.load_medicines()
        
        # Quantity input
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(999)
        
        # Add item button
        add_item_btn = QPushButton('Add Item')
        add_item_btn.clicked.connect(self.add_item)
        
        item_layout.addWidget(QLabel('Medicine:'))
        item_layout.addWidget(self.medicine_combo)
        item_layout.addWidget(QLabel('Quantity:'))
        item_layout.addWidget(self.quantity_input)
        item_layout.addWidget(add_item_btn)
        layout.addLayout(item_layout)

        # Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            'Medicine', 'Unit Price', 'Quantity', 'Total', 'Action'
        ])
        layout.addWidget(self.items_table)

        # Total Amount
        total_layout = QHBoxLayout()
        self.total_label = QLabel('Total: $0.00')
        total_layout.addStretch()
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton('Complete Sale')
        save_btn.clicked.connect(self.complete_sale)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_medicines(self):
        """Load available medicines into the combo box."""
        medicines = self.inventory_manager.get_all_medicines()
        for medicine in medicines:
            if medicine.quantity > 0:  # Only show medicines in stock
                self.medicine_combo.addItem(medicine.name, medicine.id)

    def add_item(self):
        """Add item to the sale."""
        medicine_id = self.medicine_combo.currentData()
        quantity = self.quantity_input.value()
        
        if not medicine_id:
            QMessageBox.warning(self, 'Error', 'Please select a medicine')
            return
        
        medicine = self.inventory_manager.get_medicine(medicine_id)
        if not medicine:
            QMessageBox.warning(self, 'Error', 'Medicine not found')
            return
        
        if quantity > medicine.quantity:
            QMessageBox.warning(self, 'Error', 'Insufficient stock')
            return
        
        # Add to sale items
        item = {
            'medicine_id': medicine_id,
            'name': medicine.name,
            'quantity': quantity,
            'unit_price': medicine.unit_price
        }
        self.sale_items.append(item)
        
        # Update table
        self.update_items_table()

    def update_items_table(self):
        """Update the items table and total amount."""
        self.items_table.setRowCount(len(self.sale_items))
        total = 0
        
        for row, item in enumerate(self.sale_items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(format_currency(item['unit_price'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            
            item_total = item['quantity'] * item['unit_price']
            total += item_total
            self.items_table.setItem(row, 3, QTableWidgetItem(format_currency(item_total)))
            
            # Delete button
            delete_btn = QPushButton('Remove')
            delete_btn.clicked.connect(lambda checked, row=row: self.remove_item(row))
            self.items_table.setCellWidget(row, 4, delete_btn)
        
        self.total_label.setText(f'Total: {format_currency(total)}')

    def remove_item(self, row: int):
        """Remove item from sale."""
        self.sale_items.pop(row)
        self.update_items_table()

    def complete_sale(self):
        """Complete the sale transaction."""
        if not self.sale_items:
            QMessageBox.warning(self, 'Error', 'Please add items to the sale')
            return
        
        customer_name = self.customer_input.text()
        if not customer_name:
            QMessageBox.warning(self, 'Error', 'Please enter customer name')
            return
        
        # Create sale
        sale = self.billing_manager.create_sale(
            items=self.sale_items,
            customer_name=customer_name,
            user_id=self.user_id
        )
        
        if sale:
            QMessageBox.information(self, 'Success', 'Sale completed successfully!')
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to complete sale')
