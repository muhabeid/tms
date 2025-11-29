import asyncio
from app.db.session import engine, get_session
from app.models.transport import Truck
from app.models.hr import Driver  # Import to register model
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async def test_insert_truck():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("Creating truck object...")
            truck = Truck(
                plate_number="KBZ-001A",
                model="Isuzu FRR",
                year=2022,
                mileage=15000.0,
                status="AVAILABLE"
            )
            print("Adding to session...")
            session.add(truck)
            print("Committing...")
            await session.commit()
            print("Refreshing...")
            await session.refresh(truck)
            print(f"Truck created successfully: {truck.id}")
        except Exception as e:
            print(f"Error creating truck: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_insert_truck())
