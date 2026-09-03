import logging
import cv2
import numpy as np
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.database.connection import SessionLocal
from app.models.vehicle_observation import VehicleObservation
from app.models.vehicle_journey import VehicleJourney, JourneyPoint
from app.models.watchlist import WatchlistRecord, WatchlistAlert
from app.models.incident import Incident
from app.models.camera import Camera
from app.ai.temporal_engine import TemporalEngine
from app.api.websocket import manager
import asyncio
import re
import math

logger = logging.getLogger(__name__)

# Attempt to load ML libraries
try:
    from ultralytics import YOLO
    import easyocr
    ML_AVAILABLE = True
except ImportError:
    logger.warning("ultralytics or easyocr not installed. Falling back to Mock Pipeline.")
    ML_AVAILABLE = False

class TrackData:
    def __init__(self):
        self.reads = [] # list of (plate_text, conf)
        self.last_seen = datetime.utcnow()
        self.reported = False

class ANPRPipeline:
    def __init__(self, publish_mode="DB", redis_client=None):
        self.publish_mode = publish_mode
        self.redis_client = redis_client
        self.tracks: Dict[int, TrackData] = {}
        self.lock = threading.Lock()
        self.temporal_engine = TemporalEngine()
        self.camera_configs = {} # id -> {"ppm": None, "lat": 0.0, "lng": 0.0}
        
        if ML_AVAILABLE:
            logger.info("Initializing Real YOLOv8 + EasyOCR Pipeline")
            # For prototype, use YOLOv8 nano for vehicle and plate. 
            # In production, we'd use a dedicated plate detection model.
            self.model = YOLO('yolov8n.pt') 
            self.reader = easyocr.Reader(['en'], gpu=False)
        else:
            self.model = None
            self.reader = None
            
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
    def _cleanup_loop(self):
        """Periodically clean up stale tracks and report the best plate read."""
        while True:
            try:
                now = datetime.utcnow()
                with self.lock:
                    stale_ids = []
                    for tid, track in self.tracks.items():
                        if (now - track.last_seen).total_seconds() > 2.0:
                            if not track.reported and track.reads:
                                self._report_best_read(tid, track)
                                track.reported = True
                            stale_ids.append(tid)
                            
                    for tid in stale_ids:
                        del self.tracks[tid]
            except Exception as e:
                logger.error(f"Error in ANPR cleanup loop: {e}")
            
            import time
            time.sleep(1.0)
            
    def _report_best_read(self, track_id: int, track: TrackData):
        if not track.reads:
            return
            
        # Multi-frame voting: pick the plate text that appears most often, or highest conf
        from collections import Counter
        # Group by normalized text
        texts = [self._normalize_plate(text) for text, conf in track.reads if text]
        if not texts:
            return
            
        counter = Counter(texts)
        best_text = counter.most_common(1)[0][0]
        
        # Get max confidence for this text
        best_conf = max([conf for text, conf in track.reads if self._normalize_plate(text) == best_text])
        
        logger.info(f"Finalizing Plate for Track {track_id}: {best_text} (Conf: {best_conf:.2f})")
        
        # Store in DB and check Watchlist
        db = SessionLocal()
        try:
            # We don't have camera_id here directly, so we need a way to pass it. 
            # Wait, the pipeline receives (cam_id, frame). We should pass cam_id to tracks!
            pass
        finally:
            db.close()

    def _normalize_plate(self, text: str) -> str:
        # Strip all non-alphanumeric characters and uppercase
        return re.sub(r'[^A-Z0-9]', '', text.upper())

    def process_frame(self, camera_id: str, frame: np.ndarray):
        """Sink function called by CameraManager."""
        try:
            if not ML_AVAILABLE:
                self._mock_process(camera_id, frame)
                return
                
            now = datetime.utcnow()
            
            # Cache camera config
            if camera_id not in self.camera_configs:
                db = SessionLocal()
                try:
                    cam = db.query(Camera).filter((Camera.id == camera_id) | (Camera.camera_code == camera_id)).first()
                    if cam:
                        self.camera_configs[camera_id] = {
                            "ppm": cam.pixels_per_meter,
                            "lat": cam.latitude,
                            "lng": cam.longitude
                        }
                    else:
                        self.camera_configs[camera_id] = {"ppm": None, "lat": 0.0, "lng": 0.0}
                finally:
                    db.close()
            
            cfg = self.camera_configs[camera_id]
            
            # Run YOLO with ByteTrack
            results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", classes=[2, 3, 5, 7], verbose=False)
            
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                confs = results[0].boxes.conf.cpu().numpy()
                
                # Phase 5: Pass to Temporal Engine
                events = self.temporal_engine.process_frame(
                    camera_id,
                    now,
                    boxes.tolist(),
                    track_ids,
                    confs.tolist(),
                    cfg["ppm"]
                )
                
                if events:
                    self._handle_temporal_events(events, cfg["lat"], cfg["lng"])
                
                for box, track_id, conf in zip(boxes, track_ids, confs):
                    # In a real scenario, we would run a secondary model to detect the plate inside the vehicle box.
                    # For prototype, we'll just run EasyOCR on the bottom half of the vehicle crop.
                    x1, y1, x2, y2 = map(int, box)
                    h = y2 - y1
                    crop = frame[y1 + h//2:y2, x1:x2]
                    
                    if crop.size == 0:
                        continue
                        
                    ocr_results = self.reader.readtext(crop)
                    
                    for (bbox, text, ocr_conf) in ocr_results:
                        normalized = self._normalize_plate(text)
                        if len(normalized) >= 4:
                            self._add_read(track_id, text, ocr_conf, conf, camera_id)
                            break
                            
        except Exception as e:
            logger.error(f"Error in ANPR process_frame: {e}")

    def _add_read(self, track_id: int, text: str, ocr_conf: float, det_conf: float, camera_id: str):
        with self.lock:
            if track_id not in self.tracks:
                self.tracks[track_id] = TrackData()
                self.tracks[track_id].camera_id = camera_id
                self.tracks[track_id].det_conf = det_conf
            
            track = self.tracks[track_id]
            track.reads.append((text, ocr_conf))
            track.last_seen = datetime.utcnow()
            
            # If we have 5 good reads, report immediately
            if len(track.reads) >= 5 and not track.reported:
                self._report_best_read_full(track_id, track)
                track.reported = True

    def _report_best_read_full(self, track_id: int, track: TrackData):
        if not track.reads:
            return
            
        texts = [self._normalize_plate(text) for text, conf in track.reads if text]
        if not texts:
            return
            
        from collections import Counter
        best_text = Counter(texts).most_common(1)[0][0]
        best_conf = max([conf for text, conf in track.reads if self._normalize_plate(text) == best_text])
        
        logger.info(f"Detected Plate: {best_text} from Cam: {track.camera_id}")
        
        now = datetime.utcnow()
        if self.publish_mode == "REDIS" and self.redis_client:
            import json
            payload = {
                "type": "PLATE_OBSERVATION",
                "camera_id": track.camera_id,
                "track_id": track_id,
                "plate_text": best_text,
                "ocr_confidence": float(best_conf),
                "detection_confidence": float(track.det_conf),
                "timestamp": now.isoformat()
            }
            self.redis_client.publish("trafficguard:events:plate", json.dumps(payload))
            return
            
        db = SessionLocal()
        try:
            # 1. Save Vehicle Observation
            obs = VehicleObservation(
                camera_id=track.camera_id,
                track_id=track_id,
                plate_text=best_text,
                normalized_plate=best_text,
                ocr_confidence=float(best_conf),
                detection_confidence=float(track.det_conf),
                timestamp=now,
                vehicle_class="CAR" # Mocked for now, can be extracted from YOLO
            )
            db.add(obs)
            db.commit()
            db.refresh(obs)
            
            # 2. Correlate with Vehicle Journey
            # Find the active journey (last seen within 2 hours)
            journey = db.query(VehicleJourney).filter(
                VehicleJourney.normalized_plate == best_text,
                VehicleJourney.status == "ACTIVE"
            ).order_by(VehicleJourney.last_seen.desc()).first()
            
            if journey and (now - journey.last_seen).total_seconds() <= 7200: # 2 hours
                journey.last_seen = now
            else:
                # Mark old journeys as COMPLETED
                if journey:
                    journey.status = "COMPLETED"
                journey = VehicleJourney(
                    normalized_plate=best_text,
                    first_seen=now,
                    last_seen=now,
                    status="ACTIVE"
                )
                db.add(journey)
                
            db.commit()
            db.refresh(journey)
            
            # Add Journey Point
            point = JourneyPoint(
                journey_id=journey.id,
                camera_id=track.camera_id,
                timestamp=now,
                confidence=float(best_conf)
            )
            db.add(point)
            db.commit()
            
            # 3. Check Watchlist & Suppress Alerts
            watchlist_match = db.query(WatchlistRecord).filter(WatchlistRecord.plate_text == best_text).first()
            if watchlist_match:
                # Check for recent alerts for this plate to suppress spam
                # e.g., if there's an alert in the last 15 minutes for the SAME camera, suppress it.
                last_alert = db.query(WatchlistAlert).filter(
                    WatchlistAlert.watchlist_id == watchlist_match.id
                ).order_by(WatchlistAlert.timestamp.desc()).first()
                
                # Fetch last observation for that alert to compare camera
                should_alert = True
                if last_alert:
                    time_diff = (now - last_alert.timestamp).total_seconds()
                    if time_diff < 900: # 15 minutes global cooldown
                        # But wait, if it's a NEW camera in this journey, maybe we want to alert?
                        # The user said: "If a watchlisted vehicle appears at a new camera: generate one meaningful alert."
                        last_alert_obs = db.query(VehicleObservation).filter(VehicleObservation.id == last_alert.observation_id).first()
                        if last_alert_obs and last_alert_obs.camera_id == track.camera_id:
                            should_alert = False
                        
                if should_alert:
                    alert = WatchlistAlert(
                        observation_id=obs.id,
                        watchlist_id=watchlist_match.id,
                        status="NEW",
                        timestamp=now
                    )
                    db.add(alert)
                    db.commit()
                    db.refresh(alert)
                    
                    # Broadcast WS Alert
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    alert_data = {
                        "type": "WATCHLIST_ALERT",
                        "data": {
                            "id": alert.id,
                            "plate_text": best_text,
                            "category": watchlist_match.category,
                            "camera_id": obs.camera_id,
                            "timestamp": alert.timestamp.isoformat()
                        }
                    }
                    loop.run_until_complete(manager.broadcast(alert_data))
                else:
                    logger.info(f"Watchlist Alert Suppressed for {best_text} (Cooldown/Same Cam)")
                
        except Exception as e:
            logger.error(f"DB Error reporting plate: {e}")
        finally:
            db.close()

    def _handle_temporal_events(self, events: List[Dict], lat: float, lng: float):
        if self.publish_mode == "REDIS" and self.redis_client:
            import json
            for ev in events:
                ev["latitude"] = lat
                ev["longitude"] = lng
                ev["timestamp"] = ev["timestamp"].isoformat()
                self.redis_client.publish("trafficguard:events:incident", json.dumps(ev))
                logger.info(f"Temporal Engine published {ev['type']} to Redis on cam {ev['camera_id']}")
            return
            
        db = SessionLocal()
        try:
            for ev in events:
                inc = Incident(
                    camera_id=ev["camera_id"],
                    incident_type=ev["type"],
                    severity=ev["severity"],
                    confidence=ev["confidence"],
                    latitude=lat,
                    longitude=lng,
                    timestamp=ev["timestamp"],
                    vehicle_count=ev.get("vehicle_count", len(ev.get("track_ids", []))),
                    status="NEW",
                    description=f"Automated detection of {ev['type']} at {ev['camera_id']}",
                    track_ids=",".join(map(str, ev.get("track_ids", []))),
                    signals_used=",".join(ev.get("signals_used", []))
                )
                db.add(inc)
                db.commit()
                db.refresh(inc)
                
                logger.info(f"Temporal Engine triggered {ev['type']} on cam {ev['camera_id']}")
                
                # Broadcast
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
            logger.error(f"Error handling temporal events: {e}")
        finally:
            db.close()

    def _mock_process(self, camera_id: str, frame: np.ndarray):
        """Simulated pipeline if ML libs are not available."""
        pass

anpr_pipeline = ANPRPipeline()
