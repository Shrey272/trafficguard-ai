import requests

BASE_URL = "http://127.0.0.1:8000/api"

def test_unauthorized_access():
    print("Testing unauthenticated access to /api/cameras...")
    response = requests.get(f"{BASE_URL}/cameras")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    print("Success: Unauthenticated access blocked.")

def test_rate_limit():
    print("Testing rate limits on /api/auth/login...")
    # 5 per minute limit
    for i in range(6):
        response = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "wrong"})
        if i < 5:
            assert response.status_code == 401
        else:
            assert response.status_code == 429, f"Expected 429, got {response.status_code}"
    print("Success: Rate limiting active.")

if __name__ == "__main__":
    try:
        test_unauthorized_access()
        test_rate_limit()
        print("All basic security tests passed.")
    except Exception as e:
        print(f"Test failed: {e}")
