from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from fastapi import HTTPException
from app.models.hr import Employee, EmployeeDocument, Certification, EmployeeType, EmployeeStatus, EmployeeHistory
from app.schemas.hr import (
    EmployeeCreate, EmployeeUpdate,
    EmployeeDocumentCreate, EmployeeDocumentUpdate,
    CertificationCreate, CertificationUpdate
)
from datetime import date, timedelta


# Employee CRUD
async def get_employees(db: AsyncSession, skip: int = 0, limit: int = 100,
                        employee_type: str = None, status: str = None,
                        branch: str = None, department: str = None, search: str = None):
    """Get all employees with optional filters"""
    query = select(Employee)
    
    if employee_type:
        query = query.where(Employee.employee_type == employee_type)
    if status:
        query = query.where(Employee.status == status)
    if branch:
        query = query.where(Employee.branch == branch)
    if department:
        query = query.where(Employee.department == department)
    if search:
        like = f"%{search}%"
        query = query.where(or_(Employee.name.ilike(like), Employee.employee_number.ilike(like)))
    
    result = await db.execute(query.offset(skip).limit(limit).order_by(Employee.name))
    return result.scalars().all()


async def create_employee(db: AsyncSession, employee: EmployeeCreate):
    """Create a new employee"""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee


async def get_employee(db: AsyncSession, employee_id: int):
    """Get an employee by ID"""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


async def update_employee(db: AsyncSession, employee_id: int, employee_update: EmployeeUpdate):
    """Update an employee"""
    db_employee = await get_employee(db, employee_id)
    update_data = employee_update.model_dump(exclude_unset=True)
    changes = {}
    for field, value in update_data.items():
        old = getattr(db_employee, field, None)
        if value != old:
            changes[field] = (old, value)
        setattr(db_employee, field, value)
    await db.commit()
    await db.refresh(db_employee)
    from app.models.hr import EmployeeHistory
    tracked_fields = {
        "employee_type": "ROLE_CHANGE",
        "department": "DEPARTMENT_CHANGE",
        "branch": "BRANCH_CHANGE",
        "status": "STATUS_CHANGE",
        "supervisor_id": "SUPERVISOR_CHANGE"
    }
    for field, (old, new) in changes.items():
        if field in tracked_fields:
            history = EmployeeHistory(
                employee_id=employee_id,
                change_type=tracked_fields[field],
                from_value=str(old) if old is not None else None,
                to_value=str(new) if new is not None else None,
                effective_date=date.today()
            )
            db.add(history)
    await db.commit()
    return db_employee


async def delete_employee(db: AsyncSession, employee_id: int):
    """Delete an employee"""
    db_employee = await get_employee(db, employee_id)
    await db.delete(db_employee)
    await db.commit()
    return {"message": "Employee deleted successfully"}


# EmployeeDocument CRUD
async def get_employee_documents(db: AsyncSession, employee_id: int = None):
    """Get employee documents, optionally filtered by employee"""
    query = select(EmployeeDocument)
    if employee_id:
        query = query.where(EmployeeDocument.employee_id == employee_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_employee_document(db: AsyncSession, document: EmployeeDocumentCreate):
    """Create a new employee document"""
    db_document = EmployeeDocument(**document.model_dump())
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    return db_document


async def get_employee_history(db: AsyncSession, employee_id: int):
    result = await db.execute(select(EmployeeHistory).where(EmployeeHistory.employee_id == employee_id))
    return result.scalars().all()


async def add_employee_history(db: AsyncSession, employee_id: int, change_type: str, from_value: str = None, to_value: str = None, notes: str = None):
    history = EmployeeHistory(
        employee_id=employee_id,
        change_type=change_type,
        from_value=from_value,
        to_value=to_value,
        effective_date=date.today(),
        notes=notes
    )
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def get_employee_document(db: AsyncSession, document_id: int):
    """Get an employee document by ID"""
    result = await db.execute(select(EmployeeDocument).where(EmployeeDocument.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


async def update_employee_document(db: AsyncSession, document_id: int, document_update: EmployeeDocumentUpdate):
    """Update an employee document"""
    db_document = await get_employee_document(db, document_id)
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    await db.commit()
    await db.refresh(db_document)
    return db_document


async def delete_employee_document(db: AsyncSession, document_id: int):
    """Delete an employee document"""
    db_document = await get_employee_document(db, document_id)
    await db.delete(db_document)
    await db.commit()
    return {"message": "Document deleted successfully"}


# Certification CRUD
async def get_certifications(db: AsyncSession, employee_id: int = None):
    """Get certifications, optionally filtered by employee"""
    query = select(Certification)
    if employee_id:
        query = query.where(Certification.employee_id == employee_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_certification(db: AsyncSession, certification: CertificationCreate):
    """Create a new certification"""
    db_certification = Certification(**certification.model_dump())
    db.add(db_certification)
    await db.commit()
    await db.refresh(db_certification)
    return db_certification


async def get_certification(db: AsyncSession, certification_id: int):
    """Get a certification by ID"""
    result = await db.execute(select(Certification).where(Certification.id == certification_id))
    certification = result.scalar_one_or_none()
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification


async def update_certification(db: AsyncSession, certification_id: int, certification_update: CertificationUpdate):
    """Update a certification"""
    db_certification = await get_certification(db, certification_id)
    update_data = certification_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_certification, field, value)
    await db.commit()
    await db.refresh(db_certification)
    return db_certification


async def delete_certification(db: AsyncSession, certification_id: int):
    """Delete a certification"""
    db_certification = await get_certification(db, certification_id)
    await db.delete(db_certification)
    await db.commit()
    return {"message": "Certification deleted successfully"}


# Analytics Functions
async def get_expiring_documents(db: AsyncSession, days: int = 30):
    """Get documents expiring within specified days"""
    expiry_threshold = date.today() + timedelta(days=days)
    
    result = await db.execute(
        select(EmployeeDocument).where(
            and_(
                EmployeeDocument.expiry_date.isnot(None),
                EmployeeDocument.expiry_date <= expiry_threshold,
                EmployeeDocument.expiry_date >= date.today()
            )
        )
    )
    return result.scalars().all()


async def get_expiring_certifications(db: AsyncSession, days: int = 30):
    """Get certifications expiring within specified days"""
    expiry_threshold = date.today() + timedelta(days=days)
    
    result = await db.execute(
        select(Certification).where(
            and_(
                Certification.expiry_date.isnot(None),
                Certification.expiry_date <= expiry_threshold,
                Certification.expiry_date >= date.today()
            )
        )
    )
    return result.scalars().all()


async def get_expiring_contracts(db: AsyncSession, days: int = 30):
    threshold = date.today() + timedelta(days=days)
    result = await db.execute(select(Employee).where(and_(Employee.contract_end.isnot(None), Employee.contract_end <= threshold)))
    return result.scalars().all()


async def get_upcoming_probation_completions(db: AsyncSession, days: int = 30):
    threshold = date.today() + timedelta(days=days)
    result = await db.execute(select(Employee).where(and_(Employee.probation_end.isnot(None), Employee.probation_end <= threshold)))
    return result.scalars().all()


async def get_employee_count_by_type(db: AsyncSession):
    """Get employee count grouped by type"""
    result = await db.execute(
        select(
            Employee.employee_type,
            func.count(Employee.id).label('count')
        ).where(Employee.status == EmployeeStatus.ACTIVE).group_by(Employee.employee_type)
    )
    return [{"employee_type": row.employee_type, "count": row.count} for row in result.all()]
