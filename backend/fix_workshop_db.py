import asyncio
import asyncpg
from app.core.config import settings

async def add_missing_column():
    """Add missing job_card_number column to maintenance_jobs table"""
    try:
        # Connect to the database
        # Convert asyncpg URL format from SQLAlchemy format
        database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(database_url)
        
        print("Adding job_card_number column to maintenance_jobs table...")
        
        # Add the column
        await conn.execute("""
            ALTER TABLE maintenance_jobs 
            ADD COLUMN IF NOT EXISTS job_card_number VARCHAR(50)
        """)
        
        # Update existing rows
        await conn.execute("""
            UPDATE maintenance_jobs 
            SET job_card_number = 'JC-' || LPAD(id::text, 6, '0') 
            WHERE job_card_number IS NULL
        """)
        
        # Make the column NOT NULL
        await conn.execute("""
            ALTER TABLE maintenance_jobs 
            ALTER COLUMN job_card_number SET NOT NULL
        """)
        
        # Add unique constraint
        await conn.execute("""
            ALTER TABLE maintenance_jobs 
            ADD CONSTRAINT unique_job_card_number UNIQUE (job_card_number)
        """)
        
        print("Successfully added job_card_number column!")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error adding column: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_missing_column())