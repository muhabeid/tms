from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from fastapi import HTTPException
from app.models.express import Bus, Route, Booking, ParcelBooking, SeatMap, BookingStatus
from app.schemas.express import (
    BusCreate, BusUpdate,
    RouteCreate, RouteUpdate,
    BookingCreate, BookingUpdate,
    ParcelBookingCreate, ParcelBookingUpdate,
    SeatMapCreate, SeatMapUpdate
)
from datetime import datetime


# Bus CRUD
async def get_buses(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all buses"""
    result = await db.execute(select(Bus).offset(skip).limit(limit))
    return result.scalars().all()


async def create_bus(db: AsyncSession, bus: BusCreate):
    """Create a new bus"""
    db_bus = Bus(**bus.model_dump())
    db.add(db_bus)
    await db.commit()
    await db.refresh(db_bus)
    return db_bus


async def get_bus(db: AsyncSession, bus_id: int):
    """Get a bus by ID"""
    result = await db.execute(select(Bus).where(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    return bus


async def update_bus(db: AsyncSession, bus_id: int, bus_update: BusUpdate):
    """Update a bus"""
    db_bus = await get_bus(db, bus_id)
    update_data = bus_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_bus, field, value)
    await db.commit()
    await db.refresh(db_bus)
    return db_bus


async def delete_bus(db: AsyncSession, bus_id: int):
    """Delete a bus"""
    db_bus = await get_bus(db, bus_id)
    await db.delete(db_bus)
    await db.commit()
    return {"message": "Bus deleted successfully"}


# Route CRUD
async def get_routes(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Get all routes"""
    result = await db.execute(select(Route).offset(skip).limit(limit))
    return result.scalars().all()


async def create_route(db: AsyncSession, route: RouteCreate):
    """Create a new route"""
    db_route = Route(**route.model_dump())
    db.add(db_route)
    await db.commit()
    await db.refresh(db_route)
    return db_route


async def get_route(db: AsyncSession, route_id: int):
    """Get a route by ID"""
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


async def update_route(db: AsyncSession, route_id: int, route_update: RouteUpdate):
    """Update a route"""
    db_route = await get_route(db, route_id)
    update_data = route_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_route, field, value)
    await db.commit()
    await db.refresh(db_route)
    return db_route


async def delete_route(db: AsyncSession, route_id: int):
    """Delete a route"""
    db_route = await get_route(db, route_id)
    await db.delete(db_route)
    await db.commit()
    return {"message": "Route deleted successfully"}


# Booking CRUD (Passenger)
async def check_seat_availability(db: AsyncSession, bus_id: int, seat_number: str, travel_date: datetime):
    """Check if a seat is available for a specific bus and travel date"""
    result = await db.execute(
        select(Booking).where(
            and_(
                Booking.bus_id == bus_id,
                Booking.seat_number == seat_number,
                Booking.travel_date == travel_date,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        )
    )
    existing_booking = result.scalar_one_or_none()
    return existing_booking is None


async def get_bookings(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = None):
    """Get all bookings with optional status filter"""
    query = select(Booking)
    if status:
        query = query.where(Booking.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_booking(db: AsyncSession, booking: BookingCreate):
    """Create a new booking with seat availability check"""
    # Check seat availability
    is_available = await check_seat_availability(
        db, booking.bus_id, booking.seat_number, booking.travel_date
    )
    if not is_available:
        raise HTTPException(
            status_code=400,
            detail=f"Seat {booking.seat_number} is already booked for this date"
        )
    
    db_booking = Booking(**booking.model_dump())
    db.add(db_booking)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking


async def get_booking(db: AsyncSession, booking_id: int):
    """Get a booking by ID"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


async def update_booking(db: AsyncSession, booking_id: int, booking_update: BookingUpdate):
    """Update a booking"""
    db_booking = await get_booking(db, booking_id)
    update_data = booking_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_booking, field, value)
    await db.commit()
    await db.refresh(db_booking)
    return db_booking


async def cancel_booking(db: AsyncSession, booking_id: int):
    """Cancel a booking"""
    db_booking = await get_booking(db, booking_id)
    db_booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(db_booking)
    return db_booking


# ParcelBooking CRUD
async def get_parcel_bookings(db: AsyncSession, skip: int = 0, limit: int = 100, status: str = None):
    """Get all parcel bookings with optional status filter"""
    query = select(ParcelBooking)
    if status:
        query = query.where(ParcelBooking.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def create_parcel_booking(db: AsyncSession, parcel_booking: ParcelBookingCreate):
    """Create a new parcel booking"""
    db_parcel_booking = ParcelBooking(**parcel_booking.model_dump())
    db.add(db_parcel_booking)
    await db.commit()
    await db.refresh(db_parcel_booking)
    return db_parcel_booking


async def get_parcel_booking(db: AsyncSession, parcel_booking_id: int):
    """Get a parcel booking by ID"""
    result = await db.execute(select(ParcelBooking).where(ParcelBooking.id == parcel_booking_id))
    parcel_booking = result.scalar_one_or_none()
    if not parcel_booking:
        raise HTTPException(status_code=404, detail="Parcel booking not found")
    return parcel_booking


async def update_parcel_booking(db: AsyncSession, parcel_booking_id: int, parcel_booking_update: ParcelBookingUpdate):
    """Update a parcel booking"""
    db_parcel_booking = await get_parcel_booking(db, parcel_booking_id)
    update_data = parcel_booking_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_parcel_booking, field, value)
    await db.commit()
    await db.refresh(db_parcel_booking)
    return db_parcel_booking


async def cancel_parcel_booking(db: AsyncSession, parcel_booking_id: int):
    """Cancel a parcel booking"""
    db_parcel_booking = await get_parcel_booking(db, parcel_booking_id)
    db_parcel_booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(db_parcel_booking)
    return db_parcel_booking


# SeatMap CRUD
async def get_seat_maps(db: AsyncSession, bus_id: int = None):
    """Get seat maps, optionally filtered by bus"""
    query = select(SeatMap)
    if bus_id:
        query = query.where(SeatMap.bus_id == bus_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_seat_map(db: AsyncSession, seat_map: SeatMapCreate):
    """Create a new seat map entry"""
    db_seat_map = SeatMap(**seat_map.model_dump())
    db.add(db_seat_map)
    await db.commit()
    await db.refresh(db_seat_map)
    return db_seat_map


async def update_seat_map(db: AsyncSession, seat_map_id: int, seat_map_update: SeatMapUpdate):
    """Update a seat map entry"""
    result = await db.execute(select(SeatMap).where(SeatMap.id == seat_map_id))
    db_seat_map = result.scalar_one_or_none()
    if not db_seat_map:
        raise HTTPException(status_code=404, detail="Seat map not found")
    
    update_data = seat_map_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_seat_map, field, value)
    await db.commit()
    await db.refresh(db_seat_map)
    return db_seat_map


async def get_available_seats(db: AsyncSession, bus_id: int, travel_date: datetime):
    """Get all available seats for a bus on a specific travel date"""
    # Get all seats for the bus
    result = await db.execute(select(SeatMap).where(SeatMap.bus_id == bus_id))
    all_seats = result.scalars().all()
    
    # Get booked seats for the travel date
    booked_result = await db.execute(
        select(Booking.seat_number).where(
            and_(
                Booking.bus_id == bus_id,
                Booking.travel_date == travel_date,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        )
    )
    booked_seats = {row[0] for row in booked_result.all()}
    
    # Filter available seats
    available_seats = [
        seat for seat in all_seats
        if seat.is_available and seat.seat_number not in booked_seats
    ]
    
    return available_seats
