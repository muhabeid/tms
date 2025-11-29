from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, case
from fastapi import HTTPException
from app.models.finance import Transaction, Invoice, TransactionType, InvoiceStatus
from app.schemas.finance import (
    TransactionCreate, TransactionUpdate,
    InvoiceCreate, InvoiceUpdate
)
from datetime import datetime, timedelta


# Transaction CRUD
async def get_transactions(db: AsyncSession, skip: int = 0, limit: int = 100,
                           transaction_type: str = None, start_date: datetime = None, end_date: datetime = None):
    """Get all transactions with optional filters"""
    query = select(Transaction)
    
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    result = await db.execute(query.offset(skip).limit(limit).order_by(Transaction.date.desc()))
    return result.scalars().all()


async def create_transaction(db: AsyncSession, transaction: TransactionCreate):
    """Create a new transaction"""
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


async def get_transaction(db: AsyncSession, transaction_id: int):
    """Get a transaction by ID"""
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


async def update_transaction(db: AsyncSession, transaction_id: int, transaction_update: TransactionUpdate):
    """Update a transaction"""
    db_transaction = await get_transaction(db, transaction_id)
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


async def delete_transaction(db: AsyncSession, transaction_id: int):
    """Delete a transaction"""
    db_transaction = await get_transaction(db, transaction_id)
    await db.delete(db_transaction)
    await db.commit()
    return {"message": "Transaction deleted successfully"}


# Invoice CRUD
async def get_invoices(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = None):
    """Get all invoices with optional status filter"""
    query = select(Invoice)
    if status:
        query = query.where(Invoice.status == status)
    result = await db.execute(query.offset(skip).limit(limit).order_by(Invoice.invoice_date.desc()))
    return result.scalars().all()


async def create_invoice(db: AsyncSession, invoice: InvoiceCreate):
    """Create a new invoice"""
    db_invoice = Invoice(**invoice.model_dump())
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


async def get_invoice(db: AsyncSession, invoice_id: int):
    """Get an invoice by ID"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


async def update_invoice(db: AsyncSession, invoice_id: int, invoice_update: InvoiceUpdate):
    """Update an invoice"""
    db_invoice = await get_invoice(db, invoice_id)
    update_data = invoice_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


async def delete_invoice(db: AsyncSession, invoice_id: int):
    """Delete an invoice"""
    db_invoice = await get_invoice(db, invoice_id)
    await db.delete(db_invoice)
    await db.commit()
    return {"message": "Invoice deleted successfully"}


async def mark_invoice_paid(db: AsyncSession, invoice_id: int, amount_paid: float, payment_method: str = None):
    """Mark an invoice as paid and create corresponding transaction"""
    db_invoice = await get_invoice(db, invoice_id)
    
    db_invoice.amount_paid += amount_paid
    if db_invoice.amount_paid >= db_invoice.total_amount:
        db_invoice.status = InvoiceStatus.PAID
    
    # Create revenue transaction
    transaction = Transaction(
        transaction_type=TransactionType.REVENUE,
        category="Invoice Payment",
        amount=amount_paid,
        related_entity_type="invoice",
        related_entity_id=invoice_id,
        payment_method=payment_method,
        status="COMPLETED",
        invoice_number=db_invoice.invoice_number,
        description=f"Payment for invoice {db_invoice.invoice_number}"
    )
    db.add(transaction)
    
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice


# Analytics Functions
async def get_financial_summary(db: AsyncSession, start_date: datetime = None, end_date: datetime = None):
    """Get financial summary with revenue and expenses"""
    query_revenue = select(func.sum(Transaction.amount)).where(Transaction.transaction_type == TransactionType.REVENUE)
    query_expense = select(func.sum(Transaction.amount)).where(Transaction.transaction_type == TransactionType.EXPENSE)
    
    if start_date:
        query_revenue = query_revenue.where(Transaction.date >= start_date)
        query_expense = query_expense.where(Transaction.date >= start_date)
    if end_date:
        query_revenue = query_revenue.where(Transaction.date <= end_date)
        query_expense = query_expense.where(Transaction.date <= end_date)
    
    result_revenue = await db.execute(query_revenue)
    result_expense = await db.execute(query_expense)
    
    total_revenue = result_revenue.scalar() or 0
    total_expense = result_expense.scalar() or 0
    
    return {
        "total_revenue": float(total_revenue),
        "total_expense": float(total_expense),
        "net_profit": float(total_revenue - total_expense)
    }


async def get_revenue_by_category(db: AsyncSession, start_date: datetime = None, end_date: datetime = None):
    """Get revenue breakdown by category"""
    query = select(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).where(Transaction.transaction_type == TransactionType.REVENUE).group_by(Transaction.category)
    
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    result = await db.execute(query)
    return [{"category": row.category, "total": float(row.total)} for row in result.all()]


async def get_expense_by_category(db: AsyncSession, start_date: datetime = None, end_date: datetime = None):
    """Get expense breakdown by category"""
    query = select(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).where(Transaction.transaction_type == TransactionType.EXPENSE).group_by(Transaction.category)
    
    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)
    
    result = await db.execute(query)
    return [{"category": row.category, "total": float(row.total)} for row in result.all()]


async def get_department_summary(db: AsyncSession, start_date: datetime = None, end_date: datetime = None):
    """Get revenue and expense totals grouped by department (category)"""
    revenue_case = case((Transaction.transaction_type == TransactionType.REVENUE, Transaction.amount), else_=0)
    expense_case = case((Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount), else_=0)

    query = select(
        Transaction.category.label('department'),
        func.sum(revenue_case).label('revenue'),
        func.sum(expense_case).label('expense')
    ).group_by(Transaction.category)

    if start_date:
        query = query.where(Transaction.date >= start_date)
    if end_date:
        query = query.where(Transaction.date <= end_date)

    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "department": row.department,
            "revenue": float(row.revenue or 0),
            "expense": float(row.expense or 0),
            "net": float((row.revenue or 0) - (row.expense or 0))
        }
        for row in rows
    ]
