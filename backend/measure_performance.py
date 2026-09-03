import time
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = None

def login():
    global TOKEN
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin123"})
    if res.status_code == 200:
        TOKEN = res.json()["access_token"]
        return True
    return False

def get_headers():
    return {"Authorization": f"Bearer {TOKEN}"}

def measure_api_latency():
    print("Measuring API latency (10 requests)...")
    latencies = []
    for _ in range(10):
        start = time.time()
        requests.get(f"{BASE_URL}/system/health", headers=get_headers())
        end = time.time()
        latencies.append(end - start)
    
    avg_latency = sum(latencies) / len(latencies) * 1000
    print(f"Average API Latency: {avg_latency:.2f} ms")
    return avg_latency

def measure_db_response():
    print("Measuring DB Response via heavy query (GET /incidents)...")
    start = time.time()
    requests.get(f"{BASE_URL}/incidents?limit=1000", headers=get_headers())
    end = time.time()
    latency = (end - start) * 1000
    print(f"DB Query Latency: {latency:.2f} ms")
    return latency

def simulate_event_latency():
    print("Simulating event processing latency (POST /incidents)...")
    payload = {
        "camera_id": "CAM-001",
        "incident_type": "ACCIDENT",
        "severity": "Major",
        "confidence": 0.95,
        "latitude": 21.1838,
        "longitude": 72.8223,
        "vehicle_count": 2,
        "description": "Simulated performance test incident"
    }
    
    start = time.time()
    res = requests.post(f"{BASE_URL}/incidents", json=payload, headers=get_headers())
    end = time.time()
    
    latency = (end - start) * 1000
    print(f"Event Creation & Broadcast Latency: {latency:.2f} ms")
    
    if res.status_code == 200:
        incident_id = res.json()["id"]
        # Clean up
        # We don't have a delete incident endpoint easily accessible, so we resolve it
        requests.patch(f"{BASE_URL}/incidents/{incident_id}/status", json={"status": "RESOLVED"}, headers=get_headers())
    
    return latency

if __name__ == "__main__":
    if login():
        print(f"--- TrafficGuard AI Performance Metrics ---")
        print(f"Timestamp: {datetime.utcnow().isoformat()}")
        measure_api_latency()
        measure_db_response()
        simulate_event_latency()
        print("--- End Metrics ---")
    else:
        print("Failed to authenticate.")
