from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class EmployeeType(str, Enum):
    DRIVER = "DRIVER"
    MECHANIC = "MECHANIC"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CLERK = "CLERK"


class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"


class DocumentType(str, Enum):
    LICENSE = "LICENSE"
    CONTRACT = "CONTRACT"
    CERTIFICATE = "CERTIFICATE"
    ID = "ID"
    OTHER = "OTHER"


class DocumentStatus(str, Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"


class CertificationStatus(str, Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"


# Employee Schemas
class EmployeeBase(BaseModel):
    employee_number: str
    name: str
    email: Optional[str] = None
    phone: str
    phone_alt: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    role_title: Optional[str] = None
    employee_type: EmployeeType
    department: Optional[str] = None
    branch: Optional[str] = None
    secondary_department: Optional[str] = None
    supervisor_id: Optional[int] = None
    contract_type: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    probation_end: Optional[date] = None
    employment_date: date
    termination_date: Optional[date] = None
    license_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    status: Optional[EmployeeStatus] = EmployeeStatus.ACTIVE


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    employee_type: Optional[EmployeeType] = None
    department: Optional[str] = None
    branch: Optional[str] = None
    termination_date: Optional[date] = None
    license_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    status: Optional[EmployeeStatus] = None
    supervisor_id: Optional[int] = None
    contract_type: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    probation_end: Optional[date] = None


class EmployeeResponse(EmployeeBase):
    id: int

    model_config = {"from_attributes": True}


# EmployeeDocument Schemas
class EmployeeDocumentBase(BaseModel):
    employee_id: int
    document_type: DocumentType
    document_name: str
    file_path: Optional[str] = None
    tag: Optional[str] = None
    is_sensitive: Optional[bool] = False
    verified: Optional[bool] = False
    approved_by: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[DocumentStatus] = DocumentStatus.VALID
    notes: Optional[str] = None


class EmployeeDocumentCreate(EmployeeDocumentBase):
    pass


class EmployeeDocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    document_name: Optional[str] = None
    file_path: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[DocumentStatus] = None
    notes: Optional[str] = None
    tag: Optional[str] = None
    is_sensitive: Optional[bool] = None
    verified: Optional[bool] = None
    approved_by: Optional[str] = None


class EmployeeHistoryBase(BaseModel):
    employee_id: int
    change_type: str
    from_value: Optional[str] = None
    to_value: Optional[str] = None
    effective_date: date
    notes: Optional[str] = None


class EmployeeHistoryResponse(EmployeeHistoryBase):
    id: int
    model_config = {"from_attributes": True}


class EmployeeDocumentResponse(EmployeeDocumentBase):
    id: int

    model_config = {"from_attributes": True}


# Certification Schemas
class CertificationBase(BaseModel):
    employee_id: int
    certification_type: str
    certification_name: str
    issuing_authority: Optional[str] = None
    issue_date: date
    expiry_date: Optional[date] = None
    status: Optional[CertificationStatus] = CertificationStatus.VALID
    notes: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    certification_type: Optional[str] = None
    certification_name: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[CertificationStatus] = None
    notes: Optional[str] = None


class CertificationResponse(CertificationBase):
    id: int

    model_config = {"from_attributes": True}
