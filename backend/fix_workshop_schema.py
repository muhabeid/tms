import asyncio
from app.db.session import get_session

async def fix_workshop_schema():
    """Add missing job_card_number column to maintenance_jobs table"""
    async for session in get_session():
        try:
            # Check if the column exists
            result = await session.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'maintenance_jobs' 
                AND column_name = 'job_card_number'
            """)
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("Adding job_card_number column to maintenance_jobs table...")
                await session.execute("""
                    ALTER TABLE maintenance_jobs 
                    ADD COLUMN job_card_number VARCHAR(50) UNIQUE
                """)
                
                # Update existing rows with default job card numbers
                await session.execute("""
                    UPDATE maintenance_jobs 
                    SET job_card_number = 'JC-' || LPAD(id::text, 6, '0')
                    WHERE job_card_number IS NULL
                """)
                
                # Make the column NOT NULL after updating existing rows
                await session.execute("""
                    ALTER TABLE maintenance_jobs 
                    ALTER COLUMN job_card_number SET NOT NULL
                """)
                
                await session.commit()
                print("Successfully added job_card_number column!")
            else:
                print("job_card_number column already exists")
                
        except Exception as e:
            print(f"Error fixing schema: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(fix_workshop_schema())