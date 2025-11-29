from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum

class Truck(Base):
    __tablename__ = "trucks"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, nullable=False, index=True)
    model = Column(String, nullable=False)
    year = Column(Integer)
    mileage = Column(Float, default=0.0)
    status = Column(String, default="AVAILABLE")  # AVAILABLE, IN_USE, MAINTENANCE, INACTIVE
    current_location = Column(String, nullable=True)
    
    # Relationships
    deliveries = relationship("DeliveryNote", back_populates="truck")
    trips = relationship("Trip", back_populates="vehicle")


class CargoCategory(str, enum.Enum):
    LOCAL = "LOCAL"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"


class DeliveryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class DeliveryNote(Base):
    __tablename__ = "delivery_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_number = Column(String, unique=True, nullable=False, index=True)
    
    # Vehicle and Driver
    truck_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Cargo Details
    cargo_description = Column(String, nullable=False)
    cargo_category = Column(Enum(CargoCategory), nullable=False)
    tonnage = Column(Float, nullable=False)
    
    # Client Information
    client_name = Column(String, nullable=False)
    client_contact = Column(String, nullable=False)
    consignee_name = Column(String, nullable=False)
    consignee_contact = Column(String, nullable=False)
    
    # Route Information
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    distance = Column(Float, nullable=True)
    
    # Tracking
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.ACTIVE, nullable=False)
    
    # Relationships
    truck = relationship("Truck", back_populates="deliveries")
    driver = relationship("Employee", back_populates="deliveries", foreign_keys=[driver_id])
    trip = relationship("Trip", back_populates="delivery", uselist=False)


class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to Delivery
    delivery_id = Column(Integer, ForeignKey("delivery_notes.id"), nullable=False, unique=True)
    
    # Vehicle (for backward compatibility and direct queries)
    vehicle_id = Column(Integer, ForeignKey("trucks.id"), nullable=False)
    
    # Fuel and Cost Tracking
    fuel_consumed = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    
    # Additional trip details
    start_odometer = Column(Float, nullable=True)
    end_odometer = Column(Float, nullable=True)
    
    # Relationships
    delivery = relationship("DeliveryNote", back_populates="trip")
    vehicle = relationship("Truck", back_populates="trips")
