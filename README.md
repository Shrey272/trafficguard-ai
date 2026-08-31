# TrafficGuard AI 🚨🚦
> **Real-Time AI-Based Traffic Monitoring & Emergency Response System**

TrafficGuard AI is a high-scale, real-time intelligent traffic management system that detects road accidents, analyzes traffic congestion, tracks vehicle counts, and dispatches automated alerts to emergency services (Police & Hospitals).

---

## 🛠️ Complete Technology Stack

| Layer | Technologies Used | Key Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | **React.js, Vite, Tailwind CSS, Lucide Icons** | Real-time live camera feed display, interactive GIS maps, incident management dashboard |
| **Backend API** | **FastAPI, Python 3.14, Uvicorn, WebSockets** | High-performance asynchronous REST API, real-time WebSocket telemetry streaming |
| **Database** | **PostgreSQL (Neon Cloud / Docker), SQLAlchemy, Alembic** | Production connection pooling, high-query index optimization, automated schema management (SQLite local fallback) |
| **AI & Computer Vision** | **YOLOv8, ByteTrack, OpenCV** | Real-time vehicle detection, speed analysis, multi-object tracking, and accident severity detection |
| **DevOps & Cloud** | **Docker, Docker Compose, Render, Vercel** | Containerized microservices, cloud auto-deployments, and database persistence |

---

## 🚀 Quick Start Instructions

### 1. Run the Entire Project (Single Command)
```powershell
.\start.bat
```

### 2. Run Database Migration (SQLite ➔ PostgreSQL)
```powershell
backend\venv\Scripts\python backend\scripts\migrate_sqlite_to_postgres.py
```

### 3. Run via Docker Compose
```powershell
docker-compose up -d
```
