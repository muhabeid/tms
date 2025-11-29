from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class Bus(Base):
    __tablename__ = "buses"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False, index=True)
    model = Column(String, nullable=False)
    year = Column(Integer)
    capacity = Column(Integer, nullable=False)  # Total passenger capacity
    mileage = Column(Float, default=0.0)
    status = Column(String, default="AVAILABLE")  # AVAILABLE, IN_SERVICE, MAINTENANCE, INACTIVE
    total_seats = Column(Integer, nullable=False)
    seat_layout_json = Column(Text, nullable=True)  # JSON string for seat configuration
    
    # Relationships
    bookings = relationship("Booking", back_populates="bus")
    parcel_bookings = relationship("ParcelBooking", back_populates="bus")
    seat_maps = relationship("SeatMap", back_populates="bus", cascade="all, delete-orphan")


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance = Column(Float, nullable=True)  # in kilometers
    duration = Column(Integer, nullable=True)  # in minutes
    schedule = Column(String, nullable=True)  # e.g., "Daily 6:00 AM, 2:00 PM"
    fare = Column(Float, nullable=False)  # Base fare for passengers
    
    # Relationships
    bookings = relationship("Booking", back_populates="route")
    parcel_bookings = relationship("ParcelBooking", back_populates="route")


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class Booking(Base):
    """Passenger booking model"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Route and Bus
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    
    # Passenger Information
    passenger_name = Column(String, nullable=False)
    passenger_contact = Column(String, nullable=False)
    
    # Booking Details
    seat_number = Column(String, nullable=False)
    fare = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    travel_date = Column(DateTime, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Relationships
    route = relationship("Route", back_populates="bookings")
    bus = relationship("Bus", back_populates="bookings")


class ParcelBooking(Base):
    """Parcel/cargo booking model"""
    __tablename__ = "parcel_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Route and Bus
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    
    # Sender Information
    sender_name = Column(String, nullable=False)
    sender_contact = Column(String, nullable=False)
    
    # Receiver Information
    receiver_name = Column(String, nullable=False)
    receiver_contact = Column(String, nullable=False)
    
    # Parcel Details
    parcel_description = Column(String, nullable=False)
    weight = Column(Float, nullable=False)  # in kilograms
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    
    # Booking Details
    fare = Column(Float, nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Relationships
    route = relationship("Route", back_populates="parcel_bookings")
    bus = relationship("Bus", back_populates="parcel_bookings")


class SeatMap(Base):
    """Seat configuration for buses"""
    __tablename__ = "seat_maps"
    
    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    
    seat_number = Column(String, nullable=False)
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    bus = relationship("Bus", back_populates="seat_maps")
