import os
import sys
import unittest
from fastapi.testclient import TestClient
from main import app
from app.database import init_db

class Phase1TestSuite(unittest.TestCase):
    def setUp(self):
        init_db.seed_users()
        init_db.seed_cameras()
        init_db.seed_vehicle_plates()
        init_db.seed_audit_logs()

    def test_01_health_check(self):
        with TestClient(app) as client:
            res = client.get("/health")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "ok")
            print("[OK] Health check endpoint working")

    def test_02_authentication_and_rbac(self):
        with TestClient(app) as client:
            # 1. Login as Admin
            admin_res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
            self.assertEqual(admin_res.status_code, 200, f"Admin login failed: {admin_res.text}")
            admin_data = admin_res.json()
            self.assertIn("access_token", admin_data)
            self.assertEqual(admin_data["user"]["role"], "ADMIN")
            admin_token = admin_data["access_token"]
            print("[OK] Admin login successful")

            # 2. Login as Operator
            op_res = client.post("/api/auth/login", json={"username": "operator", "password": "operator123"})
            self.assertEqual(op_res.status_code, 200, f"Operator login failed: {op_res.text}")
            op_data = op_res.json()
            self.assertEqual(op_data["user"]["role"], "OPERATOR")
            op_token = op_data["access_token"]
            print("[OK] Operator login successful")

            # 3. Login as Viewer
            viewer_res = client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"})
            self.assertEqual(viewer_res.status_code, 200, f"Viewer login failed: {viewer_res.text}")
            viewer_data = viewer_res.json()
            self.assertEqual(viewer_data["user"]["role"], "VIEWER")
            viewer_token = viewer_data["access_token"]
            print("[OK] Viewer login successful")

            # 4. Profile /me
            me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
            self.assertEqual(me_res.status_code, 200)
            self.assertEqual(me_res.json()["username"], "admin")
            print("[OK] /api/auth/me endpoint verified")

    def test_03_camera_registry_crud_and_rbac(self):
        with TestClient(app) as client:
            admin_token = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
            viewer_token = client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"}).json()["access_token"]

            # Viewer lists cameras (Allowed)
            list_res = client.get("/api/cameras", headers={"Authorization": f"Bearer {viewer_token}"})
            self.assertEqual(list_res.status_code, 200)
            cameras = list_res.json()
            self.assertGreaterEqual(len(cameras), 1)
            print(f"[OK] Camera list returned {len(cameras)} registered cameras")

            # Verify sensitive RTSP password masking
            first_cam = cameras[0]
            if first_cam.get("rtsp_url"):
                self.assertNotIn("pass123", first_cam["rtsp_url"])
                print("[OK] RTSP credentials successfully masked in API responses")

            # Viewer tries to create a camera (Forbidden - 403)
            new_cam_payload = {
                "camera_code": "CAM-TEST-99",
                "name": "Test Junction Surveillance",
                "department": "Traffic Police",
                "vendor": "Axis",
                "model": "Q3538-LVE",
                "vms_name": "Surat VMS Beta",
                "source_type": "MOCK",
                "location_name": "Test Crossing",
                "latitude": 21.1900,
                "longitude": 72.8100,
                "rtsp_url": "mock://test-stream",
                "enabled": True
            }
            forbidden_res = client.post("/api/cameras", json=new_cam_payload, headers={"Authorization": f"Bearer {viewer_token}"})
            self.assertEqual(forbidden_res.status_code, 403)
            print("[OK] RBAC enforced: Viewer forbidden from creating cameras (403)")

            # Admin creates camera (Allowed - 200)
            create_res = client.post("/api/cameras", json=new_cam_payload, headers={"Authorization": f"Bearer {admin_token}"})
            self.assertEqual(create_res.status_code, 200)
            created_cam = create_res.json()
            self.assertEqual(created_cam["camera_code"], "CAM-TEST-99")
            print(f"[OK] Admin created camera {created_cam['camera_code']} ({created_cam['id']})")

            # Health endpoint
            health_res = client.get(f"/api/cameras/{created_cam['id']}/health")
            self.assertEqual(health_res.status_code, 200)
            health_data = health_res.json()
            self.assertEqual(health_data["camera_code"], "CAM-TEST-99")
            print("[OK] Camera health endpoint verified")

            # Admin updates camera
            update_res = client.put(f"/api/cameras/{created_cam['id']}", json={"name": "Updated Test Junction"}, headers={"Authorization": f"Bearer {admin_token}"})
            self.assertEqual(update_res.status_code, 200)
            self.assertEqual(update_res.json()["name"], "Updated Test Junction")
            print("[OK] Admin updated camera metadata")

            # Clean up delete
            del_res = client.delete(f"/api/cameras/{created_cam['id']}", headers={"Authorization": f"Bearer {admin_token}"})
            self.assertEqual(del_res.status_code, 200)
            print("[OK] Admin deleted camera successfully")

    def test_04_camera_stream_control(self):
        with TestClient(app) as client:
            op_token = client.post("/api/auth/login", json={"username": "operator", "password": "operator123"}).json()["access_token"]
            
            # Connect CAM-001
            conn_res = client.post("/api/cameras/CAM-001/connect", headers={"Authorization": f"Bearer {op_token}"})
            self.assertEqual(conn_res.status_code, 200)
            print("[OK] Operator connected camera stream")

            # Restart CAM-001
            restart_res = client.post("/api/cameras/CAM-001/restart", headers={"Authorization": f"Bearer {op_token}"})
            self.assertEqual(restart_res.status_code, 200)
            print("[OK] Operator restarted camera stream")

            # Disconnect CAM-001
            disc_res = client.post("/api/cameras/CAM-001/disconnect", headers={"Authorization": f"Bearer {op_token}"})
            self.assertEqual(disc_res.status_code, 200)
            print("[OK] Operator disconnected camera stream")

    def test_05_audit_logs(self):
        with TestClient(app) as client:
            admin_token = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
            viewer_token = client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"}).json()["access_token"]

            # Viewer cannot view audit logs
            v_res = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {viewer_token}"})
            self.assertEqual(v_res.status_code, 403)
            print("[OK] RBAC enforced: Viewer forbidden from reading audit logs (403)")

            # Admin can view audit logs
            a_res = client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
            self.assertEqual(a_res.status_code, 200)
            logs = a_res.json()
            self.assertGreaterEqual(len(logs), 1)
            actions = [l["action"] for l in logs]
            print(f"[OK] Audit logs verified ({len(logs)} records found, latest actions: {actions[:3]})")

if __name__ == "__main__":
    unittest.main()
