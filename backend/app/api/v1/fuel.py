from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import fuel as crud_fuel
from app.schemas.fuel import (
    FuelStationCreate, FuelStationUpdate, FuelStationResponse,
    FuelLogCreate, FuelLogUpdate, FuelLogResponse
)
from typing import List, Optional
from datetime import datetime
from app.core.error_handler import get_error_handler

router = APIRouter()
error_handler = get_error_handler("fuel")


# FuelStation Endpoints
@router.get("/stations", response_model=List[FuelStationResponse])
async def list_fuel_stations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """Get all fuel stations"""
    stations = await crud_fuel.get_fuel_stations(db, skip=skip, limit=limit)
    return stations


@router.post("/stations", response_model=FuelStationResponse)
async def create_fuel_station(station: FuelStationCreate, db: AsyncSession = Depends(get_session)):
    """Create a new fuel station"""
    return await crud_fuel.create_fuel_station(db, station)


@router.get("/stations/{station_id}", response_model=FuelStationResponse)
async def get_fuel_station(station_id: int, db: AsyncSession = Depends(get_session)):
    """Get a fuel station by ID"""
    return await crud_fuel.get_fuel_station(db, station_id)


@router.put("/stations/{station_id}", response_model=FuelStationResponse)
async def update_fuel_station(station_id: int, station_update: FuelStationUpdate, db: AsyncSession = Depends(get_session)):
    """Update a fuel station"""
    return await crud_fuel.update_fuel_station(db, station_id, station_update)


@router.delete("/stations/{station_id}")
async def delete_fuel_station(station_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a fuel station"""
    return await crud_fuel.delete_fuel_station(db, station_id)


# FuelLog Endpoints
@router.get("/logs", response_model=List[FuelLogResponse])
async def list_fuel_logs(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = Query(None, description="Filter by vehicle ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: AsyncSession = Depends(get_session)
):
    """Get all fuel logs with optional filters"""
    try:
        logs = await crud_fuel.get_fuel_logs(
            db,
            skip=skip,
            limit=limit,
            vehicle_id=vehicle_id,
            start_date=start_date,
            end_date=end_date,
        )
        return logs
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/logs", method="GET")
        raise


@router.post("/logs", response_model=FuelLogResponse)
async def create_fuel_log(fuel_log: FuelLogCreate, db: AsyncSession = Depends(get_session)):
    """Create a new fuel log"""
    return await crud_fuel.create_fuel_log(db, fuel_log)


@router.get("/logs/{log_id}", response_model=FuelLogResponse)
async def get_fuel_log(log_id: int, db: AsyncSession = Depends(get_session)):
    """Get a fuel log by ID"""
    return await crud_fuel.get_fuel_log(db, log_id)


@router.put("/logs/{log_id}", response_model=FuelLogResponse)
async def update_fuel_log(log_id: int, fuel_log_update: FuelLogUpdate, db: AsyncSession = Depends(get_session)):
    """Update a fuel log"""
    return await crud_fuel.update_fuel_log(db, log_id, fuel_log_update)


@router.delete("/logs/{log_id}")
async def delete_fuel_log(log_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a fuel log"""
    return await crud_fuel.delete_fuel_log(db, log_id)


# Analytics Endpoints
@router.get("/analytics/vehicle/{vehicle_id}")
async def get_vehicle_fuel_consumption(
    vehicle_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_session)
):
    """Get fuel consumption statistics for a vehicle"""
    return await crud_fuel.get_vehicle_fuel_consumption(db, vehicle_id, days)


@router.get("/analytics/summary")
async def get_fuel_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for summary"),
    end_date: Optional[datetime] = Query(None, description="End date for summary"),
    db: AsyncSession = Depends(get_session)
):
    """Get overall fuel consumption summary"""
    return await crud_fuel.get_fuel_summary(db, start_date, end_date)