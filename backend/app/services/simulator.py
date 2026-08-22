import asyncio
import random
from datetime import datetime
from app.database.connection import SessionLocal
from app.models.incident import Incident
from app.api.websocket import manager

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
        
        # Generate random incident
        inc_type, severity = random.choice(incident_types)
        camera_id = random.choice(cameras)
        
        confidence = round(random.uniform(85.0, 99.9), 1)
        lat = 40.7 + random.uniform(-0.1, 0.1)
        lng = -74.0 + random.uniform(-0.1, 0.1)
        vehicles = random.randint(1, 10) if inc_type == "ACCIDENT" else random.randint(20, 100)
        
        db = SessionLocal()
        try:
            new_incident = Incident(
                camera_id=camera_id,
                incident_type=inc_type,
                severity=severity,
                confidence=confidence,
                latitude=lat,
                longitude=lng,
                timestamp=datetime.utcnow(),
                vehicle_count=vehicles,
                status="NEW",
                description=f"Automated detection of {inc_type} at {camera_id}"
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
            await manager.broadcast(incident_data)
            print(f"Simulated new incident: {inc_type} at {camera_id}")
            
        except Exception as e:
            print(f"Error in simulator: {e}")
        finally:
            db.close()
