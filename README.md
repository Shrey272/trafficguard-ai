# TrafficGuard AI

AI-Based Traffic Monitoring & Emergency Response System.

## Architecture

* **Frontend:** React, Vite, Tailwind CSS
* **Backend:** FastAPI, SQLite, WebSockets
* **AI Pipeline:** YOLO, ByteTrack, OpenCV

## Setup Instructions

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. AI Pipeline
```bash
cd ai
pip install -r requirements.txt
```
