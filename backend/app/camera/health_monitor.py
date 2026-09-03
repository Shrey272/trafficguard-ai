import asyncio
import logging
from datetime import datetime
from app.database.connection import SessionLocal
from app.models.camera import Camera
from app.camera.camera_manager import camera_manager
from app.api.websocket import manager

logger = logging.getLogger(__name__)

async def start_camera_health_monitor(interval_seconds: float = 8.0):
    """
    Background task running continuously to inspect camera adapter health,
    sync database state, and broadcast real-time metrics over WebSockets.
    """
    logger.info("Started Camera Health Monitor background task.")
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            
            all_health = camera_manager.get_all_health()
            if not all_health:
                continue

            db = SessionLocal()
            try:
                updates_to_broadcast = []
                for cam_id, health_data in all_health.items():
                    cam = db.query(Camera).filter(Camera.id == cam_id).first()
                    if cam:
                        current_status = health_data["status"]
                        # If camera was disabled manually, preserve disabled status
                        if cam.status == "DISABLED":
                            continue

                        status_changed = cam.status != current_status
                        cam.status = current_status
                        if health_data["is_connected"]:
                            cam.last_seen = datetime.utcnow()
                        
                        updates_to_broadcast.append({
                            "camera_id": cam_id,
                            "camera_code": cam.camera_code,
                            "name": cam.name,
                            "status": current_status,
                            "is_connected": health_data["is_connected"],
                            "fps": health_data["fps"],
                            "uptime_seconds": health_data["uptime_seconds"],
                            "error_message": health_data["error_message"],
                            "latency_ms": health_data["latency_ms"],
                            "last_seen": cam.last_seen.isoformat() if cam.last_seen else None,
                            "status_changed": status_changed
                        })

                db.commit()

                # Broadcast health updates to authenticated WebSocket clients
                if updates_to_broadcast:
                    await manager.broadcast({
                        "type": "CAMERA_HEALTH_METRICS",
                        "data": updates_to_broadcast,
                        "timestamp": datetime.utcnow().isoformat()
                    })

            except Exception as db_err:
                logger.error(f"Error updating camera health in DB: {db_err}")
            finally:
                db.close()

        except asyncio.CancelledError:
            logger.info("Camera Health Monitor task cancelled.")
            break
        except Exception as ex:
            logger.error(f"Unexpected error in camera health monitor loop: {ex}")
