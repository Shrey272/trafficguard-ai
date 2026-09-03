import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.responses import FileResponse  # type: ignore
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter

from app.api import cameras, incidents, traffic, websocket, auth, watchlist, vehicles, audit, onvif, alerts, workers, system
from app.database.connection import engine, Base
from app.models.camera import Camera
from app.models.incident import Incident
from app.models.traffic import TrafficEvent
from app.models.alert import Alert
from app.models.vehicle_observation import VehicleObservation
from app.models.vehicle_journey import VehicleJourney, JourneyPoint
from app.models.watchlist import WatchlistRecord, WatchlistAlert
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.worker import EdgeWorker
from app.database import init_db
from app.services.simulator import simulate_live_data
from app.camera.camera_manager import camera_manager
from app.services.redis_listener import redis_listener
from app.camera.health_monitor import start_camera_health_monitor
from app.ai.pipeline import anpr_pipeline

# Ensure schema migrations and create missing DB tables
init_db.migrate_schema()
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB with schema migration, users, cameras, plates, and audit logs
    init_db.migrate_schema()
    init_db.seed_users()
    init_db.seed_cameras()
    init_db.seed_vehicle_observations()
    init_db.seed_audit_logs()

    # Initialize Normalized Camera Manager
    camera_manager.initialize_all()
    camera_manager.register_ai_sink(anpr_pipeline.process_frame)
    redis_listener.start()

    # Start background simulator & health monitor tasks
    simulator_task = asyncio.create_task(simulate_live_data())
    health_monitor_task = asyncio.create_task(start_camera_health_monitor())

    yield

    # Cancel background tasks on shutdown
    simulator_task.cancel()
    health_monitor_task.cancel()
    camera_manager.shutdown()
    redis_listener.stop()

app = FastAPI(title="TrafficGuard AI - CCTV & Traffic Intelligence", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(onvif.router, prefix="/api/onvif", tags=["onvif"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
app.include_router(audit.router, prefix="/api/audit-logs", tags=["audit"])
app.include_router(system.router, prefix="/api/system", tags=["System"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(workers.router, prefix="/api/workers", tags=["workers"])
app.include_router(workers.internal_router, prefix="/api/internal/workers", tags=["workers-internal"])

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "TrafficGuard AI Backend",
        "cameras_managed": len(camera_manager.adapters),
        "version": "2.5.0-PHASE2"
    }

# Serve Frontend Static Files
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
