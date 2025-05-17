from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func
from database.db_connection import get_db
from database.models import Medicine, Sale, SaleItem, Purchase, PurchaseItem
from utils.helpers import format_currency, format_date
import logging

logger = logging.getLogger(__name__)

class ReportManager:
    def __init__(self):
        self.db = next(get_db())
    
    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Get items that are below reorder level."""
        try:
            low_stock = self.db.query(Medicine).filter(
                Medicine.quantity <= Medicine.reorder_level
            ).all()
            
            return [{
                'name': med.name,
                'current_stock': med.quantity,
                'reorder_level': med.reorder_level,
                'manufacturer': med.manufacturer
            } for med in low_stock]
        except Exception as e:
            logger.error(f"Error getting low stock items: {str(e)}")
            return []

    def get_expiring_items(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get items that will expire within specified days."""
        try:
            expiry_date = datetime.now() + timedelta(days=days)
            expiring = self.db.query(Medicine).filter(
                Medicine.expiry_date <= expiry_date
            ).all()
            
            return [{
                'name': med.name,
                'expiry_date': format_date(med.expiry_date),
                'current_stock': med.quantity,
                'batch_number': med.batch_number
            } for med in expiring]
        except Exception as e:
            logger.error(f"Error getting expiring items: {str(e)}")
            return []

    def generate_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report."""
        try:
            total_items = self.db.query(func.count(Medicine.id)).scalar()
            total_value = self.db.query(
                func.sum(Medicine.quantity * Medicine.unit_price)
            ).scalar() or 0
            
            low_stock = self.get_low_stock_items()
            expiring_soon = self.get_expiring_items()
            
            return {
                'summary': {
                    'total_items': total_items,
                    'total_value': format_currency(total_value),
                    'low_stock_count': len(low_stock),
                    'expiring_soon_count': len(expiring_soon)
                },
                'low_stock_items': low_stock,
                'expiring_items': expiring_soon
            }
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            return {}

    def generate_sales_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate sales report for given date range."""
        try:
            sales = self.db.query(Sale).filter(
                Sale.date.between(start_date, end_date)
            ).all()
            
            total_sales = sum(sale.total_amount for sale in sales)
            avg_sale = total_sales / len(sales) if sales else 0
            
            top_products = self.db.query(
                Medicine.name,
                func.sum(SaleItem.quantity).label('total_quantity'),
                func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_value')
            ).join(SaleItem).join(Sale).filter(
                Sale.date.between(start_date, end_date)
            ).group_by(Medicine.name).order_by(
                func.sum(SaleItem.quantity).desc()
            ).limit(5).all()
            
            return {
                'summary': {
                    'total_sales': format_currency(total_sales),
                    'number_of_sales': len(sales),
                    'average_sale': format_currency(avg_sale)
                },
                'top_products': [{
                    'name': name,
                    'quantity': quantity,
                    'value': format_currency(value)
                } for name, quantity, value in top_products],
                'date_range': {
                    'start': format_date(start_date),
                    'end': format_date(end_date)
                }
            }
        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            return {}

    def generate_profit_loss_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate profit/loss report for given date range."""
        try:
            # Calculate total sales
            sales_total = self.db.query(
                func.sum(Sale.total_amount)
            ).filter(
                Sale.date.between(start_date, end_date)
            ).scalar() or 0
            
            # Calculate total purchases
            purchases_total = self.db.query(
                func.sum(Purchase.total_amount)
            ).filter(
                Purchase.date.between(start_date, end_date)
            ).scalar() or 0
            
            # Calculate expired/damaged stock value
            expired_value = self.db.query(
                func.sum(Medicine.quantity * Medicine.unit_price)
            ).filter(
                Medicine.expiry_date <= datetime.now()
            ).scalar() or 0
            
            gross_profit = sales_total - purchases_total
            net_profit = gross_profit - expired_value
            
            return {
                'summary': {
                    'total_sales': format_currency(sales_total),
                    'total_purchases': format_currency(purchases_total),
                    'expired_stock_value': format_currency(expired_value),
                    'gross_profit': format_currency(gross_profit),
                    'net_profit': format_currency(net_profit)
                },
                'date_range': {
                    'start': format_date(start_date),
                    'end': format_date(end_date)
                }
            }
        except Exception as e:
            logger.error(f"Error generating profit/loss report: {str(e)}")
            return {}

    def __del__(self):
        """Cleanup database connection."""
        if hasattr(self, 'db'):
            self.db.close()
