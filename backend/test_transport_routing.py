import requests
import json

# Test Transport endpoints
base_url = "http://localhost:8002/api/v1/transport"

print("Testing Transport Module Endpoints...")
print("=" * 50)

# Test 1: List trucks
print("\n1. GET /trucks")
try:
    response = requests.get(f"{base_url}/trucks")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test 2: Create truck
print("\n2. POST /trucks")
truck_data = {
    "plate_number": "TEST-001",
    "model": "Isuzu FRR",
    "year": 2023,
    "mileage": 0,
    "status": "AVAILABLE"
}
try:
    response = requests.post(f"{base_url}/trucks", json=truck_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test 3: Test other modules
print("\n3. Testing other modules for comparison...")
print("\n3a. GET /api/v1/workshop/jobs")
try:
    response = requests.get("http://localhost:8002/api/v1/workshop/jobs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Workshop works! Count: {len(response.json())}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\n3b. GET /api/v1/express/buses")
try:
    response = requests.get("http://localhost:8002/api/v1/express/buses")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Express works! Count: {len(response.json())}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
