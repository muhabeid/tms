import asyncio
from app.db.session import engine
from app.db.base import Base
from app.models import workshop, hr, transport, express, fuel, finance  # Import all models to register them

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(create_tables())
