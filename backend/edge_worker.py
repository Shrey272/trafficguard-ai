import argparse
import time
import requests
import json
import logging
import threading
import redis
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EdgeWorker")

# Import isolated modules
from app.camera.camera_manager import CameraManager
from app.ai.pipeline import ANPRPipeline

def main():
    parser = argparse.ArgumentParser(description="TrafficGuard AI Edge Worker")
    parser.add_argument("--id", required=True, help="Worker ID")
    parser.add_argument("--capacity", type=int, default=10, help="Max cameras to process")
    parser.add_argument("--central-url", default="http://localhost:8000", help="Central Platform URL")
    parser.add_argument("--redis-host", default="localhost", help="Redis Host")
    parser.add_argument("--redis-port", type=int, default=6379, help="Redis Port")
    args = parser.parse_args()
    
    logger.info(f"Starting Edge Worker {args.id} (Capacity: {args.capacity})")
    
    # Initialize Redis
    try:
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port, decode_responses=True, protocol=2)
        redis_client.ping()
        logger.info("Connected to Redis broker.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return

    # Initialize independent Camera Manager and Pipeline
    cam_manager = CameraManager()
    pipeline = ANPRPipeline(publish_mode="REDIS", redis_client=redis_client)
    cam_manager.register_ai_sink(pipeline.process_frame)
    cam_manager._start_frame_dispatcher()
    
    assigned_cameras = set()

    def heartbeat_loop():
        while True:
            try:
                payload = {
                    "status": "ONLINE",
                    "processing_fps": 10.0, # Mocked or calculated
                    "capacity": args.capacity
                }
                resp = requests.post(f"{args.central_url}/api/internal/workers/{args.id}/heartbeat", json=payload)
                if resp.status_code == 200:
                    new_assignments = set(resp.json().get("assigned_cameras", []))
                    
                    # Start new cameras
                    for cam_id in new_assignments - assigned_cameras:
                        logger.info(f"Assigned new camera: {cam_id}")
                        # Edge worker would need DB access or Central API to fetch camera rtsp_url
                        # Assuming local DB access for prototype (CameraManager uses SessionLocal natively)
                        cam_manager.start_camera(cam_id)
                        
                    # Stop removed cameras
                    for cam_id in assigned_cameras - new_assignments:
                        logger.info(f"Camera {cam_id} removed from assignment")
                        cam_manager.stop_camera(cam_id)
                        
                    assigned_cameras.clear()
                    assigned_cameras.update(new_assignments)
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                
            # Publish worker and camera health via Redis
            try:
                health_data = cam_manager.get_all_health()
                for cam_id, h in health_data.items():
                    redis_client.publish("trafficguard:health:camera", json.dumps(h))
            except Exception as e:
                pass
                
            time.sleep(5)

    threading.Thread(target=heartbeat_loop, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down Edge Worker")
        cam_manager.shutdown()

if __name__ == "__main__":
    main()
