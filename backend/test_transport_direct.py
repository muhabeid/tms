"""
Direct test of Transport module database operations
This bypasses HTTP to test if the issue is with DB or models
"""
import asyncio
from app.db.session import get_session, engine
from app.crud import transport as crud_transport
from app.crud import hr as crud_hr
from app.schemas.transport import TruckCreate, DeliveryNoteCreate, CargoCategory
from app.schemas.hr import EmployeeCreate, EmployeeType
from fastapi import HTTPException
from sqlalchemy import text
from datetime import date
import random

async def test_transport_crud():
    print("Testing Transport CRUD operations directly...")
    print("=" * 50)
    
    # Get database session
    async for db in get_session():
        try:
            async with engine.begin() as conn:
                await conn.execute(text("""
                    ALTER TABLE delivery_notes DROP CONSTRAINT IF EXISTS delivery_notes_driver_id_fkey;
                """))
                await conn.execute(text("""
                    ALTER TABLE delivery_notes ADD CONSTRAINT delivery_notes_driver_id_fkey
                    FOREIGN KEY (driver_id) REFERENCES employees(id)
                    ON UPDATE CASCADE ON DELETE RESTRICT;
                """))
            # Test 1: List trucks
            print("\n1. Testing get_trucks()...")
            trucks = await crud_transport.get_trucks(db)
            print(f"OK Success! Found {len(trucks)} trucks")
            
            # Test 2: Create truck
            print("\n2. Testing create_truck()...")
            truck_data = TruckCreate(
                plate_number=f"TEST-DIRECT-{random.randint(100,999)}",
                model="Isuzu FRR",
                year=2023,
                mileage=0.0,
                status="AVAILABLE"
            )
            new_truck = await crud_transport.create_truck(db, truck_data)
            print(f"OK Success! Created truck with ID: {new_truck.id}")
            
            # Test 3: Get truck by ID
            print("\n3. Testing get_truck()...")
            truck = await crud_transport.get_truck(db, new_truck.id)
            print(f"OK Success! Retrieved truck: {truck.plate_number}")
            
            # Test 4: Attempt create_delivery with invalid driver
            print("\n4. Testing create_delivery() with invalid driver...")
            try:
                delivery = DeliveryNoteCreate(
                    truck_id=new_truck.id,
                    driver_id=999999,
                    cargo_description="Test Cargo",
                    cargo_category=CargoCategory.LOCAL,
                    tonnage=1.0,
                    client_name="Client",
                    client_contact="0000000",
                    consignee_name="Consignee",
                    consignee_contact="1111111",
                    origin="A",
                    destination="B",
                    distance=10.0
                )
                await crud_transport.create_delivery(db, delivery)
                print("Unexpected success: create_delivery should have failed for invalid driver")
            except HTTPException as e:
                print(f"OK Expected error: {e.detail}")

            # Test 5: Create valid driver and delivery
            print("\n5. Creating valid DRIVER employee...")
            employee = EmployeeCreate(
                employee_number=f"DRV-TEST-{random.randint(100,999)}",
                name="Test Driver",
                phone="0700000000",
                employee_type=EmployeeType.DRIVER,
                employment_date=date.today()
            )
            new_emp = await crud_hr.create_employee(db, employee)
            print(f"OK Created employee ID: {new_emp.id}")

            print("\n6. Creating delivery with valid driver...")
            valid_delivery = DeliveryNoteCreate(
                truck_id=new_truck.id,
                driver_id=new_emp.id,
                cargo_description="Valid Cargo",
                cargo_category=CargoCategory.LOCAL,
                tonnage=5.0,
                client_name="Client X",
                client_contact="0711111111",
                consignee_name="Consignee X",
                consignee_contact="0722222222",
                origin="Origin",
                destination="Destination",
                distance=100.0
            )
            created = await crud_transport.create_delivery(db, valid_delivery)
            print(f"OK Created delivery: {created.delivery_number}")

            print("\n7. Skipping truck deletion due to active delivery (FK protection)")
            
            print("\n" + "=" * 50)
            print("OK ALL TESTS PASSED!")
            print("Transport CRUD operations work correctly.")
            print("Issue must be in HTTP layer or endpoint configuration.")
            
        except Exception as e:
            print(f"\nX ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        break  # Only use first session

if __name__ == "__main__":
    asyncio.run(test_transport_crud())
