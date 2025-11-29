"""
Test database connection directly
"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def test_db():
    print("Testing database connection...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("OK Database connection works!")
            
            # Check if trucks table exists
            result = await conn.execute(text("SELECT COUNT(*) FROM trucks"))
            count = result.scalar()
            print(f"OK Trucks table exists with {count} rows")
            
            # Check if employees table exists  
            result = await conn.execute(text("SELECT COUNT(*) FROM employees"))
            count = result.scalar()
            print(f"OK Employees table exists with {count} rows")
            
    except Exception as e:
        print(f"X ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
