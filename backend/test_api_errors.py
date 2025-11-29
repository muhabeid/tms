"""
Test script to verify API error handling in transport module
"""
import asyncio
import aiohttp

async def test_api_error_handling():
    """Test API error handling by triggering various error conditions"""
    print("Testing API error handling...")
    
    base_url = "http://localhost:8003/api/v1/transport"
    
    # Test 1: Try to get a non-existent truck (should trigger 404)
    print("\n1. Testing 404 error for non-existent truck...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/trucks/99999") as response:
                print(f"Status: {response.status}")
                if response.status == 404:
                    print("✅ 404 error handled correctly")
                else:
                    text = await response.text()
                    print(f"Response: {text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test 2: Try to create a truck with invalid data (should trigger validation error)
    print("\n2. Testing validation error with invalid truck data...")
    try:
        invalid_truck_data = {
            "plate_number": "",  # Empty plate number should be invalid
            "model": "Test Model",
            "year": 2023,
            "mileage": 0,
            "status": "INVALID_STATUS"  # Invalid status
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/trucks", json=invalid_truck_data) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text[:200]}...")
                
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test 3: Test list endpoint (should work, but will show in logs if any issues)
    print("\n3. Testing list trucks endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/trucks") as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Found {len(data)} trucks")
                else:
                    text = await response.text()
                    print(f"Error response: {text}")
                    
    except Exception as e:
        print(f"Connection error: {e}")
    
    print("\n✅ API error handling test completed!")
    print("Check the logs/transport_error.log file for any logged errors.")

if __name__ == "__main__":
    asyncio.run(test_api_error_handling())