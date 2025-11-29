from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import hr as crud_hr
from app.schemas.hr import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentResponse,
    CertificationCreate, CertificationUpdate, CertificationResponse
)
from typing import List, Optional
from fastapi import File, UploadFile, Form
from pathlib import Path
from datetime import date

router = APIRouter()


# Employee Endpoints
@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    employee_type: Optional[str] = Query(None, description="Filter by employee type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    branch: Optional[str] = Query(None, description="Filter by branch"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search by name or number"),
    db: AsyncSession = Depends(get_session)
):
    employees = await crud_hr.get_employees(db, skip=skip, limit=limit,
                                            employee_type=employee_type, status=status,
                                            branch=branch, department=department, search=search)
    return employees


@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, db: AsyncSession = Depends(get_session)):
    """Create a new employee"""
    return await crud_hr.create_employee(db, employee)


@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_session)):
    """Get an employee by ID"""
    return await crud_hr.get_employee(db, employee_id)


@router.put("/employees/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: AsyncSession = Depends(get_session)):
    """Update an employee"""
    return await crud_hr.update_employee(db, employee_id, employee_update)


@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_session)):
    """Delete an employee"""
    return await crud_hr.delete_employee(db, employee_id)


@router.get("/employees/{employee_id}/history")
async def list_employee_history(employee_id: int, db: AsyncSession = Depends(get_session)):
    return await crud_hr.get_employee_history(db, employee_id)


# EmployeeDocument Endpoints
@router.get("/documents", response_model=List[EmployeeDocumentResponse])
async def list_employee_documents(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    db: AsyncSession = Depends(get_session)
):
    """Get employee documents, optionally filtered by employee"""
    documents = await crud_hr.get_employee_documents(db, employee_id=employee_id)
    return documents


@router.post("/documents", response_model=EmployeeDocumentResponse)
async def create_employee_document(document: EmployeeDocumentCreate, db: AsyncSession = Depends(get_session)):
    """Create a new employee document"""
    return await crud_hr.create_employee_document(db, document)


@router.post("/documents/upload", response_model=EmployeeDocumentResponse)
async def upload_employee_document(
    employee_id: int = Form(...),
    document_type: str = Form(...),
    document_name: str = Form(...),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    tag: Optional[str] = Form(None),
    is_sensitive: Optional[bool] = Form(False),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session)
):
    upload_dir = Path("uploads/hr")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{employee_id}_{document_name}_{file.filename}"
    content = await file.read()
    file_path.write_bytes(content)
    doc = EmployeeDocumentCreate(
        employee_id=employee_id,
        document_type=document_type, 
        document_name=document_name,
        file_path=str(file_path),
        issue_date=issue_date if issue_date else None,
        expiry_date=expiry_date if expiry_date else None,
        tag=tag if tag else None,
        is_sensitive=is_sensitive
    )
    return await crud_hr.create_employee_document(db, doc)


@router.get("/documents/{document_id}", response_model=EmployeeDocumentResponse)
async def get_employee_document(document_id: int, db: AsyncSession = Depends(get_session)):
    """Get an employee document by ID"""
    return await crud_hr.get_employee_document(db, document_id)


@router.put("/documents/{document_id}", response_model=EmployeeDocumentResponse)
async def update_employee_document(document_id: int, document_update: EmployeeDocumentUpdate, db: AsyncSession = Depends(get_session)):
    """Update an employee document"""
    return await crud_hr.update_employee_document(db, document_id, document_update)


@router.delete("/documents/{document_id}")
async def delete_employee_document(document_id: int, db: AsyncSession = Depends(get_session)):
    """Delete an employee document"""
    return await crud_hr.delete_employee_document(db, document_id)


# Certification Endpoints
@router.get("/certifications", response_model=List[CertificationResponse])
async def list_certifications(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    db: AsyncSession = Depends(get_session)
):
    """Get certifications, optionally filtered by employee"""
    certifications = await crud_hr.get_certifications(db, employee_id=employee_id)
    return certifications


@router.post("/certifications", response_model=CertificationResponse)
async def create_certification(certification: CertificationCreate, db: AsyncSession = Depends(get_session)):
    """Create a new certification"""
    return await crud_hr.create_certification(db, certification)


@router.get("/certifications/{certification_id}", response_model=CertificationResponse)
async def get_certification(certification_id: int, db: AsyncSession = Depends(get_session)):
    """Get a certification by ID"""
    return await crud_hr.get_certification(db, certification_id)


@router.put("/certifications/{certification_id}", response_model=CertificationResponse)
async def update_certification(certification_id: int, certification_update: CertificationUpdate, db: AsyncSession = Depends(get_session)):
    """Update a certification"""
    return await crud_hr.update_certification(db, certification_id, certification_update)


@router.delete("/certifications/{certification_id}")
async def delete_certification(certification_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a certification"""
    return await crud_hr.delete_certification(db, certification_id)


# Analytics Endpoints
@router.get("/analytics/expiring-documents", response_model=List[EmployeeDocumentResponse])
async def get_expiring_documents(
    days: int = Query(30, description="Number of days to check for expiry"),
    db: AsyncSession = Depends(get_session)
):
    """Get documents expiring within specified days"""
    return await crud_hr.get_expiring_documents(db, days)


@router.get("/analytics/expiring-certifications", response_model=List[CertificationResponse])
async def get_expiring_certifications(
    days: int = Query(30, description="Number of days to check for expiry"),
    db: AsyncSession = Depends(get_session)
):
    """Get certifications expiring within specified days"""
    return await crud_hr.get_expiring_certifications(db, days)


@router.get("/analytics/employee-count-by-type")
async def get_employee_count_by_type(db: AsyncSession = Depends(get_session)):
    """Get employee count grouped by type"""
    return await crud_hr.get_employee_count_by_type(db)


@router.get("/analytics/expiring-contracts")
async def list_expiring_contracts(days: int = Query(60), db: AsyncSession = Depends(get_session)):
    return await crud_hr.get_expiring_contracts(db, days)


@router.get("/analytics/upcoming-probation-completions")
async def list_upcoming_probation(days: int = Query(30), db: AsyncSession = Depends(get_session)):
    return await crud_hr.get_upcoming_probation_completions(db, days)


# Calendar / Holidays
@router.get("/calendar/holidays")
async def get_calendar_holidays(
    year: Optional[int] = Query(None, description="Year for holidays"),
    branch: Optional[str] = Query(None, description="Optional branch context"),
    country: Optional[str] = Query("KE", description="Country code for holiday set")
):
    """Return a simple set of ISO dates for public holidays.
    This small, centralized config can later be backed by DB.
    """
    y = year or date.today().year
    # Minimal Kenya set (static, can be extended or replaced with DB)
    fixed = [
        f"{y}-01-01",  # New Year's Day
        f"{y}-05-01",  # Labour Day
        f"{y}-06-01",  # Madaraka Day
        f"{y}-10-20",  # Mashujaa Day
        f"{y}-12-12",  # Jamhuri Day
        f"{y}-12-25",  # Christmas Day
        f"{y}-12-26",  # Boxing Day
    ]
    # Easter and Eid vary; skipped for simplicity in this small endpoint
    # Branch can later be used to include local observances
    return {"year": y, "country": country, "branch": branch, "dates": fixed}