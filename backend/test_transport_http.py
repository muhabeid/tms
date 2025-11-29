"""
Comprehensive HTTP test for Transport module endpoints
Tests all CRUD operations via actual HTTP requests
"""
import urllib.request
import urllib.error
import json
import time

def http_request(url, method="GET", data=None):
    """Make HTTP request using urllib"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

print("=" * 60)
print("TRANSPORT MODULE HTTP ENDPOINT TEST")
print("=" * 60)

base_url = "http://localhost:8002/api/v1/transport"

# Wait for server to start
print("\nWaiting for server to start...")
time.sleep(2)

# Test 1: GET /trucks
print("\n1. GET /trucks")
status, response = http_request(f"{base_url}/trucks")
print(f"   Status: {status}")
if status == 200:
    print(f"   SUCCESS! Found {len(response)} trucks")
else:
    print(f"   ERROR: {response}")

# Test 2: POST /trucks
print("\n2. POST /trucks")
truck_data = {
    "plate_number": "HTTP-TEST-001",
    "model": "Isuzu FRR",
    "year": 2023,
    "mileage": 0,
    "status": "AVAILABLE"
}
status, response = http_request(f"{base_url}/trucks", method="POST", data=truck_data)
print(f"   Status: {status}")
if status == 200:
    truck_id = response.get('id')
    print(f"   SUCCESS! Created truck ID: {truck_id}")
    
    # Test 3: GET /trucks/{truck_id}
    print(f"\n3. GET /trucks/{truck_id}")
    status, response = http_request(f"{base_url}/trucks/{truck_id}")
    print(f"   Status: {status}")
    if status == 200:
        print(f"   SUCCESS! Retrieved: {response.get('plate_number')}")
    else:
        print(f"   ERROR: {response}")
    
    # Test 4: PUT /trucks/{truck_id}
    print(f"\n4. PUT /trucks/{truck_id}")
    update_data = {"mileage": 1000.0}
    status, response = http_request(f"{base_url}/trucks/{truck_id}", method="PUT", data=update_data)
    print(f"   Status: {status}")
    if status == 200:
        print(f"   SUCCESS! Updated mileage to: {response.get('mileage')}")
    else:
        print(f"   ERROR: {response}")
    
    # Test 5: DELETE /trucks/{truck_id}
    print(f"\n5. DELETE /trucks/{truck_id}")
    status, response = http_request(f"{base_url}/trucks/{truck_id}", method="DELETE")
    print(f"   Status: {status}")
    if status == 200:
        print(f"   SUCCESS! Deleted truck")
    else:
        print(f"   ERROR: {response}")
else:
    print(f"   ERROR: {response}")

# Test other modules for comparison
print("\n" + "=" * 60)
print("TESTING OTHER MODULES FOR COMPARISON")
print("=" * 60)

print("\n6. GET /api/v1/workshop/jobs")
status, response = http_request("http://localhost:8002/api/v1/workshop/jobs")
print(f"   Status: {status}")
if status == 200:
    print(f"   SUCCESS! Workshop module works")
else:
    print(f"   ERROR: {response}")

print("\n7. GET /api/v1/express/buses")
status, response = http_request("http://localhost:8002/api/v1/express/buses")
print(f"   Status: {status}")
if status == 200:
    print(f"   SUCCESS! Express module works")
else:
    print(f"   ERROR: {response}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
