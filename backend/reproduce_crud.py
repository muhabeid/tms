import asyncio
import random
from app.db.session import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import transport as crud_transport
from app.schemas.transport import TruckCreate

async def reproduce():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            plate_num = f"KBZ-{random.randint(100, 999)}A"
            print(f"Attempting to create truck with plate: {plate_num}")
            
            truck_in = TruckCreate(
                plate_number=plate_num,
                model="Isuzu FRR",
                year=2022,
                mileage=15000.0,
                status="AVAILABLE"
            )
            
            truck = await crud_transport.create_truck(session, truck_in)
            print(f"Success! Truck created: {truck.id}")
            
        except Exception as e:
            print(f"Caught exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(reproduce())
