"""
Quick API test script to verify login/register endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register():
    """Test registration"""
    print("\nTesting registration...")
    try:
        data = {
            "email": "testuser@test.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "student"
        }
        response = requests.post(
            f"{BASE_URL}/accounts/register",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test login"""
    print("\nTesting login...")
    try:
        data = {
            "email": "testuser@test.com",
            "password": "testpass123"
        }
        response = requests.post(
            f"{BASE_URL}/accounts/login",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("API Test Script")
    print("=" * 50)
    
    health_ok = test_health()
    if not health_ok:
        print("\n❌ Health check failed! Server might not be running.")
        exit(1)
    
    register_ok = test_register()
    login_ok = test_login()
    
    print("\n" + "=" * 50)
    if register_ok and login_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")


