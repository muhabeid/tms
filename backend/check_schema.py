import asyncio
from app.db.session import get_session

async def check_maintenance_jobs_schema():
    """Check what columns exist in maintenance_jobs table"""
    async for session in get_session():
        try:
            result = await session.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'maintenance_jobs' 
                ORDER BY ordinal_position
            """)
            columns = result.fetchall()
            print("Current maintenance_jobs table schema:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
            break
        except Exception as e:
            print(f"Error checking schema: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    asyncio.run(check_maintenance_jobs_schema())