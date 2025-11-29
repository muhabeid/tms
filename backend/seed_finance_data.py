import asyncio
from app.db.session import get_session
from app.crud import finance as crud_finance
from app.schemas.finance import TransactionCreate, InvoiceCreate
from datetime import datetime, timedelta

async def seed_finance_data():
    """Seed the finance module with sample data"""
    async for session in get_session():
        try:
            print("Creating sample finance data...")
            
            # Sample transactions
            transactions = [
                TransactionCreate(
                    amount=5000.0,
                    transaction_type="REVENUE",
                    description="Freight delivery payment - Client A",
                    date=datetime.now() - timedelta(days=5),
                    category="TRANSPORT"
                ),
                TransactionCreate(
                    amount=3500.0,
                    transaction_type="REVENUE",
                    description="Express bus service - Route 101",
                    date=datetime.now() - timedelta(days=3),
                    category="EXPRESS"
                ),
                TransactionCreate(
                    amount=1200.0,
                    transaction_type="EXPENSE",
                    description="Fuel purchase - Truck fleet",
                    date=datetime.now() - timedelta(days=2),
                    category="FUEL"
                ),
                TransactionCreate(
                    amount=800.0,
                    transaction_type="EXPENSE",
                    description="Vehicle maintenance - Workshop",
                    date=datetime.now() - timedelta(days=1),
                    category="MAINTENANCE"
                ),
                TransactionCreate(
                    amount=2500.0,
                    transaction_type="REVENUE",
                    description="Cargo delivery - Local route",
                    date=datetime.now(),
                    category="TRANSPORT"
                )
            ]
            
            # Create transactions
            for transaction in transactions:
                await crud_finance.create_transaction(session, transaction)
                print(f"Created transaction: {transaction.description}")
            
            # Sample invoices
            invoices = [
                InvoiceCreate(
                    invoice_number="INV-2024-001",
                    subtotal=7500.0,
                    total_amount=7500.0,
                    amount_paid=7500.0,
                    status="PAID",
                    due_date=datetime.now() + timedelta(days=30),
                    client_name="ABC Logistics Ltd"
                ),
                InvoiceCreate(
                    invoice_number="INV-2024-002",
                    subtotal=3200.0,
                    total_amount=3200.0,
                    amount_paid=0.0,
                    status="SENT",
                    due_date=datetime.now() + timedelta(days=15),
                    client_name="Express Transport Co"
                ),
                InvoiceCreate(
                    invoice_number="INV-2024-003",
                    subtotal=4800.0,
                    total_amount=4800.0,
                    amount_paid=0.0,
                    status="OVERDUE",
                    due_date=datetime.now() - timedelta(days=5),
                    client_name="Global Freight Services"
                )
            ]
            
            # Create invoices
            for invoice in invoices:
                await crud_finance.create_invoice(session, invoice)
                print(f"Created invoice: {invoice.invoice_number}")
            
            await session.commit()
            print("✅ Sample finance data created successfully!")
            
        except Exception as e:
            print(f"❌ Error creating finance data: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_finance_data())