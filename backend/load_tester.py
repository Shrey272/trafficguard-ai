import time
import requests
import json
import threading
import statistics
import redis
from datetime import datetime

NUM_WORKERS = 10
CAMERAS_PER_WORKER = 50
CENTRAL_API = "http://localhost:8000"
REDIS_HOST = "localhost"

redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, protocol=2)

latencies = []
events_published = 0
lock = threading.Lock()
running = True

def worker_thread(worker_id: int):
    global events_published
    wid = f"edge-load-{worker_id}"
    
    # Register / Heartbeat
    while running:
        try:
            start_t = time.time()
            resp = requests.post(f"{CENTRAL_API}/api/internal/workers/{wid}/heartbeat", json={
                "status": "ONLINE",
                "processing_fps": 30.0,
                "capacity": CAMERAS_PER_WORKER
            }, timeout=2)
            resp.raise_for_status()
            lat = time.time() - start_t
            with lock:
                latencies.append(lat)
        except requests.exceptions.ConnectionError:
            time.sleep(2.0)
            continue
        except Exception as e:
            print(f"Worker {wid} heartbeat failed: {e}")
            
        # Simulate publishing events
        for _ in range(5):
            if not running:
                break
            try:
                # Mock Plate Observation
                plate_payload = {
                    "type": "PLATE_OBSERVATION",
                    "camera_id": f"SIM-CAM-{worker_id}",
                    "track_id": worker_id * 100,
                    "plate_text": f"XYZ{worker_id}00",
                    "ocr_confidence": 0.95,
                    "detection_confidence": 0.88,
                    "timestamp": datetime.utcnow().isoformat()
                }
                redis_client.publish("trafficguard:events:plate", json.dumps(plate_payload))
                
                with lock:
                    events_published += 1
            except Exception as e:
                pass
                
            time.sleep(1.0) # Publish an event every 1s

def main():
    global running
    print(f"Starting Load Test with {NUM_WORKERS} workers...")
    threads = []
    
    start_time = time.time()
    
    for i in range(NUM_WORKERS):
        t = threading.Thread(target=worker_thread, args=(i,), daemon=True)
        t.start()
        threads.append(t)
        
    try:
        time.sleep(10) # Run test for 10 seconds
    except KeyboardInterrupt:
        pass
        
    running = False
    for t in threads:
        t.join(timeout=1.0)
        
    duration = time.time() - start_time
    
    # Report
    print("=== Load Test Results ===")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total API Heartbeats Recorded: {len(latencies)}")
    if latencies:
        print(f"Avg API Latency: {statistics.mean(latencies)*1000:.2f} ms")
        print(f"Max API Latency: {max(latencies)*1000:.2f} ms")
    
    print(f"Total Redis Events Published: {events_published}")
    print(f"Event Throughput: {events_published/duration:.2f} events/sec")

if __name__ == "__main__":
    main()
