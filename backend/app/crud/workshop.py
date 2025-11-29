from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from fastapi import HTTPException
from app.models.workshop import (
    MaintenanceJob, Supplier, StoreItem, PurchaseOrder, PurchaseOrderItem,
    StockMovement, JobCardPart, JobStatus, MovementType, ReferenceType
)
from app.schemas.workshop import (
    MaintenanceJobCreate, MaintenanceJobUpdate,
    SupplierCreate, SupplierUpdate,
    StoreItemCreate, StoreItemUpdate,
    PurchaseOrderCreate, PurchaseOrderUpdate,
    PurchaseOrderItemCreate, PurchaseOrderItemUpdate,
    StockMovementCreate,
    JobCardPartCreate, JobCardPartUpdate
)


# MaintenanceJob CRUD
async def get_maintenance_jobs(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = None):
    """Get all maintenance jobs with optional status filter"""
    query = select(MaintenanceJob)
    if status:
        query = query.where(MaintenanceJob.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_maintenance_job(db: AsyncSession, job: MaintenanceJobCreate):
    """Create a new maintenance job"""
    job_data = job.model_dump()
    
    # Generate job card number if not provided
    if 'job_card_number' not in job_data or not job_data['job_card_number']:
        # Get the next ID for generating job card number
        result = await db.execute(select(MaintenanceJob.id).order_by(MaintenanceJob.id.desc()).limit(1))
        last_id = result.scalar_one_or_none() or 0
        job_data['job_card_number'] = f'JC-{str(last_id + 1).zfill(6)}'
    
    db_job = MaintenanceJob(**job_data)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    return db_job


async def get_maintenance_job(db: AsyncSession, job_id: int):
    """Get a maintenance job by ID"""
    result = await db.execute(select(MaintenanceJob).where(MaintenanceJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Maintenance job not found")
    return job


async def update_maintenance_job(db: AsyncSession, job_id: int, job_update: MaintenanceJobUpdate):
    """Update a maintenance job"""
    db_job = await get_maintenance_job(db, job_id)
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)
    await db.commit()
    await db.refresh(db_job)
    return db_job


async def delete_maintenance_job(db: AsyncSession, job_id: int):
    """Delete a maintenance job"""
    db_job = await get_maintenance_job(db, job_id)
    await db.delete(db_job)
    await db.commit()
    return {"message": "Maintenance job deleted successfully"}


# Supplier CRUD
async def get_suppliers(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all suppliers"""
    result = await db.execute(select(Supplier).offset(skip).limit(limit))
    return result.scalars().all()


async def create_supplier(db: AsyncSession, supplier: SupplierCreate):
    """Create a new supplier"""
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    await db.commit()
    await db.refresh(db_supplier)
    return db_supplier


async def get_supplier(db: AsyncSession, supplier_id: int):
    """Get a supplier by ID"""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


async def update_supplier(db: AsyncSession, supplier_id: int, supplier_update: SupplierUpdate):
    """Update a supplier"""
    db_supplier = await get_supplier(db, supplier_id)
    update_data = supplier_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    await db.commit()
    await db.refresh(db_supplier)
    return db_supplier


async def delete_supplier(db: AsyncSession, supplier_id: int):
    """Delete a supplier"""
    db_supplier = await get_supplier(db, supplier_id)
    await db.delete(db_supplier)
    await db.commit()
    return {"message": "Supplier deleted successfully"}


# StoreItem CRUD
async def get_store_items(db: AsyncSession, skip: int = 0, limit: int = 100, low_stock: bool = False):
    """Get all store items, optionally filter for low stock"""
    query = select(StoreItem)
    if low_stock:
        query = query.where(StoreItem.quantity_in_stock <= StoreItem.reorder_level)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_store_item(db: AsyncSession, item: StoreItemCreate):
    """Create a new store item"""
    db_item = StoreItem(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def get_store_item(db: AsyncSession, item_id: int):
    """Get a store item by ID"""
    result = await db.execute(select(StoreItem).where(StoreItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Store item not found")
    return item


async def update_store_item(db: AsyncSession, item_id: int, item_update: StoreItemUpdate):
    """Update a store item"""
    db_item = await get_store_item(db, item_id)
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_store_item(db: AsyncSession, item_id: int):
    """Delete a store item"""
    db_item = await get_store_item(db, item_id)
    await db.delete(db_item)
    await db.commit()
    return {"message": "Store item deleted successfully"}


async def adjust_stock(db: AsyncSession, item_id: int, quantity: int, movement_type: MovementType, 
                       reference_type: ReferenceType, reference_id: int, performed_by: int = None, notes: str = None):
    """Adjust stock quantity and create movement record"""
    db_item = await get_store_item(db, item_id)
    
    # Update stock quantity
    db_item.quantity_in_stock += quantity
    
    if db_item.quantity_in_stock < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Create stock movement record
    movement = StockMovement(
        item_id=item_id,
        movement_type=movement_type,
        quantity=quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        performed_by=performed_by,
        notes=notes
    )
    db.add(movement)
    
    await db.commit()
    await db.refresh(db_item)
    return db_item


# PurchaseOrder CRUD
async def get_purchase_orders(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = None):
    """Get all purchase orders with optional status filter"""
    query = select(PurchaseOrder)
    if status:
        query = query.where(PurchaseOrder.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_purchase_order(db: AsyncSession, po: PurchaseOrderCreate):
    """Create a new purchase order"""
    db_po = PurchaseOrder(**po.model_dump())
    db.add(db_po)
    await db.commit()
    await db.refresh(db_po)
    return db_po


async def get_purchase_order(db: AsyncSession, po_id: int):
    """Get a purchase order by ID"""
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == po_id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


async def update_purchase_order(db: AsyncSession, po_id: int, po_update: PurchaseOrderUpdate):
    """Update a purchase order"""
    db_po = await get_purchase_order(db, po_id)
    update_data = po_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_po, field, value)
    await db.commit()
    await db.refresh(db_po)
    return db_po


async def delete_purchase_order(db: AsyncSession, po_id: int):
    """Delete a purchase order"""
    db_po = await get_purchase_order(db, po_id)
    await db.delete(db_po)
    await db.commit()
    return {"message": "Purchase order deleted successfully"}


# PurchaseOrderItem CRUD
async def create_purchase_order_item(db: AsyncSession, po_item: PurchaseOrderItemCreate):
    """Create a new purchase order item"""
    db_po_item = PurchaseOrderItem(**po_item.model_dump())
    db.add(db_po_item)
    await db.commit()
    await db.refresh(db_po_item)
    return db_po_item


async def receive_purchase_order_item(db: AsyncSession, po_item_id: int, quantity_received: int, performed_by: int = None):
    """Receive items from purchase order and update stock"""
    result = await db.execute(select(PurchaseOrderItem).where(PurchaseOrderItem.id == po_item_id))
    db_po_item = result.scalar_one_or_none()
    if not db_po_item:
        raise HTTPException(status_code=404, detail="Purchase order item not found")
    
    # Update received quantity
    db_po_item.quantity_received += quantity_received
    
    # Add to stock
    await adjust_stock(
        db, 
        db_po_item.item_id, 
        quantity_received, 
        MovementType.IN,
        ReferenceType.PURCHASE_ORDER,
        db_po_item.purchase_order_id,
        performed_by,
        f"Received from PO #{db_po_item.purchase_order_id}"
    )
    
    await db.commit()
    await db.refresh(db_po_item)
    return db_po_item


# StockMovement CRUD
async def get_stock_movements(db: AsyncSession, item_id: int = None, skip: int = 0, limit: int = 100):
    """Get stock movements, optionally filtered by item"""
    query = select(StockMovement)
    if item_id:
        query = query.where(StockMovement.item_id == item_id)
    result = await db.execute(query.offset(skip).limit(limit).order_by(StockMovement.date.desc()))
    return result.scalars().all()


async def create_stock_movement(db: AsyncSession, movement: StockMovementCreate):
    """Create a stock movement and adjust stock"""
    quantity = movement.quantity if movement.movement_type == MovementType.IN else -movement.quantity
    
    await adjust_stock(
        db,
        movement.item_id,
        quantity,
        movement.movement_type,
        movement.reference_type,
        movement.reference_id,
        movement.performed_by,
        movement.notes
    )
    
    # Return the created movement
    result = await db.execute(
        select(StockMovement)
        .where(StockMovement.item_id == movement.item_id)
        .order_by(StockMovement.date.desc())
        .limit(1)
    )
    return result.scalar_one()


# JobCardPart CRUD
async def add_part_to_job_card(db: AsyncSession, job_card_part: JobCardPartCreate):
    """Add a part to a job card and deduct from stock"""
    # Create job card part record
    db_job_card_part = JobCardPart(**job_card_part.model_dump())
    db.add(db_job_card_part)
    
    # Deduct from stock
    await adjust_stock(
        db,
        job_card_part.item_id,
        -job_card_part.quantity_used,
        MovementType.OUT,
        ReferenceType.JOB_CARD,
        job_card_part.job_card_id,
        notes=f"Used in job card #{job_card_part.job_card_id}"
    )
    
    # Update job card parts cost
    job = await get_maintenance_job(db, job_card_part.job_card_id)
    job.parts_cost += job_card_part.total_cost
    job.total_cost = job.labor_cost + job.parts_cost
    
    await db.commit()
    await db.refresh(db_job_card_part)
    return db_job_card_part


async def get_job_card_parts(db: AsyncSession, job_card_id: int):
    """Get all parts used in a job card"""
    result = await db.execute(select(JobCardPart).where(JobCardPart.job_card_id == job_card_id))
    return result.scalars().all()
