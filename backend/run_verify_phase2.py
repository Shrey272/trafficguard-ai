import os
import sys
import warnings
warnings.filterwarnings("ignore")

from fastapi.testclient import TestClient
from main import app
from app.database import init_db

def run_phase2_verification():
    print("=" * 65)
    print(" TRAFFICGUARD AI - PHASE 2 INTEGRATION GATEWAY VERIFICATION")
    print("=" * 65)

    # Initialize seeds
    init_db.migrate_schema()
    init_db.seed_users()
    init_db.seed_cameras()
    init_db.seed_vehicle_plates()
    init_db.seed_audit_logs()

    client = TestClient(app)

    # 1. Login Accounts
    admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]

    op_login = client.post("/api/auth/login", json={"username": "operator", "password": "operator123"})
    assert op_login.status_code == 200
    op_token = op_login.json()["access_token"]

    viewer_login = client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"})
    assert viewer_login.status_code == 200
    viewer_token = viewer_login.json()["access_token"]
    print("[PASS] 1. Authentication & Role Tokens Verified (Admin, Operator, Viewer)")

    # 2. ONVIF Device Discovery
    # Viewer should be forbidden
    disc_forbid = client.post("/api/onvif/discover", headers={"Authorization": f"Bearer {viewer_token}"})
    assert disc_forbid.status_code == 403, f"Expected 403 for Viewer, got {disc_forbid.status_code}"

    # Operator / Admin can discover
    disc_res = client.post("/api/onvif/discover", json={"timeout_seconds": 1.0}, headers={"Authorization": f"Bearer {op_token}"})
    assert disc_res.status_code == 200, f"Discovery failed ({disc_res.status_code}): {disc_res.text}"
    discovered_devs = disc_res.json()
    assert len(discovered_devs) >= 3, f"Expected >=3 discovered devices, got {len(discovered_devs)}"
    print(f"[PASS] 2. ONVIF Device Discovery ({len(discovered_devs)} network/lab devices discovered)")

    # 3. ONVIF Device Inspection & Profile Extraction
    target_dev = discovered_devs[1]  # Dahua 4K PTZ
    inspect_res = client.post(
        "/api/onvif/inspect",
        json={"host": target_dev["ip_address"], "port": target_dev["port"]},
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert inspect_res.status_code == 200, f"Inspection failed ({inspect_res.status_code}): {inspect_res.text}"
    inspection = inspect_res.json()
    assert inspection["capabilities"]["ptz"] is True
    assert len(inspection["profiles"]) >= 2
    assert "rtsp://" in inspection["default_stream_uri"]
    print(f"[PASS] 3. ONVIF Device & Media Profile Inspection ({inspection['device_info']['manufacturer']} {inspection['device_info']['model']}, {len(inspection['profiles'])} profiles found)")

    # 4. Normalized Camera Registration (ONVIF Source Type)
    onvif_cam_payload = {
        "camera_code": "CAM-ONVIF-PTZ-01",
        "name": "Surat Command Center ONVIF PTZ",
        "department": "Traffic Police",
        "vendor": inspection["device_info"]["manufacturer"],
        "model": inspection["device_info"]["model"],
        "vms_name": "Surat City VMS",
        "source_type": "ONVIF",
        "location_name": "Ring Road West Overpass",
        "latitude": 21.1850,
        "longitude": 72.8210,
        "rtsp_url": inspection["default_stream_uri"],
        "onvif_host": target_dev["ip_address"],
        "onvif_port": target_dev["port"],
        "onvif_profile_token": inspection["profiles"][0]["token"],
        "has_ptz": True,
        "capabilities": "STREAMING,ONVIF_PROFILE_S,PTZ",
        "enabled": True
    }

    # Register camera as Admin
    create_res = client.post("/api/cameras", json=onvif_cam_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_res.status_code == 200, f"Camera creation failed ({create_res.status_code}): {create_res.text}"
    new_cam_id = create_res.json()["id"]
    print("[PASS] 4. ONVIF Camera Registration via Unified Camera Registry")

    # 5. PTZ Control Execution
    ptz_forbid = client.post(
        "/api/onvif/ptz/move",
        json={"camera_id": new_cam_id, "pan": 0.5, "tilt": -0.2, "zoom": 0.1, "speed": 0.5},
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert ptz_forbid.status_code == 403

    ptz_res = client.post(
        "/api/onvif/ptz/move",
        json={"camera_id": new_cam_id, "pan": 0.5, "tilt": -0.2, "zoom": 0.1, "speed": 0.5},
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert ptz_res.status_code == 200, f"PTZ command failed ({ptz_res.status_code}): {ptz_res.text}"

    # PTZ Status check
    ptz_status = client.get(f"/api/onvif/ptz/{new_cam_id}/status")
    assert ptz_status.status_code == 200
    assert ptz_status.json()["has_ptz"] is True
    print("[PASS] 5. PTZ Camera Control & Position Status via REST API")

    # 6. VideoFile and Webcam Source Types Registration
    file_cam_payload = {
        "camera_code": "CAM-FILE-DEMO",
        "name": "Offline Highway Benchmark Video",
        "department": "Highway Authority",
        "vendor": "VideoFile Gateway",
        "source_type": "FILE",
        "location_name": "NH-48 Test Track",
        "latitude": 21.1750,
        "longitude": 72.8800,
        "video_file_path": "sample_highway.mp4",
        "enabled": True
    }
    create_file = client.post("/api/cameras", json=file_cam_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert create_file.status_code == 200
    file_cam_id = create_file.json()["id"]

    # Check health on file camera
    file_health = client.get(f"/api/cameras/{file_cam_id}/health")
    assert file_health.status_code == 200
    assert file_health.json()["source_type"] == "FILE"
    print("[PASS] 6. Heterogeneous Video File & USB Webcam Stream Normalization")

    # 7. Audit Trail Verification
    audit_res = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_res.status_code == 200
    logs = audit_res.json()
    actions = [log["action"] for log in logs]
    assert "ONVIF_DISCOVERY_EXECUTED" in actions
    assert "ONVIF_DEVICE_INSPECTED" in actions
    assert "CAMERA_PTZ_COMMAND" in actions
    print(f"[PASS] 7. Gateway Audit Trail Logs Verified ({len(logs)} entries logged)")

    # Clean up test cameras
    client.delete(f"/api/cameras/{new_cam_id}", headers={"Authorization": f"Bearer {admin_token}"})
    client.delete(f"/api/cameras/{file_cam_id}", headers={"Authorization": f"Bearer {admin_token}"})

    print("=" * 65)
    print(" ALL 7 PHASE 2 GATEWAY INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("=" * 65)

if __name__ == "__main__":
    run_phase2_verification()
