from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import finance as crud_finance
from app.schemas.finance import (
    TransactionCreate, TransactionUpdate, TransactionResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse
)
from typing import List, Optional
from datetime import datetime
from app.core.error_handler import get_error_handler

router = APIRouter()
error_handler = get_error_handler("finance")


# Transaction Endpoints
@router.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type (REVENUE/EXPENSE)"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: AsyncSession = Depends(get_session)
):
    """Get all transactions with optional filters"""
    try:
        transactions = await crud_finance.get_transactions(db, skip=skip, limit=limit,
                                                           transaction_type=transaction_type,
                                                           start_date=start_date, end_date=end_date)
        return transactions
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/transactions", method="GET")
        raise


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, db: AsyncSession = Depends(get_session)):
    """Create a new transaction"""
    try:
        return await crud_finance.create_transaction(db, transaction)
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/transactions", method="POST", request_data=transaction.dict() if hasattr(transaction, 'dict') else str(transaction))
        raise


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Get a transaction by ID"""
    return await crud_finance.get_transaction(db, transaction_id)


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: AsyncSession = Depends(get_session)):
    """Update a transaction"""
    return await crud_finance.update_transaction(db, transaction_id, transaction_update)


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a transaction"""
    return await crud_finance.delete_transaction(db, transaction_id)


# Invoice Endpoints
@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by invoice status"),
    db: AsyncSession = Depends(get_session)
):
    """Get all invoices with optional status filter"""
    invoices = await crud_finance.get_invoices(db, skip=skip, limit=limit, status=status)
    return invoices


@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(invoice: InvoiceCreate, db: AsyncSession = Depends(get_session)):
    """Create a new invoice"""
    try:
        return await crud_finance.create_invoice(db, invoice)
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/invoices", method="POST", request_data=invoice.dict() if hasattr(invoice, 'dict') else str(invoice))
        raise


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: int, db: AsyncSession = Depends(get_session)):
    """Get an invoice by ID"""
    return await crud_finance.get_invoice(db, invoice_id)


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(invoice_id: int, invoice_update: InvoiceUpdate, db: AsyncSession = Depends(get_session)):
    """Update an invoice"""
    return await crud_finance.update_invoice(db, invoice_id, invoice_update)


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_session)):
    """Delete an invoice"""
    return await crud_finance.delete_invoice(db, invoice_id)


@router.put("/invoices/{invoice_id}/pay", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: int,
    amount_paid: float = Query(..., description="Amount paid"),
    payment_method: Optional[str] = Query(None, description="Payment method"),
    db: AsyncSession = Depends(get_session)
):
    """Mark an invoice as paid and create transaction"""
    return await crud_finance.mark_invoice_paid(db, invoice_id, amount_paid, payment_method)


# Analytics Endpoints
@router.get("/analytics/summary")
async def get_financial_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for summary"),
    end_date: Optional[datetime] = Query(None, description="End date for summary"),
    db: AsyncSession = Depends(get_session)
):
    """Get financial summary with revenue, expenses, and net profit"""
    try:
        return await crud_finance.get_financial_summary(db, start_date, end_date)
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/analytics/summary", method="GET")
        raise


@router.get("/analytics/revenue-by-category")
async def get_revenue_by_category(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_session)
):
    """Get revenue breakdown by category"""
    return await crud_finance.get_revenue_by_category(db, start_date, end_date)


@router.get("/analytics/expense-by-category")
async def get_expense_by_category(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_session)
):
    """Get expense breakdown by category"""
    return await crud_finance.get_expense_by_category(db, start_date, end_date)


@router.get("/analytics/by-department")
async def get_by_department(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_session)
):
    """Get revenue and expense totals grouped by department (category)"""
    try:
        return await crud_finance.get_department_summary(db, start_date, end_date)
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/analytics/by-department", method="GET")
        raise