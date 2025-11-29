from app.schemas.transport import TruckResponse
from app.models.transport import Truck
from app.models.hr import Driver  # Import to register model

def test_pydantic_serialization():
    try:
        print("Creating dummy truck...")
        truck = Truck(
            id=1,
            plate_number="TEST-001",
            model="Test Model",
            year=2023,
            mileage=100.0,
            status="AVAILABLE",
            current_location=None
        )
        print("Validating against TruckResponse...")
        response = TruckResponse.model_validate(truck)
        print(f"Validation successful: {response}")
    except Exception as e:
        print(f"Validation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pydantic_serialization()
