import asyncio
from app.db.session import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import workshop as crud_workshop
from app.schemas.workshop import MaintenanceJobCreate
from datetime import date

async def reproduce():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("Attempting to create maintenance job...")
            
            # We need a truck first, let's assume one exists or create one
            # For simplicity, we'll try ID 1. If it fails, we'll know.
            # But better to create one to be safe.
            from app.crud import transport as crud_transport
            from app.schemas.transport import TruckCreate
            import random
            
            plate_num = f"KBZ-{random.randint(100, 999)}W"
            truck_in = TruckCreate(
                plate_number=plate_num,
                model="Workshop Test Truck",
                year=2022,
                mileage=10000.0,
                status="AVAILABLE"
            )
            truck = await crud_transport.create_truck(session, truck_in)
            print(f"Created truck: {truck.id}")
            
            job_in = MaintenanceJobCreate(
                truck_id=truck.id,
                title="Routine Service",
                description="Oil change and filter replacement",
                scheduled_date=date.today(),
                status="SCHEDULED"
            )
            
            job = await crud_workshop.create_maintenance_job(session, job_in)
            print(f"Success! Job created: {job.id}")
            
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce())
