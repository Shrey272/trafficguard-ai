import asyncio
import random
from datetime import datetime
from app.database.connection import SessionLocal
from app.models.incident import Incident
from app.api.websocket import manager
from app.ai.temporal_engine import TemporalEngine

temporal_engine = TemporalEngine()

cameras = [
    "CAM-001", "CAM-002", "CAM-003", "CAM-004", "CAM-005",
    "CAM-NH48-02", "CAM-CTY-12", "CAM-RND-03"
]

incident_types = [
    ("ACCIDENT", "Major"),
    ("ACCIDENT", "Moderate"),
    ("CONGESTION", "Major"),
    ("CONGESTION", "Moderate"),
    ("CONGESTION", "Minor"),
    ("DEBRIS", "Minor")
]

async def simulate_live_data():
    while True:
        # Wait a random time between 15 and 30 seconds
        await asyncio.sleep(random.randint(15, 30))
        
        # Simulate a sequence of track boxes that causes an ACCIDENT or CONGESTION
        camera_id = random.choice(cameras)
        track_id = random.randint(1000, 9999)
        now = datetime.utcnow()
        
        # Simulate Normal Movement -> Sudden Stop -> Verifying -> Confirmed
        for i in range(4):
            # Normal movement
            boxes = [(100 + i*10, 100 + i*10, 150 + i*10, 150 + i*10)]
            temporal_engine.process_frame(camera_id, now + timedelta(seconds=i), boxes, [track_id], [0.95], 10.0)
            
        for i in range(4, 15):
            # Stopped suddenly
            boxes = [(140, 140, 190, 190)]
            events = temporal_engine.process_frame(camera_id, now + timedelta(seconds=i), boxes, [track_id], [0.95], 10.0)
            
            if events:
                _handle_simulated_events(events)
                break
                
        # Occasionally simulate a vehicle movement (1 in 3 chance)
        if random.randint(1, 3) == 1:
            db = SessionLocal()
            try:
                simulate_vehicle_journey(db)
            finally:
                db.close()

def _handle_simulated_events(events):
    db = SessionLocal()
    try:
        for ev in events:
            new_incident = Incident(
                camera_id=ev["camera_id"],
                incident_type=ev["type"],
                severity=ev["severity"],
                confidence=ev["confidence"],
                latitude=40.7 + random.uniform(-0.1, 0.1),
                longitude=-74.0 + random.uniform(-0.1, 0.1),
                timestamp=ev["timestamp"],
                vehicle_count=ev.get("vehicle_count", 1),
                status="NEW",
                description=f"Temporal engine detected {ev['type']} at {ev['camera_id']}",
                track_ids=",".join(map(str, ev.get("track_ids", []))),
                signals_used=",".join(ev.get("signals_used", []))
            )
            db.add(new_incident)
            db.commit()
            db.refresh(new_incident)
            
            # Serialize for websocket
            incident_data = {
                "type": "NEW_INCIDENT",
                "data": {
                    "id": new_incident.id,
                    "camera_id": new_incident.camera_id,
                    "incident_type": new_incident.incident_type,
                    "severity": new_incident.severity,
                    "confidence": new_incident.confidence,
                    "latitude": new_incident.latitude,
                    "longitude": new_incident.longitude,
                    "timestamp": new_incident.timestamp.isoformat(),
                    "vehicle_count": new_incident.vehicle_count,
                    "status": new_incident.status,
                    "description": new_incident.description
                }
            }
            
            # Broadcast
            loop = asyncio.get_event_loop()
            loop.create_task(manager.broadcast(incident_data))
            print(f"Simulated new temporal incident: {ev['type']} at {ev['camera_id']}")
    except Exception as e:
        print(f"Error in simulator event handler: {e}")
    finally:
        db.close()

def simulate_vehicle_journey(db):
    from app.models.vehicle_observation import VehicleObservation
    from app.models.vehicle_journey import VehicleJourney, JourneyPoint
    from app.models.watchlist import WatchlistRecord, WatchlistAlert
    import string
    
    # Generate a random plate
    plate_text = f"GJ-{random.randint(1,9):02d}-{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}-{random.randint(1000,9999)}"
    normalized = plate_text.replace("-", "")
    
    now = datetime.utcnow()
    
    # Pick 2-4 random cameras to form a journey
    journey_cams = random.sample(cameras, random.randint(2, 4))
    
    journey = VehicleJourney(
        normalized_plate=normalized,
        first_seen=now - timedelta(minutes=random.randint(20, 60)),
        last_seen=now,
        status="ACTIVE"
    )
    db.add(journey)
    db.commit()
    db.refresh(journey)
    
    for i, cam_id in enumerate(journey_cams):
        point_time = journey.first_seen + timedelta(minutes=i*10)
        
        obs = VehicleObservation(
            camera_id=cam_id,
            track_id=random.randint(100, 999),
            plate_text=plate_text,
            normalized_plate=normalized,
            ocr_confidence=round(random.uniform(0.85, 0.99), 2),
            detection_confidence=round(random.uniform(0.85, 0.99), 2),
            timestamp=point_time,
            vehicle_class="CAR"
        )
        db.add(obs)
        
        pt = JourneyPoint(
            journey_id=journey.id,
            camera_id=cam_id,
            timestamp=point_time,
            confidence=obs.ocr_confidence
        )
        db.add(pt)
        
    db.commit()
    print(f"Simulated vehicle journey for {normalized} across {len(journey_cams)} cameras.")
