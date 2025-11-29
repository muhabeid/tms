from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class JobType(str, Enum):
    SCHEDULED = "SCHEDULED"
    BREAKDOWN = "BREAKDOWN"
    INSPECTION = "INSPECTION"
    ACCIDENT_REPAIR = "ACCIDENT_REPAIR"
    UPGRADE = "UPGRADE"


class JobPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ItemType(str, Enum):
    SPARE_PART = "SPARE_PART"
    CONSUMABLE = "CONSUMABLE"
    TOOL = "TOOL"


class VehicleType(str, Enum):
    TRUCK = "TRUCK"
    BUS = "BUS"
    UNIVERSAL = "UNIVERSAL"


class MovementType(str, Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"


class ReferenceType(str, Enum):
    JOB_CARD = "JOB_CARD"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    ADJUSTMENT = "ADJUSTMENT"


class POStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class SupplierStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# MaintenanceJob Schemas
class MaintenanceJobBase(BaseModel):
    job_card_number: str
    vehicle_id: int
    mechanic_id: Optional[int] = None
    job_type: JobType
    description: str
    scheduled_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    priority: Optional[JobPriority] = JobPriority.MEDIUM
    status: Optional[JobStatus] = JobStatus.PENDING
    labor_cost: Optional[float] = 0.0
    parts_cost: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0


class MaintenanceJobCreate(MaintenanceJobBase):
    pass


class MaintenanceJobUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    mechanic_id: Optional[int] = None
    job_type: Optional[JobType] = None
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    priority: Optional[JobPriority] = None
    status: Optional[JobStatus] = None
    labor_cost: Optional[float] = None
    parts_cost: Optional[float] = None
    total_cost: Optional[float] = None


class MaintenanceJobResponse(MaintenanceJobBase):
    id: int

    model_config = {"from_attributes": True}


# Supplier Schemas
class SupplierBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[SupplierStatus] = SupplierStatus.ACTIVE


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    status: Optional[SupplierStatus] = None


class SupplierResponse(SupplierBase):
    id: int

    model_config = {"from_attributes": True}


# StoreItem Schemas
class StoreItemBase(BaseModel):
    part_number: str
    name: str
    description: Optional[str] = None
    item_type: ItemType
    vehicle_type: Optional[VehicleType] = VehicleType.UNIVERSAL
    quantity_in_stock: Optional[int] = 0
    minimum_stock_level: Optional[int] = 0
    reorder_level: Optional[int] = 0
    reorder_quantity: Optional[int] = 0
    unit_cost: float
    selling_price: Optional[float] = None
    supplier_id: Optional[int] = None
    shelf_location: Optional[str] = None
    warehouse_section: Optional[str] = None


class StoreItemCreate(StoreItemBase):
    pass


class StoreItemUpdate(BaseModel):
    part_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[ItemType] = None
    vehicle_type: Optional[VehicleType] = None
    quantity_in_stock: Optional[int] = None
    minimum_stock_level: Optional[int] = None
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None
    unit_cost: Optional[float] = None
    selling_price: Optional[float] = None
    supplier_id: Optional[int] = None
    shelf_location: Optional[str] = None
    warehouse_section: Optional[str] = None


class StoreItemResponse(StoreItemBase):
    id: int

    model_config = {"from_attributes": True}


# PurchaseOrder Schemas
class PurchaseOrderBase(BaseModel):
    po_number: str
    supplier_id: int
    order_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    total_amount: Optional[float] = 0.0
    status: Optional[POStatus] = POStatus.DRAFT


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrderUpdate(BaseModel):
    supplier_id: Optional[int] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    total_amount: Optional[float] = None
    status: Optional[POStatus] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    id: int

    model_config = {"from_attributes": True}


# PurchaseOrderItem Schemas
class PurchaseOrderItemBase(BaseModel):
    purchase_order_id: int
    item_id: int
    quantity_ordered: int
    quantity_received: Optional[int] = 0
    unit_price: float
    total_price: float


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass


class PurchaseOrderItemUpdate(BaseModel):
    quantity_ordered: Optional[int] = None
    quantity_received: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    id: int

    model_config = {"from_attributes": True}


# StockMovement Schemas
class StockMovementBase(BaseModel):
    item_id: int
    movement_type: MovementType
    quantity: int
    reference_type: ReferenceType
    reference_id: int
    date: Optional[datetime] = None
    performed_by: Optional[int] = None
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementResponse(StockMovementBase):
    id: int

    model_config = {"from_attributes": True}


# JobCardPart Schemas
class JobCardPartBase(BaseModel):
    job_card_id: int
    item_id: int
    quantity_used: int
    unit_cost: float
    total_cost: float


class JobCardPartCreate(JobCardPartBase):
    pass


class JobCardPartUpdate(BaseModel):
    quantity_used: Optional[int] = None
    unit_cost: Optional[float] = None
    total_cost: Optional[float] = None


class JobCardPartResponse(JobCardPartBase):
    id: int

    model_config = {"from_attributes": True}
