from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from fastapi import HTTPException
from app.models.fuel import FuelStation, FuelLog
from app.models.finance import Transaction, TransactionType, TransactionStatus
from app.models.transport import Trip, Truck
from app.schemas.fuel import (
    FuelStationCreate, FuelStationUpdate,
    FuelLogCreate, FuelLogUpdate
)
from datetime import datetime, timedelta


# FuelStation CRUD
async def get_fuel_stations(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all fuel stations"""
    result = await db.execute(select(FuelStation).offset(skip).limit(limit))
    return result.scalars().all()


async def create_fuel_station(db: AsyncSession, station: FuelStationCreate):
    """Create a new fuel station"""
    db_station = FuelStation(**station.model_dump())
    db.add(db_station)
    await db.commit()
    await db.refresh(db_station)
    return db_station


async def get_fuel_station(db: AsyncSession, station_id: int):
    """Get a fuel station by ID"""
    result = await db.execute(select(FuelStation).where(FuelStation.id == station_id))
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail="Fuel station not found")
    return station


async def update_fuel_station(db: AsyncSession, station_id: int, station_update: FuelStationUpdate):
    """Update a fuel station"""
    db_station = await get_fuel_station(db, station_id)
    update_data = station_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_station, field, value)
    await db.commit()
    await db.refresh(db_station)
    return db_station


async def delete_fuel_station(db: AsyncSession, station_id: int):
    """Delete a fuel station"""
    db_station = await get_fuel_station(db, station_id)
    await db.delete(db_station)
    await db.commit()
    return {"message": "Fuel station deleted successfully"}


# FuelLog CRUD
async def get_fuel_logs(db: AsyncSession, skip: int = 0, limit: int = 100, 
                        vehicle_id: int = None, start_date: datetime = None, end_date: datetime = None):
    """Get all fuel logs with optional filters"""
    query = select(FuelLog)
    
    if vehicle_id:
        query = query.where(FuelLog.vehicle_id == vehicle_id)
    if start_date:
        query = query.where(FuelLog.date_time >= start_date)
    if end_date:
        query = query.where(FuelLog.date_time <= end_date)
    
    result = await db.execute(query.offset(skip).limit(limit).order_by(FuelLog.date_time.desc()))
    return result.scalars().all()


async def create_fuel_log(db: AsyncSession, fuel_log: FuelLogCreate):
    """Create a new fuel log"""
    db_fuel_log = FuelLog(**fuel_log.model_dump())
    db.add(db_fuel_log)
    await db.commit()
    await db.refresh(db_fuel_log)

    try:
        if db_fuel_log.total_cost is not None:
            description = (
                f"Fuel purchase for vehicle {db_fuel_log.vehicle_id}:"
                f" {db_fuel_log.litres} litres at station {db_fuel_log.fuel_station_id}"
            )
            tx = Transaction(
                transaction_type=TransactionType.EXPENSE,
                category="Fuel",
                amount=float(db_fuel_log.total_cost),
                related_entity_type="trip" if db_fuel_log.trip_id else "fuel_log",
                related_entity_id=db_fuel_log.trip_id if db_fuel_log.trip_id else db_fuel_log.id,
                payment_method=None,
                status=TransactionStatus.COMPLETED,
                description=description,
                receipt_number=db_fuel_log.receipt_number,
                reference_number=f"FUEL-{db_fuel_log.id}"
            )
            db.add(tx)

        if db_fuel_log.trip_id:
            result = await db.execute(select(Trip).where(Trip.id == db_fuel_log.trip_id))
            trip = result.scalar_one_or_none()
            if trip:
                trip.fuel_consumed = (trip.fuel_consumed or 0.0) + float(db_fuel_log.litres or 0.0)
                if db_fuel_log.total_cost is not None:
                    trip.actual_cost = (trip.actual_cost or 0.0) + float(db_fuel_log.total_cost)

        if db_fuel_log.vehicle_id and db_fuel_log.odometer_reading is not None:
            result = await db.execute(select(Truck).where(Truck.id == db_fuel_log.vehicle_id))
            truck = result.scalar_one_or_none()
            if truck:
                truck.mileage = float(db_fuel_log.odometer_reading)

        await db.commit()
    except Exception:
        await db.rollback()

    return db_fuel_log


async def get_fuel_log(db: AsyncSession, log_id: int):
    """Get a fuel log by ID"""
    result = await db.execute(select(FuelLog).where(FuelLog.id == log_id))
    fuel_log = result.scalar_one_or_none()
    if not fuel_log:
        raise HTTPException(status_code=404, detail="Fuel log not found")
    return fuel_log


async def update_fuel_log(db: AsyncSession, log_id: int, fuel_log_update: FuelLogUpdate):
    """Update a fuel log"""
    db_fuel_log = await get_fuel_log(db, log_id)
    update_data = fuel_log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fuel_log, field, value)
    await db.commit()
    await db.refresh(db_fuel_log)
    return db_fuel_log


async def delete_fuel_log(db: AsyncSession, log_id: int):
    """Delete a fuel log"""
    db_fuel_log = await get_fuel_log(db, log_id)
    await db.delete(db_fuel_log)
    await db.commit()
    return {"message": "Fuel log deleted successfully"}


# Analytics Functions
async def get_vehicle_fuel_consumption(db: AsyncSession, vehicle_id: int, days: int = 30):
    """Get fuel consumption statistics for a vehicle"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            func.sum(FuelLog.litres).label('total_litres'),
            func.sum(FuelLog.total_cost).label('total_cost'),
            func.avg(FuelLog.cost_per_litre).label('avg_cost_per_litre'),
            func.count(FuelLog.id).label('fill_count')
        ).where(
            and_(
                FuelLog.vehicle_id == vehicle_id,
                FuelLog.date_time >= start_date
            )
        )
    )
    
    stats = result.one()
    return {
        "vehicle_id": vehicle_id,
        "period_days": days,
        "total_litres": float(stats.total_litres) if stats.total_litres else 0,
        "total_cost": float(stats.total_cost) if stats.total_cost else 0,
        "avg_cost_per_litre": float(stats.avg_cost_per_litre) if stats.avg_cost_per_litre else 0,
        "fill_count": stats.fill_count
    }


async def get_fuel_summary(db: AsyncSession, start_date: datetime = None, end_date: datetime = None):
    """Get overall fuel consumption summary"""
    query = select(
        func.sum(FuelLog.litres).label('total_litres'),
        func.sum(FuelLog.total_cost).label('total_cost'),
        func.avg(FuelLog.cost_per_litre).label('avg_cost_per_litre'),
        func.count(func.distinct(FuelLog.vehicle_id)).label('vehicle_count')
    )
    
    if start_date:
        query = query.where(FuelLog.date_time >= start_date)
    if end_date:
        query = query.where(FuelLog.date_time <= end_date)
    
    result = await db.execute(query)
    stats = result.one()
    
    return {
        "total_litres": float(stats.total_litres) if stats.total_litres else 0,
        "total_cost": float(stats.total_cost) if stats.total_cost else 0,
        "avg_cost_per_litre": float(stats.avg_cost_per_litre) if stats.avg_cost_per_litre else 0,
        "vehicle_count": stats.vehicle_count
    }
