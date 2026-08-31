from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api import cameras, incidents, traffic, alerts, websocket
from app.database.connection import engine, Base
from app.models.camera import Camera
from app.models.incident import Incident
from app.models.traffic import TrafficEvent
from app.models.alert import Alert
from contextlib import asynccontextmanager
from app.database import init_db

# Create DB tables
Base.metadata.create_all(bind=engine)


import asyncio
from app.services.simulator import simulate_live_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB with mock data if needed
    init_db.seed_cameras()
    # Start the simulator task
    simulator_task = asyncio.create_task(simulate_live_data())
    yield
    # Cancel on shutdown
    simulator_task.cancel()

app = FastAPI(title="TrafficGuard AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(websocket.router, tags=["websocket"])

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "TrafficGuard AI Backend is running"}

# Serve Frontend Static Files
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    # Mount assets folder explicitly if needed, but the catch-all handles files well
    # Mount everything else via catch-all to support React Router (SPA)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
