import urllib.request
import json

BASE_URL = "http://localhost:8003/api/v1/transport"

def make_request(method, url, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.data = json_data

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200 or response.status == 201:
                return json.loads(response.read().decode('utf-8'))
            else:
                print(f"Request failed with status: {response.status}")
                return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None


print("=== Testing Transport Module ===\n")

# Test 1: Create a truck
import random
plate_num = f"KBZ-{random.randint(100, 999)}A"
print(f"1. Creating truck {plate_num}...")
truck_data = {
    "plate_number": plate_num,
    "model": "Isuzu FRR",
    "year": 2022,
    "mileage": 15000.0,
    "status": "AVAILABLE"
}
truck = make_request("POST", f"{BASE_URL}/trucks", truck_data)
if truck:
    print(f"   ✓ Truck created: {truck['plate_number']} (ID: {truck['id']})\n")
    truck_id = truck['id']
else:
    print("   ✗ Failed to create truck\n")
    exit(1)

# Test 2: Create a driver (via HR API)
print("2. Creating driver...")
driver_data = {"name": "John Kamau"}
req = urllib.request.Request("http://localhost:8002/api/v1/hr/employees", method="POST")
req.add_header('Content-Type', 'application/json')
req.data = json.dumps(driver_data).encode('utf-8')
with urllib.request.urlopen(req) as response:
    driver = json.loads(response.read().decode('utf-8'))
    print(f"   ✓ Driver created: {driver['name']} (ID: {driver['id']})\n")
    driver_id = driver['id']

# Test 3: Create a LOCAL delivery
print("3. Creating LOCAL delivery...")
delivery_data = {
    "truck_id": truck_id,
    "driver_id": driver_id,
    "cargo_description": "Electronics - Laptops and Monitors",
    "cargo_category": "LOCAL",
    "tonnage": 2.5,
    "client_name": "TechStore Ltd",
    "client_contact": "+254712345678",
    "consignee_name": "Nairobi Branch",
    "consignee_contact": "+254712345679",
    "origin": "Mombasa",
    "destination": "Nairobi",
    "distance": 480.0
}
delivery = make_request("POST", f"{BASE_URL}/deliveries", delivery_data)
if delivery:
    print(f"   ✓ Delivery created: {delivery['delivery_number']}")
    print(f"     Category: {delivery['cargo_category']}, Status: {delivery['status']}\n")
    delivery_id = delivery['id']
else:
    print("   ✗ Failed to create delivery\n")
    exit(1)

# Test 4: Try to create another LOCAL delivery (should fail - business rule)
print("4. Testing business rule: Creating another LOCAL delivery (should fail)...")
delivery2 = make_request("POST", f"{BASE_URL}/deliveries", delivery_data)
if delivery2:
    print("   ✗ Business rule failed - should not allow multiple active LOCAL deliveries\n")
else:
    print("   ✓ Business rule working - rejected duplicate LOCAL delivery\n")

# Test 5: Create an IMPORT delivery (should succeed - different category)
print("5. Creating IMPORT delivery (different category, should succeed)...")
delivery_data["cargo_category"] = "IMPORT"
delivery_data["cargo_description"] = "Imported Machinery"
delivery_data["tonnage"] = 15.0
delivery_import = make_request("POST", f"{BASE_URL}/deliveries", delivery_data)
if delivery_import:
    print(f"   ✓ IMPORT delivery created: {delivery_import['delivery_number']}\n")
else:
    print("   ✗ Failed to create IMPORT delivery\n")

# Test 6: List all deliveries
print("6. Listing all deliveries...")
deliveries = make_request("GET", f"{BASE_URL}/deliveries")
if deliveries:
    print(f"   ✓ Found {len(deliveries)} deliveries:")
    for d in deliveries:
        print(f"     - {d['delivery_number']}: {d['cargo_category']} ({d['status']})")
    print()

# Test 7: Complete the first delivery
print("7. Completing LOCAL delivery...")
completed = make_request("PUT", f"{BASE_URL}/deliveries/{delivery_id}/complete")
if completed:
    print(f"   ✓ Delivery completed: {completed['delivery_number']} (Status: {completed['status']})\n")

# Test 8: Now we should be able to create another LOCAL delivery
print("8. Creating new LOCAL delivery after completion...")
delivery_data["cargo_category"] = "LOCAL"
delivery_data["cargo_description"] = "Furniture"
delivery_new = make_request("POST", f"{BASE_URL}/deliveries", delivery_data)
if delivery_new:
    print(f"   ✓ New LOCAL delivery created: {delivery_new['delivery_number']}\n")

# Test 9: List trips
print("9. Listing all trips...")
trips = make_request("GET", f"{BASE_URL}/trips")
if trips:
    print(f"   ✓ Found {len(trips)} trips (auto-created with deliveries)\n")

print("=== Transport Module Test Complete ===")
