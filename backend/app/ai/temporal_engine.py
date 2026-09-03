import logging
import math
from typing import Dict, List, Tuple, Set, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TemporalTrack:
    def __init__(self, track_id: int):
        self.track_id = track_id
        # History: list of (timestamp, centroid_x, centroid_y, bbox)
        self.history: List[Tuple[datetime, float, float, Tuple[int, int, int, int]]] = []
        
        # Computed metrics
        self.velocity: float = 0.0 # px/s or m/s
        self.direction: float = 0.0 # radians
        self.stationary_duration: float = 0.0 # seconds
        self.last_seen: datetime = datetime.utcnow()
        
        # State machine
        self.state: str = "NORMAL" # NORMAL, ACCIDENT_CANDIDATE, VERIFYING, CONFIRMED, REJECTED
        self.state_entered_at: datetime = datetime.utcnow()
        self.signals: Set[str] = set()

    def add_observation(self, timestamp: datetime, bbox: Tuple[int, int, int, int], pixels_per_meter: Optional[float]):
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        
        self.history.append((timestamp, cx, cy, bbox))
        
        # Keep bounded history (e.g., last 30 observations or 10 seconds)
        if len(self.history) > 60:
            self.history.pop(0)
            
        self.last_seen = timestamp
        self._compute_metrics(pixels_per_meter)

    def _compute_metrics(self, pixels_per_meter: Optional[float]):
        if len(self.history) < 2:
            return
            
        t1, cx1, cy1, _ = self.history[-2]
        t2, cx2, cy2, _ = self.history[-1]
        
        dt = (t2 - t1).total_seconds()
        if dt <= 0:
            return
            
        dx = cx2 - cx1
        dy = cy2 - cy1
        distance_px = math.sqrt(dx**2 + dy**2)
        
        # Velocity
        if pixels_per_meter and pixels_per_meter > 0:
            distance_m = distance_px / pixels_per_meter
            self.velocity = distance_m / dt # m/s
        else:
            self.velocity = distance_px / dt # px/s
            
        # Direction
        self.direction = math.atan2(dy, dx)
        
        # Stationary check
        speed_threshold = 0.5 if pixels_per_meter else 5.0 # m/s or px/s
        if self.velocity < speed_threshold:
            if self.stationary_duration == 0.0:
                # Start counting from previous frame
                self.stationary_duration = dt
            else:
                self.stationary_duration += dt
        else:
            self.stationary_duration = 0.0

class CameraState:
    def __init__(self, camera_id: str, pixels_per_meter: Optional[float] = None):
        self.camera_id = camera_id
        self.pixels_per_meter = pixels_per_meter
        self.tracks: Dict[int, TemporalTrack] = {}
        self.last_congestion_alert: Optional[datetime] = None

class TemporalEngine:
    def __init__(self):
        self.cameras: Dict[str, CameraState] = {}
        
    def get_or_create_camera_state(self, camera_id: str, pixels_per_meter: Optional[float] = None) -> CameraState:
        if camera_id not in self.cameras:
            self.cameras[camera_id] = CameraState(camera_id, pixels_per_meter)
        else:
            # Update calibration if provided
            if pixels_per_meter is not None:
                self.cameras[camera_id].pixels_per_meter = pixels_per_meter
        return self.cameras[camera_id]
        
    def process_frame(self, camera_id: str, timestamp: datetime, boxes: List[Tuple[int,int,int,int]], track_ids: List[int], confs: List[float], pixels_per_meter: Optional[float] = None) -> List[Dict]:
        cam_state = self.get_or_create_camera_state(camera_id, pixels_per_meter)
        events = []
        
        # 1. Update Tracks
        active_ids = set()
        for bbox, tid, conf in zip(boxes, track_ids, confs):
            if tid not in cam_state.tracks:
                cam_state.tracks[tid] = TemporalTrack(tid)
            track = cam_state.tracks[tid]
            track.add_observation(timestamp, bbox, cam_state.pixels_per_meter)
            active_ids.add(tid)
            
        # 2. Evaluate State Machine for Accidents
        for tid, track in list(cam_state.tracks.items()):
            # Cleanup stale tracks
            if (timestamp - track.last_seen).total_seconds() > 5.0:
                del cam_state.tracks[tid]
                continue
                
            self._evaluate_track_state(track, timestamp, cam_state.pixels_per_meter)
            
            if track.state == "CONFIRMED":
                events.append({
                    "type": "ACCIDENT",
                    "camera_id": camera_id,
                    "track_ids": [tid],
                    "severity": "HIGH",
                    "confidence": 0.9,
                    "signals_used": list(track.signals),
                    "timestamp": timestamp,
                    "vehicle_count": len(active_ids)
                })
                # Reset state to avoid spam
                track.state = "NORMAL"
                track.signals.clear()

        # 3. Evaluate Congestion (Global Camera Level)
        congestion_event = self._evaluate_congestion(cam_state, timestamp)
        if congestion_event:
            events.append(congestion_event)
            
        return events

    def _evaluate_track_state(self, track: TemporalTrack, timestamp: datetime, pixels_per_meter: Optional[float]):
        if track.state == "NORMAL":
            # Check for sudden stop or abnormal stop
            # e.g., stationary in middle of frame for > 3 seconds
            if track.stationary_duration > 3.0:
                track.signals.add("abnormal_stop")
                track.state = "ACCIDENT_CANDIDATE"
                track.state_entered_at = timestamp
                
            # Check for sudden deceleration (needs history, simplified here)
            if len(track.history) >= 10:
                pass # Can be enhanced
                
        elif track.state == "ACCIDENT_CANDIDATE":
            # If still stationary after 5 seconds, move to verifying
            if track.stationary_duration > 5.0:
                track.state = "VERIFYING"
                track.state_entered_at = timestamp
            elif track.stationary_duration == 0:
                # Vehicle moved, reject
                track.state = "REJECTED"
                
        elif track.state == "VERIFYING":
            # Check context: are other vehicles stopping around it? (simplified)
            # If stationary > 8 seconds total, confirm
            if track.stationary_duration > 8.0:
                track.state = "CONFIRMED"
                track.signals.add("post_event_stationary")
            elif track.stationary_duration == 0:
                track.state = "REJECTED"
                
        elif track.state == "REJECTED":
            # Reset after a cooldown
            if (timestamp - track.state_entered_at).total_seconds() > 10.0:
                track.state = "NORMAL"
                track.signals.clear()

    def _evaluate_congestion(self, cam_state: CameraState, timestamp: datetime) -> Optional[Dict]:
        if not cam_state.tracks:
            return None
            
        # Count vehicles and avg speed
        active_tracks = [t for t in cam_state.tracks.values() if (timestamp - t.last_seen).total_seconds() < 2.0]
        if len(active_tracks) < 5:
            return None
            
        avg_speed = sum(t.velocity for t in active_tracks) / len(active_tracks)
        
        # Define thresholds
        speed_thresh = 2.0 if cam_state.pixels_per_meter else 15.0 # m/s or px/s
        
        if avg_speed < speed_thresh and len(active_tracks) >= 8:
            # Check cooldown
            if not cam_state.last_congestion_alert or (timestamp - cam_state.last_congestion_alert).total_seconds() > 300:
                cam_state.last_congestion_alert = timestamp
                return {
                    "type": "CONGESTION",
                    "camera_id": cam_state.camera_id,
                    "track_ids": [t.track_id for t in active_tracks],
                    "severity": "MEDIUM",
                    "confidence": 0.85,
                    "signals_used": ["low_avg_speed", "high_vehicle_count"],
                    "timestamp": timestamp,
                    "vehicle_count": len(active_tracks)
                }
        return None
