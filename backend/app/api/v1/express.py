from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import express as crud_express
from app.schemas.express import (
    BusCreate, BusUpdate, BusResponse,
    RouteCreate, RouteUpdate, RouteResponse,
    BookingCreate, BookingUpdate, BookingResponse,
    ParcelBookingCreate, ParcelBookingUpdate, ParcelBookingResponse,
    SeatMapCreate, SeatMapUpdate, SeatMapResponse
)
from typing import List, Optional
from datetime import datetime

router = APIRouter()


# Bus Endpoints
@router.get("/buses", response_model=List[BusResponse])
async def list_buses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """Get all buses"""
    buses = await crud_express.get_buses(db, skip=skip, limit=limit)
    return buses


@router.post("/buses", response_model=BusResponse)
async def create_bus(bus: BusCreate, db: AsyncSession = Depends(get_session)):
    """Create a new bus"""
    return await crud_express.create_bus(db, bus)


@router.get("/buses/{bus_id}", response_model=BusResponse)
async def get_bus(bus_id: int, db: AsyncSession = Depends(get_session)):
    """Get a bus by ID"""
    return await crud_express.get_bus(db, bus_id)


@router.put("/buses/{bus_id}", response_model=BusResponse)
async def update_bus(bus_id: int, bus_update: BusUpdate, db: AsyncSession = Depends(get_session)):
    """Update a bus"""
    return await crud_express.update_bus(db, bus_id, bus_update)


@router.delete("/buses/{bus_id}")
async def delete_bus(bus_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a bus"""
    return await crud_express.delete_bus(db, bus_id)


# Route Endpoints
@router.get("/routes", response_model=List[RouteResponse])
async def list_routes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """Get all routes"""
    routes = await crud_express.get_routes(db, skip=skip, limit=limit)
    return routes


@router.post("/routes", response_model=RouteResponse)
async def create_route(route: RouteCreate, db: AsyncSession = Depends(get_session)):
    """Create a new route"""
    return await crud_express.create_route(db, route)


@router.get("/routes/{route_id}", response_model=RouteResponse)
async def get_route(route_id: int, db: AsyncSession = Depends(get_session)):
    """Get a route by ID"""
    return await crud_express.get_route(db, route_id)


@router.put("/routes/{route_id}", response_model=RouteResponse)
async def update_route(route_id: int, route_update: RouteUpdate, db: AsyncSession = Depends(get_session)):
    """Update a route"""
    return await crud_express.update_route(db, route_id, route_update)


@router.delete("/routes/{route_id}")
async def delete_route(route_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a route"""
    return await crud_express.delete_route(db, route_id)


# Booking Endpoints (Passenger)
@router.get("/bookings", response_model=List[BookingResponse])
async def list_bookings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by booking status"),
    db: AsyncSession = Depends(get_session)
):
    """Get all bookings with optional status filter"""
    bookings = await crud_express.get_bookings(db, skip=skip, limit=limit, status=status)
    return bookings


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_session)):
    """Create a new booking (checks seat availability)"""
    return await crud_express.create_booking(db, booking)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_session)):
    """Get a booking by ID"""
    return await crud_express.get_booking(db, booking_id)


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: int, booking_update: BookingUpdate, db: AsyncSession = Depends(get_session)):
    """Update a booking"""
    return await crud_express.update_booking(db, booking_id, booking_update)


@router.put("/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(booking_id: int, db: AsyncSession = Depends(get_session)):
    """Cancel a booking"""
    return await crud_express.cancel_booking(db, booking_id)


# Parcel Booking Endpoints
@router.get("/parcel-bookings", response_model=List[ParcelBookingResponse])
async def list_parcel_bookings(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by booking status"),
    db: AsyncSession = Depends(get_session)
):
    """Get all parcel bookings with optional status filter"""
    parcel_bookings = await crud_express.get_parcel_bookings(db, skip=skip, limit=limit, status=status)
    return parcel_bookings


@router.post("/parcel-bookings", response_model=ParcelBookingResponse)
async def create_parcel_booking(parcel_booking: ParcelBookingCreate, db: AsyncSession = Depends(get_session)):
    """Create a new parcel booking"""
    return await crud_express.create_parcel_booking(db, parcel_booking)


@router.get("/parcel-bookings/{parcel_booking_id}", response_model=ParcelBookingResponse)
async def get_parcel_booking(parcel_booking_id: int, db: AsyncSession = Depends(get_session)):
    """Get a parcel booking by ID"""
    return await crud_express.get_parcel_booking(db, parcel_booking_id)


@router.put("/parcel-bookings/{parcel_booking_id}", response_model=ParcelBookingResponse)
async def update_parcel_booking(
    parcel_booking_id: int,
    parcel_booking_update: ParcelBookingUpdate,
    db: AsyncSession = Depends(get_session)
):
    """Update a parcel booking"""
    return await crud_express.update_parcel_booking(db, parcel_booking_id, parcel_booking_update)


@router.put("/parcel-bookings/{parcel_booking_id}/cancel", response_model=ParcelBookingResponse)
async def cancel_parcel_booking(parcel_booking_id: int, db: AsyncSession = Depends(get_session)):
    """Cancel a parcel booking"""
    return await crud_express.cancel_parcel_booking(db, parcel_booking_id)


# Seat Map Endpoints
@router.get("/seat-maps", response_model=List[SeatMapResponse])
async def list_seat_maps(
    bus_id: Optional[int] = Query(None, description="Filter by bus ID"),
    db: AsyncSession = Depends(get_session)
):
    """Get seat maps, optionally filtered by bus"""
    seat_maps = await crud_express.get_seat_maps(db, bus_id=bus_id)
    return seat_maps


@router.post("/seat-maps", response_model=SeatMapResponse)
async def create_seat_map(seat_map: SeatMapCreate, db: AsyncSession = Depends(get_session)):
    """Create a new seat map entry"""
    return await crud_express.create_seat_map(db, seat_map)


@router.put("/seat-maps/{seat_map_id}", response_model=SeatMapResponse)
async def update_seat_map(seat_map_id: int, seat_map_update: SeatMapUpdate, db: AsyncSession = Depends(get_session)):
    """Update a seat map entry"""
    return await crud_express.update_seat_map(db, seat_map_id, seat_map_update)


@router.get("/buses/{bus_id}/available-seats", response_model=List[SeatMapResponse])
async def get_available_seats(
    bus_id: int,
    travel_date: datetime = Query(..., description="Travel date to check availability"),
    db: AsyncSession = Depends(get_session)
):
    """Get all available seats for a bus on a specific travel date"""
    return await crud_express.get_available_seats(db, bus_id, travel_date)
