from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


# Transaction Schemas
class TransactionBase(BaseModel):
    transaction_type: TransactionType
    category: str
    amount: float
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    payment_method: Optional[str] = None
    status: Optional[TransactionStatus] = TransactionStatus.PENDING
    date: Optional[datetime] = None
    description: Optional[str] = None
    invoice_number: Optional[str] = None
    receipt_number: Optional[str] = None
    reference_number: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    transaction_type: Optional[TransactionType] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    payment_method: Optional[str] = None
    status: Optional[TransactionStatus] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    invoice_number: Optional[str] = None
    receipt_number: Optional[str] = None
    reference_number: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int

    model_config = {"from_attributes": True}


# Invoice Schemas
class InvoiceBase(BaseModel):
    invoice_number: str
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    client_name: str
    client_contact: Optional[str] = None
    client_address: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    subtotal: float
    tax: Optional[float] = 0.0
    total_amount: float
    amount_paid: Optional[float] = 0.0
    status: Optional[InvoiceStatus] = InvoiceStatus.DRAFT
    supporting_documents_json: Optional[str] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    client_address: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    amount_paid: Optional[float] = None
    status: Optional[InvoiceStatus] = None
    supporting_documents_json: Optional[str] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: int

    model_config = {"from_attributes": True}
