from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import workshop as crud_workshop
from app.schemas.workshop import (
    MaintenanceJobCreate, MaintenanceJobUpdate, MaintenanceJobResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
    StoreItemCreate, StoreItemUpdate, StoreItemResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseOrderItemCreate, PurchaseOrderItemUpdate, PurchaseOrderItemResponse,
    StockMovementCreate, StockMovementResponse,
    JobCardPartCreate, JobCardPartUpdate, JobCardPartResponse
)
from typing import List, Optional
from app.core.error_handler import get_error_handler

router = APIRouter()
error_handler = get_error_handler("workshop")


# MaintenanceJob Endpoints
@router.get("/jobs", response_model=List[MaintenanceJobResponse])
async def list_maintenance_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by job status"),
    db: AsyncSession = Depends(get_session)
):
    """Get all maintenance jobs with optional status filter"""
    try:
        # Temporarily return mock data to test frontend connectivity
        mock_jobs = [
            {
                "id": 1,
                "job_card_number": "JC-000001",
                "vehicle_id": 1,
                "mechanic_id": 1,
                "job_type": "SCHEDULED",
                "description": "Routine maintenance check",
                "scheduled_date": "2025-11-25T10:00:00",
                "start_date": None,
                "completion_date": None,
                "priority": "MEDIUM",
                "status": "PENDING",
                "labor_cost": 150.0,
                "parts_cost": 200.0,
                "total_cost": 350.0
            },
            {
                "id": 2,
                "job_card_number": "JC-000002",
                "vehicle_id": 2,
                "mechanic_id": 2,
                "job_type": "BREAKDOWN",
                "description": "Engine repair",
                "scheduled_date": "2025-11-24T14:00:00",
                "start_date": "2025-11-24T14:30:00",
                "completion_date": None,
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "labor_cost": 300.0,
                "parts_cost": 500.0,
                "total_cost": 800.0
            }
        ]
        
        # Filter by status if provided
        if status:
            mock_jobs = [job for job in mock_jobs if job["status"] == status]
        
        # Apply pagination
        return mock_jobs[skip:skip + limit]
        
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/jobs", method="GET")
        raise


@router.post("/jobs", response_model=MaintenanceJobResponse)
async def create_maintenance_job(job: MaintenanceJobCreate, db: AsyncSession = Depends(get_session)):
    """Create a new maintenance job"""
    return await crud_workshop.create_maintenance_job(db, job)


@router.get("/jobs/{job_id}", response_model=MaintenanceJobResponse)
async def get_maintenance_job(job_id: int, db: AsyncSession = Depends(get_session)):
    """Get a maintenance job by ID"""
    return await crud_workshop.get_maintenance_job(db, job_id)


@router.put("/jobs/{job_id}", response_model=MaintenanceJobResponse)
async def update_maintenance_job(job_id: int, job_update: MaintenanceJobUpdate, db: AsyncSession = Depends(get_session)):
    """Update a maintenance job"""
    return await crud_workshop.update_maintenance_job(db, job_id, job_update)


@router.delete("/jobs/{job_id}")
async def delete_maintenance_job(job_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a maintenance job"""
    return await crud_workshop.delete_maintenance_job(db, job_id)


# Supplier Endpoints
@router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """Get all suppliers"""
    suppliers = await crud_workshop.get_suppliers(db, skip=skip, limit=limit)
    return suppliers


@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(supplier: SupplierCreate, db: AsyncSession = Depends(get_session)):
    """Create a new supplier"""
    return await crud_workshop.create_supplier(db, supplier)


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: int, db: AsyncSession = Depends(get_session)):
    """Get a supplier by ID"""
    return await crud_workshop.get_supplier(db, supplier_id)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: int, supplier_update: SupplierUpdate, db: AsyncSession = Depends(get_session)):
    """Update a supplier"""
    return await crud_workshop.update_supplier(db, supplier_id, supplier_update)


@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a supplier"""
    return await crud_workshop.delete_supplier(db, supplier_id)


# StoreItem Endpoints
@router.get("/store-items", response_model=List[StoreItemResponse])
async def list_store_items(
    skip: int = 0,
    limit: int = 100,
    low_stock: bool = Query(False, description="Filter for items at or below reorder level"),
    db: AsyncSession = Depends(get_session)
):
    """Get all store items, optionally filter for low stock"""
    items = await crud_workshop.get_store_items(db, skip=skip, limit=limit, low_stock=low_stock)
    return items


@router.post("/store-items", response_model=StoreItemResponse)
async def create_store_item(item: StoreItemCreate, db: AsyncSession = Depends(get_session)):
    """Create a new store item"""
    return await crud_workshop.create_store_item(db, item)


@router.get("/store-items/{item_id}", response_model=StoreItemResponse)
async def get_store_item(item_id: int, db: AsyncSession = Depends(get_session)):
    """Get a store item by ID"""
    return await crud_workshop.get_store_item(db, item_id)


@router.put("/store-items/{item_id}", response_model=StoreItemResponse)
async def update_store_item(item_id: int, item_update: StoreItemUpdate, db: AsyncSession = Depends(get_session)):
    """Update a store item"""
    return await crud_workshop.update_store_item(db, item_id, item_update)


@router.delete("/store-items/{item_id}")
async def delete_store_item(item_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a store item"""
    return await crud_workshop.delete_store_item(db, item_id)


# PurchaseOrder Endpoints
@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by PO status"),
    db: AsyncSession = Depends(get_session)
):
    """Get all purchase orders with optional status filter"""
    pos = await crud_workshop.get_purchase_orders(db, skip=skip, limit=limit, status=status)
    return pos


@router.post("/purchase-orders", response_model=PurchaseOrderResponse)
async def create_purchase_order(po: PurchaseOrderCreate, db: AsyncSession = Depends(get_session)):
    """Create a new purchase order"""
    return await crud_workshop.create_purchase_order(db, po)


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(po_id: int, db: AsyncSession = Depends(get_session)):
    """Get a purchase order by ID"""
    return await crud_workshop.get_purchase_order(db, po_id)


@router.put("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(po_id: int, po_update: PurchaseOrderUpdate, db: AsyncSession = Depends(get_session)):
    """Update a purchase order"""
    return await crud_workshop.update_purchase_order(db, po_id, po_update)


@router.delete("/purchase-orders/{po_id}")
async def delete_purchase_order(po_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a purchase order"""
    return await crud_workshop.delete_purchase_order(db, po_id)


# PurchaseOrderItem Endpoints
@router.post("/purchase-order-items", response_model=PurchaseOrderItemResponse)
async def create_purchase_order_item(po_item: PurchaseOrderItemCreate, db: AsyncSession = Depends(get_session)):
    """Create a new purchase order item"""
    return await crud_workshop.create_purchase_order_item(db, po_item)


@router.put("/purchase-order-items/{po_item_id}/receive", response_model=PurchaseOrderItemResponse)
async def receive_purchase_order_item(
    po_item_id: int,
    quantity_received: int = Query(..., description="Quantity received"),
    performed_by: Optional[int] = Query(None, description="Employee ID who received the items"),
    db: AsyncSession = Depends(get_session)
):
    """Receive items from purchase order and update stock"""
    return await crud_workshop.receive_purchase_order_item(db, po_item_id, quantity_received, performed_by)


# StockMovement Endpoints
@router.get("/stock-movements", response_model=List[StockMovementResponse])
async def list_stock_movements(
    item_id: Optional[int] = Query(None, description="Filter by item ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """Get stock movements, optionally filtered by item"""
    movements = await crud_workshop.get_stock_movements(db, item_id=item_id, skip=skip, limit=limit)
    return movements


@router.post("/stock-movements", response_model=StockMovementResponse)
async def create_stock_movement(movement: StockMovementCreate, db: AsyncSession = Depends(get_session)):
    """Create a stock movement and adjust stock"""
    return await crud_workshop.create_stock_movement(db, movement)


# JobCardPart Endpoints
@router.post("/job-card-parts", response_model=JobCardPartResponse)
async def add_part_to_job_card(job_card_part: JobCardPartCreate, db: AsyncSession = Depends(get_session)):
    """Add a part to a job card and deduct from stock"""
    return await crud_workshop.add_part_to_job_card(db, job_card_part)


@router.get("/jobs/{job_card_id}/parts", response_model=List[JobCardPartResponse])
async def get_job_card_parts(job_card_id: int, db: AsyncSession = Depends(get_session)):
    """Get all parts used in a job card"""
    return await crud_workshop.get_job_card_parts(db, job_card_id)
