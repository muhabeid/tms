from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


# Bus Schemas
class BusBase(BaseModel):
    plate_number: str
    model: str
    year: Optional[int] = None
    capacity: int
    mileage: Optional[float] = 0.0
    status: Optional[str] = "AVAILABLE"
    total_seats: int
    seat_layout_json: Optional[str] = None


class BusCreate(BusBase):
    pass


class BusUpdate(BaseModel):
    plate_number: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity: Optional[int] = None
    mileage: Optional[float] = None
    status: Optional[str] = None
    total_seats: Optional[int] = None
    seat_layout_json: Optional[str] = None


class BusResponse(BusBase):
    id: int

    model_config = {"from_attributes": True}


# Route Schemas
class RouteBase(BaseModel):
    name: str
    origin: str
    destination: str
    distance: Optional[float] = None
    duration: Optional[int] = None
    schedule: Optional[str] = None
    fare: float


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    schedule: Optional[str] = None
    fare: Optional[float] = None


class RouteResponse(RouteBase):
    id: int

    model_config = {"from_attributes": True}


# Booking Schemas (Passenger)
class BookingBase(BaseModel):
    route_id: int
    bus_id: int
    passenger_name: str
    passenger_contact: str
    seat_number: str
    fare: float
    travel_date: datetime
    status: Optional[BookingStatus] = BookingStatus.PENDING


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    passenger_name: Optional[str] = None
    passenger_contact: Optional[str] = None
    seat_number: Optional[str] = None
    fare: Optional[float] = None
    travel_date: Optional[datetime] = None
    status: Optional[BookingStatus] = None


class BookingResponse(BookingBase):
    id: int
    booking_date: datetime

    model_config = {"from_attributes": True}


# ParcelBooking Schemas
class ParcelBookingBase(BaseModel):
    route_id: int
    bus_id: int
    sender_name: str
    sender_contact: str
    receiver_name: str
    receiver_contact: str
    parcel_description: str
    weight: float
    origin: str
    destination: str
    fare: float
    status: Optional[BookingStatus] = BookingStatus.PENDING


class ParcelBookingCreate(ParcelBookingBase):
    pass


class ParcelBookingUpdate(BaseModel):
    sender_name: Optional[str] = None
    sender_contact: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_contact: Optional[str] = None
    parcel_description: Optional[str] = None
    weight: Optional[float] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    fare: Optional[float] = None
    status: Optional[BookingStatus] = None


class ParcelBookingResponse(ParcelBookingBase):
    id: int
    booking_date: datetime

    model_config = {"from_attributes": True}


# SeatMap Schemas
class SeatMapBase(BaseModel):
    bus_id: int
    seat_number: str
    row: int
    column: int
    is_available: Optional[bool] = True


class SeatMapCreate(SeatMapBase):
    pass


class SeatMapUpdate(BaseModel):
    seat_number: Optional[str] = None
    row: Optional[int] = None
    column: Optional[int] = None
    is_available: Optional[bool] = None


class SeatMapResponse(SeatMapBase):
    id: int

    model_config = {"from_attributes": True}
