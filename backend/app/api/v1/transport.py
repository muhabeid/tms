from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_session
from app.schemas.transport import (
    TruckCreate, TruckResponse, TruckUpdate,
    DeliveryNoteCreate, DeliveryNoteResponse, DeliveryNoteUpdate,
    TripCreate, TripResponse, TripUpdate
)
from app.crud import transport as crud_transport
from app.core.error_handler import get_error_handler

router = APIRouter()
error_handler = get_error_handler("transport")

# Truck Endpoints
@router.get("/trucks", response_model=List[TruckResponse])
async def list_trucks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """List all trucks"""
    try:
        trucks = await crud_transport.get_trucks(db, skip=skip, limit=limit)
        return trucks
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/trucks", method="GET")
        raise


@router.post("/trucks", response_model=TruckResponse)
async def create_truck(truck: TruckCreate, db: AsyncSession = Depends(get_session)):
    """Create a new truck"""
    try:
        result = await crud_transport.create_truck(db, truck)
        return result
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/trucks", method="POST", request_data=truck.dict() if hasattr(truck, 'dict') else str(truck))
        raise


@router.get("/trucks/{truck_id}", response_model=TruckResponse)
async def get_truck(truck_id: int, db: AsyncSession = Depends(get_session)):
    """Get truck details"""
    truck = await crud_transport.get_truck(db, truck_id)
    if truck is None:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.put("/trucks/{truck_id}", response_model=TruckResponse)
async def update_truck(truck_id: int, truck_update: TruckUpdate, db: AsyncSession = Depends(get_session)):
    """Update truck details"""
    truck = await crud_transport.update_truck(db, truck_id, truck_update)
    if truck is None:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.delete("/trucks/{truck_id}", response_model=TruckResponse)
async def delete_truck(truck_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a truck"""
    truck = await crud_transport.delete_truck(db, truck_id)
    if truck is None:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.get("/trucks/{truck_id}/active-delivery", response_model=Optional[DeliveryNoteResponse])
async def get_truck_active_delivery(truck_id: int, db: AsyncSession = Depends(get_session)):
    """Get active delivery for a truck"""
    delivery = await crud_transport.get_active_delivery(db, truck_id)
    return delivery


# Delivery Note Endpoints
@router.get("/deliveries", response_model=List[DeliveryNoteResponse])
async def list_deliveries(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status: ACTIVE, COMPLETED, CANCELLED"),
    category: Optional[str] = Query(None, description="Filter by category: LOCAL, IMPORT, EXPORT"),
    db: AsyncSession = Depends(get_session)
):
    """List all deliveries with optional filters"""
    deliveries = await crud_transport.get_deliveries(db, skip=skip, limit=limit, status=status, category=category)
    return deliveries


@router.post("/deliveries", response_model=DeliveryNoteResponse)
async def create_delivery(delivery: DeliveryNoteCreate, db: AsyncSession = Depends(get_session)):
    """
    Create a new delivery note.
    Business Rule: Only one active delivery per truck per cargo category.
    """
    try:
        return await crud_transport.create_delivery(db, delivery)
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/deliveries", method="POST", request_data=delivery.dict() if hasattr(delivery, 'dict') else str(delivery))
        raise


@router.get("/deliveries/{delivery_id}", response_model=DeliveryNoteResponse)
async def get_delivery(delivery_id: int, db: AsyncSession = Depends(get_session)):
    """Get delivery details"""
    delivery = await crud_transport.get_delivery(db, delivery_id)
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.put("/deliveries/{delivery_id}", response_model=DeliveryNoteResponse)
async def update_delivery(delivery_id: int, delivery_update: DeliveryNoteUpdate, db: AsyncSession = Depends(get_session)):
    """Update delivery details"""
    delivery = await crud_transport.update_delivery(db, delivery_id, delivery_update)
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@router.put("/deliveries/{delivery_id}/complete", response_model=DeliveryNoteResponse)
async def complete_delivery(delivery_id: int, db: AsyncSession = Depends(get_session)):
    """Mark a delivery as completed"""
    delivery = await crud_transport.complete_delivery(db, delivery_id)
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


# Trip Endpoints
@router.get("/trips", response_model=List[TripResponse])
async def list_trips(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """List all trips"""
    try:
        trips = await crud_transport.get_trips(db, skip=skip, limit=limit)
        return trips
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/trips", method="GET")
        raise


@router.post("/trips", response_model=TripResponse)
async def create_trip(trip: TripCreate, db: AsyncSession = Depends(get_session)):
    """Create a new trip (usually auto-created with delivery)"""
    try:
        return await crud_transport.create_trip(db, trip)
    except Exception as e:
        error_handler.log_api_error(e, endpoint="/trips", method="POST", request_data=trip.dict() if hasattr(trip, 'dict') else str(trip))
        raise


@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int, db: AsyncSession = Depends(get_session)):
    """Get trip details"""
    trip = await crud_transport.get_trip(db, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.put("/trips/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: int, trip_update: TripUpdate, db: AsyncSession = Depends(get_session)):
    """Update trip details (fuel consumption, costs, etc.)"""
    trip = await crud_transport.update_trip(db, trip_id, trip_update)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
