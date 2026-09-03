import os
import sys
import warnings
warnings.filterwarnings("ignore")

from fastapi.testclient import TestClient
from main import app
from app.database import init_db

def run_verification():
    print("=" * 60)
    print(" TRAFFICGUARD AI - PHASE 1 VERIFICATION SUITE")
    print("=" * 60)

    # Initialize seeds
    init_db.migrate_schema()
    init_db.seed_users()
    init_db.seed_cameras()
    init_db.seed_vehicle_plates()
    init_db.seed_audit_logs()

    client = TestClient(app)

    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed ({res.status_code}): {res.text}"
    print("[PASS] 1. Backend Health Check & Camera Manager Status")

    # 2. Authentication
    admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200, f"Admin login failed ({admin_login.status_code}): {admin_login.text}"
    admin_token = admin_login.json()["access_token"]
    assert admin_login.json()["user"]["role"] == "ADMIN"

    op_login = client.post("/api/auth/login", json={"username": "operator", "password": "operator123"})
    assert op_login.status_code == 200, f"Operator login failed ({op_login.status_code}): {op_login.text}"
    op_token = op_login.json()["access_token"]

    viewer_login = client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"})
    assert viewer_login.status_code == 200, f"Viewer login failed ({viewer_login.status_code}): {viewer_login.text}"
    viewer_token = viewer_login.json()["access_token"]

    bad_login = client.post("/api/auth/login", json={"username": "admin", "password": "badpassword"})
    assert bad_login.status_code == 401
    print("[PASS] 2. Authentication & JWT Tokens (Admin, Operator, Viewer)")

    # 3. Camera Registry List & Masking
    cams_res = client.get("/api/cameras", headers={"Authorization": f"Bearer {viewer_token}"})
    assert cams_res.status_code == 200, f"Camera list failed ({cams_res.status_code}): {cams_res.text}"
    cams = cams_res.json()
    assert len(cams) >= 8, f"Expected >=8 cameras, found {len(cams)}"
    for c in cams:
        if c.get("rtsp_url"):
            assert "pass123" not in c["rtsp_url"], "RTSP credentials exposed in plain text!"
    print(f"[PASS] 3. Camera Registry Listing ({len(cams)} cameras loaded, credentials safely masked)")

    # 4. RBAC Authorization Checks
    cam_payload = {
        "camera_code": "CAM-VERIFY-01",
        "name": "Verification Gate Camera",
        "department": "Traffic Police",
        "vendor": "Bosch",
        "model": "FLEXIDOME IP 8000i",
        "vms_name": "Surat VMS Alpha",
        "source_type": "MOCK",
        "location_name": "Verification Crossing",
        "latitude": 21.1920,
        "longitude": 72.8250,
        "rtsp_url": "mock://verify-feed",
        "enabled": True
    }

    # Viewer cannot create
    forbid = client.post("/api/cameras", json=cam_payload, headers={"Authorization": f"Bearer {viewer_token}"})
    assert forbid.status_code == 403, f"Expected 403 Forbidden for Viewer, got {forbid.status_code}: {forbid.text}"

    # Admin creates
    created = client.post("/api/cameras", json=cam_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert created.status_code == 200, f"Failed to create camera ({created.status_code}): {created.text}"
    cam_id = created.json()["id"]

    # Health check on newly created camera
    health = client.get(f"/api/cameras/{cam_id}/health")
    assert health.status_code == 200, f"Camera health check failed ({health.status_code}): {health.text}"
    assert health.json()["camera_code"] == "CAM-VERIFY-01"

    # Admin updates
    upd = client.put(f"/api/cameras/{cam_id}", json={"name": "Updated Verification Gate"}, headers={"Authorization": f"Bearer {admin_token}"})
    assert upd.status_code == 200
    assert upd.json()["name"] == "Updated Verification Gate"

    # Admin deletes
    deleted = client.delete(f"/api/cameras/{cam_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert deleted.status_code == 200
    print("[PASS] 4. RBAC Enforcement & Camera Registry CRUD (Add, Health, Update, Delete)")

    # 5. Stream Control (Connect, Restart, Disconnect)
    conn = client.post("/api/cameras/CAM-001/connect", headers={"Authorization": f"Bearer {op_token}"})
    assert conn.status_code == 200, f"Connect failed ({conn.status_code}): {conn.text}"

    rest = client.post("/api/cameras/CAM-001/restart", headers={"Authorization": f"Bearer {op_token}"})
    assert rest.status_code == 200, f"Restart failed ({rest.status_code}): {rest.text}"

    disc = client.post("/api/cameras/CAM-001/disconnect", headers={"Authorization": f"Bearer {op_token}"})
    assert disc.status_code == 200, f"Disconnect failed ({disc.status_code}): {disc.text}"
    print("[PASS] 5. Stream Control by Operator (Connect, Restart, Disconnect)")

    # 6. Audit Trail
    audit_forbidden = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {viewer_token}"})
    assert audit_forbidden.status_code == 403, f"Expected 403 for Viewer audit log access, got {audit_forbidden.status_code}"

    audit_allowed = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_allowed.status_code == 200, f"Admin audit logs failed ({audit_allowed.status_code}): {audit_allowed.text}"
    logs = audit_allowed.json()
    assert len(logs) >= 4, f"Expected >=4 audit entries, found {len(logs)}"
    print(f"[PASS] 6. System Audit Logging & Trail Verification ({len(logs)} audit entries recorded)")

    print("=" * 60)
    print(" ALL 6 PHASE 1 TESTS PASSED SUCCESSFULLY! ")
    print("=" * 60)

if __name__ == "__main__":
    run_verification()
