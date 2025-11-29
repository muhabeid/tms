from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, text
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.transport import Truck, DeliveryNote, Trip, DeliveryStatus, CargoCategory
from app.models.finance import Transaction, TransactionType, TransactionStatus
from app.models.hr import Driver  # Ensure Driver is registered for relationships
from app.schemas.transport import (
    TruckCreate, TruckUpdate,
    DeliveryNoteCreate, DeliveryNoteUpdate,
    TripCreate, TripUpdate
)
from datetime import datetime


# Truck CRUD
async def get_trucks(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Truck).offset(skip).limit(limit))
    return result.scalars().all()


async def create_truck(db: AsyncSession, truck: TruckCreate):
    db_truck = Truck(**truck.dict())
    db.add(db_truck)
    await db.commit()
    await db.refresh(db_truck)
    return db_truck


async def get_truck(db: AsyncSession, truck_id: int):
    result = await db.execute(select(Truck).filter(Truck.id == truck_id))
    return result.scalar_one_or_none()


async def update_truck(db: AsyncSession, truck_id: int, truck_update: TruckUpdate):
    db_truck = await get_truck(db, truck_id)
    if not db_truck:
        return None
    
    update_data = truck_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_truck, key, value)
    
    await db.commit()
    await db.refresh(db_truck)
    return db_truck


async def delete_truck(db: AsyncSession, truck_id: int):
    db_truck = await get_truck(db, truck_id)
    if not db_truck:
        return None
    
    await db.delete(db_truck)
    await db.commit()
    return db_truck


# Delivery Note CRUD
async def check_active_delivery(db: AsyncSession, truck_id: int, cargo_category: CargoCategory):
    """Check if truck has an active delivery for the given category"""
    result = await db.execute(
        select(DeliveryNote).filter(
            and_(
                DeliveryNote.truck_id == truck_id,
                DeliveryNote.cargo_category == cargo_category,
                DeliveryNote.status == DeliveryStatus.ACTIVE
            )
        )
    )
    return result.scalar_one_or_none()


async def get_deliveries(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = None, category: str = None):
    query = select(DeliveryNote)
    
    if status:
        query = query.filter(DeliveryNote.status == status)
    if category:
        query = query.filter(DeliveryNote.cargo_category == category)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_delivery(db: AsyncSession, delivery: DeliveryNoteCreate):
    truck = await get_truck(db, delivery.truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    from app.models.hr import Employee, EmployeeType, EmployeeStatus
    result = await db.execute(select(Employee).where(Employee.id == delivery.driver_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=400, detail="Driver not found")
    if employee.employee_type != EmployeeType.DRIVER:
        raise HTTPException(status_code=400, detail="Selected employee is not a DRIVER")
    if employee.status != EmployeeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Driver is not ACTIVE")

    # Business Rule: Check for active delivery with same category
    active_delivery = await check_active_delivery(db, delivery.truck_id, delivery.cargo_category)
    if active_delivery:
        raise HTTPException(
            status_code=400,
            detail=f"Truck already has an active {delivery.cargo_category} delivery (Delivery #{active_delivery.delivery_number}). Complete it before creating a new one."
        )
    
    # Generate delivery number
    result = await db.execute(select(DeliveryNote))
    all_deliveries = result.scalars().all()
    delivery_number = f"DN{len(all_deliveries) + 1:06d}"
    
    db_delivery = DeliveryNote(
        **delivery.dict(),
        delivery_number=delivery_number
    )
    db.add(db_delivery)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        message = str(e.orig) if getattr(e, "orig", None) else str(e)
        if "delivery_notes_driver_id_fkey" in message:
            raise HTTPException(status_code=400, detail="Invalid driver_id: driver record not found in drivers table")
        raise HTTPException(status_code=400, detail="Cannot create delivery due to data integrity constraints")
    await db.refresh(db_delivery)
    
    # Auto-create associated Trip
    db_trip = Trip(
        delivery_id=db_delivery.id,
        vehicle_id=delivery.truck_id
    )
    db.add(db_trip)
    await db.commit()
    await db.refresh(db_delivery)
    
    return db_delivery


async def get_delivery(db: AsyncSession, delivery_id: int):
    result = await db.execute(select(DeliveryNote).filter(DeliveryNote.id == delivery_id))
    return result.scalar_one_or_none()


async def get_active_delivery(db: AsyncSession, truck_id: int):
    """Get active delivery for a truck (any category)"""
    result = await db.execute(
        select(DeliveryNote).filter(
            and_(
                DeliveryNote.truck_id == truck_id,
                DeliveryNote.status == DeliveryStatus.ACTIVE
            )
        )
    )
    return result.scalar_one_or_none()


async def update_delivery(db: AsyncSession, delivery_id: int, delivery_update: DeliveryNoteUpdate):
    db_delivery = await get_delivery(db, delivery_id)
    if not db_delivery:
        return None
    
    update_data = delivery_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_delivery, key, value)
    
    await db.commit()
    await db.refresh(db_delivery)
    return db_delivery


async def complete_delivery(db: AsyncSession, delivery_id: int):
    """Mark delivery as completed"""
    db_delivery = await get_delivery(db, delivery_id)
    if not db_delivery:
        return None
    
    db_delivery.status = DeliveryStatus.COMPLETED
    db_delivery.completion_date = datetime.utcnow()
    
    amount = 0.0
    if db_delivery.tonnage:
        amount += float(db_delivery.tonnage) * 100.0
    if db_delivery.distance:
        amount += float(db_delivery.distance) * 10.0
    description = f"Delivery {db_delivery.delivery_number} completed for {db_delivery.client_name}"
    tx = Transaction(
        transaction_type=TransactionType.REVENUE,
        category="TRANSPORT",
        amount=amount if amount > 0 else 2500.0,
        related_entity_type="delivery",
        related_entity_id=db_delivery.id,
        status=TransactionStatus.COMPLETED,
        description=description,
        reference_number=f"DEL-{db_delivery.delivery_number}"
    )
    db.add(tx)
    
    await db.commit()
    await db.refresh(db_delivery)
    return db_delivery


# Trip CRUD
async def get_trips(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Trip).offset(skip).limit(limit))
    return result.scalars().all()


async def create_trip(db: AsyncSession, trip: TripCreate):
    db_trip = Trip(**trip.dict())
    db.add(db_trip)
    await db.commit()
    await db.refresh(db_trip)
    return db_trip


async def get_trip(db: AsyncSession, trip_id: int):
    result = await db.execute(select(Trip).filter(Trip.id == trip_id))
    return result.scalar_one_or_none()


async def update_trip(db: AsyncSession, trip_id: int, trip_update: TripUpdate):
    db_trip = await get_trip(db, trip_id)
    if not db_trip:
        return None
    
    update_data = trip_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trip, key, value)
    
    await db.commit()
    await db.refresh(db_trip)
    return db_trip
