from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import enum


class EmployeeType(str, enum.Enum):
    DRIVER = "DRIVER"
    MECHANIC = "MECHANIC"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CLERK = "CLERK"


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class DocumentType(str, enum.Enum):
    LICENSE = "LICENSE"
    CONTRACT = "CONTRACT"
    CERTIFICATE = "CERTIFICATE"
    ID = "ID"
    OTHER = "OTHER"


class DocumentStatus(str, enum.Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"


class CertificationStatus(str, enum.Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"


class Employee(Base):
    """Enhanced employee model (replaces Driver)"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String, unique=True, nullable=False, index=True)
    
    # Personal Information
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    phone_alt = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    
    # Employment Details
    role_title = Column(String, nullable=True)
    employee_type = Column(Enum(EmployeeType), nullable=False, index=True)
    department = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    secondary_department = Column(String, nullable=True)
    supervisor_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    contract_type = Column(String, nullable=True)
    contract_start = Column(Date, nullable=True)
    contract_end = Column(Date, nullable=True)
    probation_end = Column(Date, nullable=True)
    employment_date = Column(Date, nullable=False)
    termination_date = Column(Date, nullable=True)
    
    # Driver-specific
    license_number = Column(String, nullable=True)
    
    # Emergency Contact
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    
    # Status
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False, index=True)
    
    # Relationships
    documents = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="employee", cascade="all, delete-orphan")
    deliveries = relationship("DeliveryNote", back_populates="driver", foreign_keys="DeliveryNote.driver_id")
    supervisor = relationship("Employee", remote_side=[id])


class EmployeeDocument(Base):
    """Employee document tracking"""
    __tablename__ = "employee_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Document Details
    document_type = Column(Enum(DocumentType), nullable=False)
    document_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    tag = Column(String, nullable=True)
    is_sensitive = Column(Boolean, nullable=False, default=False)
    verified = Column(Boolean, nullable=False, default=False)
    approved_by = Column(String, nullable=True)
    
    # Dates
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.VALID, nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="documents")


class Certification(Base):
    """Employee certification tracking"""
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    # Certification Details
    certification_type = Column(String, nullable=False)  # e.g., "Defensive Driving", "First Aid"
    certification_name = Column(String, nullable=False)
    issuing_authority = Column(String, nullable=True)
    
    # Dates
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    
    # Status
    status = Column(Enum(CertificationStatus), default=CertificationStatus.VALID, nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="certifications")


class EmployeeHistory(Base):
    __tablename__ = "employee_history"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    change_type = Column(String, nullable=False)
    from_value = Column(String, nullable=True)
    to_value = Column(String, nullable=True)
    effective_date = Column(Date, nullable=False, default=datetime.today().date())
    notes = Column(Text, nullable=True)
    employee = relationship("Employee")


# Keep Driver as alias for backward compatibility
Driver = Employee
