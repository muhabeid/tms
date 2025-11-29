from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class CargoCategory(str, Enum):
    LOCAL = "LOCAL"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"


class DeliveryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Truck Schemas
class TruckBase(BaseModel):
    plate_number: str
    model: str
    year: Optional[int] = None
    mileage: Optional[float] = 0.0
    status: Optional[str] = "AVAILABLE"
    current_location: Optional[str] = None


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    plate_number: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    status: Optional[str] = None
    current_location: Optional[str] = None


class TruckResponse(TruckBase):
    id: int

    model_config = {"from_attributes": True}


# DeliveryNote Schemas
class DeliveryNoteBase(BaseModel):
    truck_id: int
    driver_id: int
    cargo_description: str
    cargo_category: CargoCategory
    tonnage: float
    client_name: str
    client_contact: str
    consignee_name: str
    consignee_contact: str
    origin: str
    destination: str
    distance: Optional[float] = None


class DeliveryNoteCreate(DeliveryNoteBase):
    pass


class DeliveryNoteUpdate(BaseModel):
    truck_id: Optional[int] = None
    driver_id: Optional[int] = None
    cargo_description: Optional[str] = None
    cargo_category: Optional[CargoCategory] = None
    tonnage: Optional[float] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee_contact: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance: Optional[float] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    status: Optional[DeliveryStatus] = None


class DeliveryNoteResponse(DeliveryNoteBase):
    id: int
    delivery_number: str
    created_date: datetime
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    status: DeliveryStatus

    model_config = {"from_attributes": True}


# Trip Schemas
class TripBase(BaseModel):
    delivery_id: int
    vehicle_id: int
    fuel_consumed: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    start_odometer: Optional[float] = None
    end_odometer: Optional[float] = None


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    fuel_consumed: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    start_odometer: Optional[float] = None
    end_odometer: Optional[float] = None


class TripResponse(TripBase):
    id: int

    model_config = {"from_attributes": True}
