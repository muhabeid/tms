"""
Test API error handling using urllib (similar to existing test scripts)
"""
import urllib.request
import urllib.error
import json

def test_api_errors():
    """Test API error handling"""
    print("Testing API error handling...")
    
    base_url = "http://localhost:8003/api/v1/transport"
    
    # Test 1: Try to get a non-existent truck (should trigger 404)
    print("\n1. Testing 404 error for non-existent truck...")
    try:
        req = urllib.request.Request(f"{base_url}/trucks/99999")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"Unexpected success: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"✅ HTTP Error {e.code}: {e.reason}")
        if e.code == 404:
            print("✅ 404 error handled correctly")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test 2: Test list endpoint (should work, but will show in logs if any issues)
    print("\n2. Testing list trucks endpoint...")
    try:
        req = urllib.request.Request(f"{base_url}/trucks")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"✅ Found {len(data)} trucks (Status: {response.status})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test finance module endpoint
    print("\n3. Testing finance module endpoint...")
    try:
        req = urllib.request.Request("http://localhost:8003/api/v1/finance/transactions")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"✅ Finance module: {len(data)} transactions (Status: {response.status})")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ API error handling test completed!")
    print("Check the logs/ directory for error log files.")

if __name__ == "__main__":
    test_api_errors()