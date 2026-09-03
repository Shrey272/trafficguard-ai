import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Maps WebSocket connection to user metadata { "user_id": int, "username": str, "role": str }
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_data: Dict[str, Any]):
        await websocket.accept()
        self.active_connections[websocket] = user_data
        logger.info(f"WebSocket client connected: {user_data.get('username', 'Anonymous')} ({user_data.get('role', 'VIEWER')})")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            user_data = self.active_connections.pop(websocket)
            logger.info(f"WebSocket client disconnected: {user_data.get('username')}")

    async def broadcast(self, message: dict, min_role: Optional[str] = None):
        """
        Broadcasts message to connected clients.
        If min_role is provided (e.g. ADMIN), only authorized clients receive it.
        """
        role_hierarchy = {"VIEWER": 1, "OPERATOR": 2, "ADMIN": 3}
        min_level = role_hierarchy.get(min_role, 0) if min_role else 0

        dead_connections = []
        for connection, user_data in list(self.active_connections.items()):
            user_role = user_data.get("role", "VIEWER")
            if role_hierarchy.get(user_role, 1) >= min_level:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)

        for dc in dead_connections:
            self.disconnect(dc)

manager = ConnectionManager()

@router.websocket("/ws/alerts")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    # Verify token
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    user_data = {
        "user_id": int(payload["sub"]),
        "username": payload.get("username", "User"),
        "role": payload.get("role", "VIEWER")
    }

    await manager.connect(websocket, user_data)
    
    # Send welcome / connection acknowledgment
    try:
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "data": {
                "authenticated": True,
                "user": user_data
            }
        })
    except Exception:
        pass

    try:
        while True:
            # Client can send auth messages or heartbeats
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Handle late auth handshake if token was sent via message
                if msg.get("type") == "AUTH":
                    client_token = msg.get("token")
                    payload = decode_token(client_token) if client_token else None
                    if payload and "sub" in payload:
                        user_data = {
                            "user_id": int(payload["sub"]),
                            "username": payload.get("username", "User"),
                            "role": payload.get("role", "VIEWER")
                        }
                        manager.active_connections[websocket] = user_data
                        await websocket.send_json({"type": "AUTH_SUCCESS", "user": user_data})
                    else:
                        await websocket.send_json({"type": "AUTH_ERROR", "message": "Invalid token"})
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
