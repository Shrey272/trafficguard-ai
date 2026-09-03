import threading
import json
import logging
import time
import asyncio
from datetime import datetime
try:
    import redis
except ImportError:
    redis = None

from app.database.connection import SessionLocal
from app.models.incident import Incident
from app.models.vehicle_observation import VehicleObservation
from app.api.websocket import manager

logger = logging.getLogger(__name__)

class RedisListener:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.redis_client = None
        self.pubsub = None
        self.running = False
        self.thread = None

    def start(self):
        if not redis:
            logger.warning("Redis library not installed, skipping RedisListener")
            return
            
        try:
            self.redis_client = redis.Redis(host=self.host, port=self.port, decode_responses=True, protocol=2)
            self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe("trafficguard:events:incident")
            self.pubsub.subscribe("trafficguard:events:plate")
            self.pubsub.subscribe("trafficguard:health:camera")
            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True, name="RedisListener")
            self.thread.start()
            logger.info("RedisListener started and subscribed to events.")
        except Exception as e:
            logger.error(f"Failed to start RedisListener: {e}")

    def stop(self):
        self.running = False
        if self.pubsub:
            self.pubsub.close()
        if self.redis_client:
            self.redis_client.close()

    def _listen_loop(self):
        while self.running:
            try:
                message = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    channel = message['channel']
                    data = json.loads(message['data'])
                    
                    if channel == "trafficguard:events:incident":
                        self._handle_incident(data)
                    elif channel == "trafficguard:events:plate":
                        self._handle_plate(data)
                    elif channel == "trafficguard:health:camera":
                        # Could update Camera health here if we want to write it to DB continuously
                        # For prototype, we might skip frequent DB writes for health unless status changes
                        pass
            except Exception as e:
                logger.error(f"Error in RedisListener loop: {e}")
                time.sleep(2)

    def _handle_incident(self, data: dict):
        db = SessionLocal()
        try:
            # Reconstruct datetime
            dt = datetime.fromisoformat(data["timestamp"])
            inc = Incident(
                camera_id=data["camera_id"],
                incident_type=data["type"],
                severity=data.get("severity", "MEDIUM"),
                confidence=data.get("confidence", 0.0),
                latitude=data.get("latitude", 0.0),
                longitude=data.get("longitude", 0.0),
                timestamp=dt,
                vehicle_count=data.get("vehicle_count", 0),
                status="NEW",
                description=f"Automated edge detection of {data['type']} at {data['camera_id']}",
                track_ids=",".join(map(str, data.get("track_ids", []))),
                signals_used=",".join(data.get("signals_used", []))
            )
            db.add(inc)
            db.commit()
            db.refresh(inc)
            
            # Broadcast to UI
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            incident_data = {
                "type": "NEW_INCIDENT",
                "data": {
                    "id": inc.id,
                    "camera_id": inc.camera_id,
                    "incident_type": inc.incident_type,
                    "severity": inc.severity,
                    "confidence": inc.confidence,
                    "latitude": inc.latitude,
                    "longitude": inc.longitude,
                    "timestamp": inc.timestamp.isoformat(),
                    "vehicle_count": inc.vehicle_count,
                    "status": inc.status,
                    "description": inc.description
                }
            }
            loop.run_until_complete(manager.broadcast(incident_data))
        except Exception as e:
            logger.error(f"Failed to handle incident from Redis: {e}")
        finally:
            db.close()

    def _handle_plate(self, data: dict):
        db = SessionLocal()
        try:
            dt = datetime.fromisoformat(data["timestamp"])
            obs = VehicleObservation(
                camera_id=data["camera_id"],
                track_id=data["track_id"],
                plate_text=data["plate_text"],
                normalized_plate=data["plate_text"],
                ocr_confidence=data["ocr_confidence"],
                detection_confidence=data["detection_confidence"],
                timestamp=dt,
                vehicle_class="CAR"
            )
            db.add(obs)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to handle plate from Redis: {e}")
        finally:
            db.close()

redis_listener = RedisListener()
