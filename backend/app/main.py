
from fastapi import FastAPI
import app.models  # Ensure all models are registered
from app.api.v1 import hr, transport, express, fuel, finance, workshop
from app.db.session import engine
from app.db.base import Base
from sqlalchemy import text
from app.core.config import settings

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TMS Full Stack")

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(transport.router, prefix="/api/v1/transport", tags=["transport"])
app.include_router(express.router, prefix="/api/v1/express", tags=["express"])
app.include_router(fuel.router, prefix="/api/v1/fuel", tags=["fuel"])
app.include_router(hr.router, prefix="/api/v1/hr", tags=["hr"])
app.include_router(finance.router, prefix="/api/v1/finance", tags=["finance"])
app.include_router(workshop.router, prefix="/api/v1/workshop", tags=["workshop"])

@app.get("/ping")
async def ping():
    return {"ping": "pong"}

@app.on_event("startup")
async def create_missing_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        is_sqlite = settings.database_url.startswith("sqlite")
        if not is_sqlite:
            await conn.execute(text("""
                ALTER TABLE delivery_notes DROP CONSTRAINT IF EXISTS delivery_notes_driver_id_fkey;
            """))
            await conn.execute(text("""
                ALTER TABLE delivery_notes ADD CONSTRAINT delivery_notes_driver_id_fkey
                FOREIGN KEY (driver_id) REFERENCES employees(id)
                ON UPDATE CASCADE ON DELETE RESTRICT;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS vehicle_id INTEGER NOT NULL;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS driver_id INTEGER;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS fuel_station_id INTEGER;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS litres DOUBLE PRECISION;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS cost_per_litre DOUBLE PRECISION;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS total_cost DOUBLE PRECISION;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS odometer_reading DOUBLE PRECISION;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS date_time TIMESTAMP;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS receipt_number VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS delivery_id INTEGER;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS trip_id INTEGER;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS job_card_id INTEGER;
            """))
            await conn.execute(text("""
                ALTER TABLE fuel_logs ADD COLUMN IF NOT EXISTS notes VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE employees ADD COLUMN IF NOT EXISTS supervisor_id INTEGER;
            """))
            await conn.execute(text("""
                ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_type VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_start DATE;
            """))
            await conn.execute(text("""
                ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_end DATE;
            """))
            await conn.execute(text("""
                ALTER TABLE employees ADD COLUMN IF NOT EXISTS probation_end DATE;
            """))
            await conn.execute(text("""
                ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_supervisor_id_fkey;
            """))
            await conn.execute(text("""
                ALTER TABLE employees ADD CONSTRAINT employees_supervisor_id_fkey
                FOREIGN KEY (supervisor_id) REFERENCES employees(id)
                ON UPDATE CASCADE ON DELETE SET NULL;
            """))
            await conn.execute(text("""
                ALTER TABLE employee_documents ADD COLUMN IF NOT EXISTS tag VARCHAR;
            """))
            await conn.execute(text("""
                ALTER TABLE employee_documents ADD COLUMN IF NOT EXISTS is_sensitive BOOLEAN DEFAULT FALSE;
            """))
            await conn.execute(text("""
                ALTER TABLE employee_documents ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE;
            """))
            await conn.execute(text("""
                ALTER TABLE employee_documents ADD COLUMN IF NOT EXISTS approved_by VARCHAR;
            """))
