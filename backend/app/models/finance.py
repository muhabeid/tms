from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class TransactionType(str, enum.Enum):
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class Transaction(Base):
    """Enhanced transaction model for revenue and expenses"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction Type and Category
    transaction_type = Column(Enum(TransactionType), nullable=False, index=True)
    category = Column(String, nullable=False)  # e.g., "Fuel", "Maintenance", "Delivery Revenue", "Parcel Revenue"
    
    # Amount
    amount = Column(Float, nullable=False)
    
    # Polymorphic reference to related entity
    related_entity_type = Column(String, nullable=True)  # e.g., "delivery", "trip", "job_card", "invoice"
    related_entity_id = Column(Integer, nullable=True)
    
    # Payment Details
    payment_method = Column(String, nullable=True)  # e.g., "Cash", "Bank Transfer", "M-Pesa"
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    
    # Transaction Details
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    description = Column(Text, nullable=True)
    invoice_number = Column(String, nullable=True)
    receipt_number = Column(String, nullable=True)
    
    # Reference
    reference_number = Column(String, nullable=True, index=True)


class Invoice(Base):
    """Invoice model for billing"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice Details
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=True)
    
    # Client Information
    client_name = Column(String, nullable=False)
    client_contact = Column(String, nullable=True)
    client_address = Column(Text, nullable=True)
    
    # Related Entity (polymorphic)
    related_entity_type = Column(String, nullable=True)  # e.g., "delivery", "trip"
    related_entity_id = Column(Integer, nullable=True)
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    
    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False, index=True)
    
    # Documents
    supporting_documents_json = Column(Text, nullable=True)  # JSON array of file paths/URLs
    
    # Notes
    notes = Column(Text, nullable=True)
