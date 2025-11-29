from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StationType(str, Enum):
    IN_HOUSE = "IN_HOUSE"
    EXTERNAL = "EXTERNAL"


# FuelStation Schemas
class FuelStationBase(BaseModel):
    name: str
    station_type: StationType
    location: Optional[str] = None
    contact: Optional[str] = None


class FuelStationCreate(FuelStationBase):
    pass


class FuelStationUpdate(BaseModel):
    name: Optional[str] = None
    station_type: Optional[StationType] = None
    location: Optional[str] = None
    contact: Optional[str] = None


class FuelStationResponse(FuelStationBase):
    id: int

    model_config = {"from_attributes": True}


# FuelLog Schemas
class FuelLogBase(BaseModel):
    vehicle_id: int
    driver_id: Optional[int] = None
    fuel_station_id: int
    litres: float
    cost_per_litre: float
    total_cost: float
    odometer_reading: Optional[float] = None
    date_time: Optional[datetime] = None
    receipt_number: Optional[str] = None
    delivery_id: Optional[int] = None
    trip_id: Optional[int] = None
    job_card_id: Optional[int] = None
    notes: Optional[str] = None


class FuelLogCreate(FuelLogBase):
    pass


class FuelLogUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    fuel_station_id: Optional[int] = None
    litres: Optional[float] = None
    cost_per_litre: Optional[float] = None
    total_cost: Optional[float] = None
    odometer_reading: Optional[float] = None
    date_time: Optional[datetime] = None
    receipt_number: Optional[str] = None
    delivery_id: Optional[int] = None
    trip_id: Optional[int] = None
    job_card_id: Optional[int] = None
    notes: Optional[str] = None


class FuelLogResponse(FuelLogBase):
    id: int

    model_config = {"from_attributes": True}
