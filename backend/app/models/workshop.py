from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class JobType(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    BREAKDOWN = "BREAKDOWN"
    INSPECTION = "INSPECTION"
    ACCIDENT_REPAIR = "ACCIDENT_REPAIR"
    UPGRADE = "UPGRADE"


class JobPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ItemType(str, enum.Enum):
    SPARE_PART = "SPARE_PART"
    CONSUMABLE = "CONSUMABLE"
    TOOL = "TOOL"


class VehicleType(str, enum.Enum):
    TRUCK = "TRUCK"
    BUS = "BUS"
    UNIVERSAL = "UNIVERSAL"


class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER = "TRANSFER"


class ReferenceType(str, enum.Enum):
    JOB_CARD = "JOB_CARD"
    PURCHASE_ORDER = "PURCHASE_ORDER"
    ADJUSTMENT = "ADJUSTMENT"


class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class SupplierStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class MaintenanceJob(Base):
    """Enhanced MaintenanceJob/JobCard model"""
    __tablename__ = "maintenance_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_card_number = Column(String, unique=True, nullable=True, index=True, default=None)
    
    # Vehicle and Mechanic
    vehicle_id = Column(Integer, nullable=False)  # Generic vehicle ID (truck or bus)
    mechanic_id = Column(Integer, nullable=True)  # FK to employee/driver
    
    # Job Details
    job_type = Column(Enum(JobType), nullable=False)
    description = Column(Text, nullable=False)
    scheduled_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    
    # Priority and Status
    priority = Column(Enum(JobPriority), default=JobPriority.MEDIUM, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    # Costs
    labor_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Relationships
    job_card_parts = relationship("JobCardPart", back_populates="job_card", cascade="all, delete-orphan")


class Supplier(Base):
    """Supplier model for parts and materials"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    payment_terms = Column(String, nullable=True)
    status = Column(Enum(SupplierStatus), default=SupplierStatus.ACTIVE, nullable=False)
    
    # Relationships
    store_items = relationship("StoreItem", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class StoreItem(Base):
    """Store item/part model with inventory management"""
    __tablename__ = "store_items"
    
    id = Column(Integer, primary_key=True, index=True)
    part_number = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Categorization
    item_type = Column(Enum(ItemType), nullable=False)
    vehicle_type = Column(Enum(VehicleType), default=VehicleType.UNIVERSAL, nullable=False)
    
    # Stock Management
    quantity_in_stock = Column(Integer, default=0, nullable=False)
    minimum_stock_level = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=0, nullable=False)
    reorder_quantity = Column(Integer, default=0, nullable=False)
    
    # Pricing
    unit_cost = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    
    # Location
    shelf_location = Column(String, nullable=True)
    warehouse_section = Column(String, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="store_items")
    stock_movements = relationship("StockMovement", back_populates="item")
    job_card_parts = relationship("JobCardPart", back_populates="item")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="item")


class PurchaseOrder(Base):
    """Purchase order model"""
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    
    total_amount = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(POStatus), default=POStatus.DRAFT, nullable=False)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    """Purchase order line items"""
    __tablename__ = "purchase_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("StoreItem", back_populates="purchase_order_items")


class StockMovement(Base):
    """Stock movement tracking for audit trail"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)  # Positive for IN, negative for OUT
    
    # Reference to source document
    reference_type = Column(Enum(ReferenceType), nullable=False)
    reference_id = Column(Integer, nullable=False)
    
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    performed_by = Column(Integer, nullable=True)  # Employee ID
    notes = Column(Text, nullable=True)
    
    # Relationships
    item = relationship("StoreItem", back_populates="stock_movements")


class JobCardPart(Base):
    """Link between job cards and parts used"""
    __tablename__ = "job_card_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    job_card_id = Column(Integer, ForeignKey("maintenance_jobs.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    
    quantity_used = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Relationships
    job_card = relationship("MaintenanceJob", back_populates="job_card_parts")
    item = relationship("StoreItem", back_populates="job_card_parts")
