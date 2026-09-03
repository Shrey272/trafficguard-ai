import unittest
from fastapi.testclient import TestClient
from main import app
from app.database import init_db

class TestPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db.seed_users()
        init_db.seed_cameras()
        init_db.seed_vehicle_plates()
        init_db.seed_audit_logs()
        cls.client = TestClient(app)

    def test_01_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        print("[PASS] 1. Health check endpoint")

    def test_02_authentication(self):
        # 1. Admin login
        admin_res = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(admin_res.status_code, 200)
        self.admin_token = admin_res.json()["access_token"]
        self.assertEqual(admin_res.json()["user"]["role"], "ADMIN")

        # 2. Operator login
        op_res = self.client.post("/api/auth/login", json={"username": "operator", "password": "operator123"})
        self.assertEqual(op_res.status_code, 200)
        self.op_token = op_res.json()["access_token"]
        self.assertEqual(op_res.json()["user"]["role"], "OPERATOR")

        # 3. Viewer login
        v_res = self.client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"})
        self.assertEqual(v_res.status_code, 200)
        self.v_token = v_res.json()["access_token"]
        self.assertEqual(v_res.json()["user"]["role"], "VIEWER")

        # 4. Bad password check
        bad_res = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
        self.assertEqual(bad_res.status_code, 401)
        print("[PASS] 2. Authentication & JWT Tokens (Admin, Operator, Viewer)")

    def test_03_camera_registry_and_rbac(self):
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
        viewer_token = self.client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"}).json()["access_token"]

        # 1. List cameras (Allowed for viewer)
        cams_res = self.client.get("/api/cameras", headers={"Authorization": f"Bearer {viewer_token}"})
        self.assertEqual(cams_res.status_code, 200)
        cams = cams_res.json()
        self.assertGreaterEqual(len(cams), 1)

        # Verify RTSP username/password masking
        for c in cams:
            if c.get("rtsp_url"):
                self.assertNotIn("pass123", c["rtsp_url"])
                self.assertNotIn("secure456", c["rtsp_url"])

        # 2. Viewer forbidden from creating camera (RBAC check)
        cam_payload = {
            "camera_code": "CAM-UNIT-TEST-1",
            "name": "Integration Test Cam",
            "department": "Traffic Police",
            "vendor": "Uniview",
            "model": "IPC2324EBR-DPZ28",
            "vms_name": "Surat VMS Alpha",
            "source_type": "MOCK",
            "location_name": "Varachha Main Road",
            "latitude": 21.2150,
            "longitude": 72.8500,
            "rtsp_url": "mock://live-stream-feed",
            "enabled": True
        }
        forbidden_res = self.client.post("/api/cameras", json=cam_payload, headers={"Authorization": f"Bearer {viewer_token}"})
        self.assertEqual(forbidden_res.status_code, 403)

        # 3. Admin allowed to create camera
        create_res = self.client.post("/api/cameras", json=cam_payload, headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(create_res.status_code, 200)
        created_cam = create_res.json()
        self.assertEqual(created_cam["camera_code"], "CAM-UNIT-TEST-1")

        # 4. Health endpoint
        health_res = self.client.get(f"/api/cameras/{created_cam['id']}/health")
        self.assertEqual(health_res.status_code, 200)

        # 5. Admin updates camera
        upd_res = self.client.put(f"/api/cameras/{created_cam['id']}", json={"name": "Renamed Test Cam"}, headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(upd_res.status_code, 200)
        self.assertEqual(upd_res.json()["name"], "Renamed Test Cam")

        # 6. Admin deletes camera
        del_res = self.client.delete(f"/api/cameras/{created_cam['id']}", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(del_res.status_code, 200)
        print("[PASS] 3. Camera Registry CRUD, RTSP Masking & RBAC Restrictions")

    def test_04_stream_lifecycle_actions(self):
        op_token = self.client.post("/api/auth/login", json={"username": "operator", "password": "operator123"}).json()["access_token"]
        
        # Connect
        res1 = self.client.post("/api/cameras/CAM-001/connect", headers={"Authorization": f"Bearer {op_token}"})
        self.assertEqual(res1.status_code, 200)

        # Restart
        res2 = self.client.post("/api/cameras/CAM-001/restart", headers={"Authorization": f"Bearer {op_token}"})
        self.assertEqual(res2.status_code, 200)

        # Disconnect
        res3 = self.client.post("/api/cameras/CAM-001/disconnect", headers={"Authorization": f"Bearer {op_token}"})
        self.assertEqual(res3.status_code, 200)
        print("[PASS] 4. Camera Stream Lifecycle (Connect, Restart, Disconnect)")

    def test_05_audit_logs(self):
        admin_token = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"}).json()["access_token"]
        viewer_token = self.client.post("/api/auth/login", json={"username": "viewer", "password": "viewer123"}).json()["access_token"]

        # Viewer forbidden
        v_res = self.client.get("/api/audit-logs", headers={"Authorization": f"Bearer {viewer_token}"})
        self.assertEqual(v_res.status_code, 403)

        # Admin authorized
        a_res = self.client.get("/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(a_res.status_code, 200)
        logs = a_res.json()
        self.assertGreaterEqual(len(logs), 1)
        print(f"[PASS] 5. System Audit Trail ({len(logs)} entries logged)")

if __name__ == "__main__":
    unittest.main()
