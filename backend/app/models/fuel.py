from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class StationType(str, enum.Enum):
    IN_HOUSE = "IN_HOUSE"
    EXTERNAL = "EXTERNAL"


class FuelStation(Base):
    """Fuel station model - both in-house and external"""
    __tablename__ = "fuel_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    station_type = Column(Enum(StationType), nullable=False)
    location = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    
    # Relationships
    fuel_logs = relationship("FuelLog", back_populates="fuel_station")


class FuelLog(Base):
    """Enhanced fuel log model"""
    __tablename__ = "fuel_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Vehicle and Driver
    vehicle_id = Column(Integer, nullable=False, index=True)  # Generic vehicle ID (truck or bus)
    driver_id = Column(Integer, nullable=True)  # FK to employee/driver
    
    # Fuel Station
    fuel_station_id = Column(Integer, ForeignKey("fuel_stations.id"), nullable=False)
    
    # Fuel Details
    litres = Column(Float, nullable=False)
    cost_per_litre = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Vehicle Tracking
    odometer_reading = Column(Float, nullable=True)  # Current odometer reading
    
    # Transaction Details
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    receipt_number = Column(String, nullable=True)
    
    # Optional Links to related records
    delivery_id = Column(Integer, nullable=True)  # Link to delivery note
    trip_id = Column(Integer, nullable=True)  # Link to trip
    job_card_id = Column(Integer, nullable=True)  # Link to maintenance job
    
    # Notes
    notes = Column(String, nullable=True)
    
    # Relationships
    fuel_station = relationship("FuelStation", back_populates="fuel_logs")
