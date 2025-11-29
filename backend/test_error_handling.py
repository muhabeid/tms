"""
Test script to verify error handling improvements
"""
import asyncio
from app.core.error_handler import get_error_handler

async def test_error_handling():
    """Test the centralized error handling system"""
    print("Testing centralized error handling system...")
    
    # Get transport error handler
    error_handler = get_error_handler("transport")
    
    # Test 1: Basic error logging
    print("\n1. Testing basic error logging...")
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        error_handler.log_error(e, context="Test context for basic error")
    
    # Test 2: API error logging
    print("\n2. Testing API error logging...")
    try:
        raise ConnectionError("Test API connection error")
    except Exception as e:
        error_handler.log_api_error(
            e, 
            endpoint="/test/endpoint", 
            method="POST",
            request_data={"test": "data"},
            user_id="test_user_123"
        )
    
    # Test 3: Log summary
    print("\n3. Testing log summary retrieval...")
    summary = error_handler.get_log_summary(lines=5)
    print(f"Recent log entries:\n{summary}")
    
    print("\n✅ Error handling test completed!")

if __name__ == "__main__":
    asyncio.run(test_error_handling())