import unittest

from app.models.camera import Camera
from app.camera.rtsp_adapter import RTSPCameraAdapter
from app.camera.onvif_adapter import ONVIFCameraAdapter
from app.camera.file_adapter import VideoFileAdapter
from app.camera.webcam_adapter import WebcamAdapter
from app.camera.vms_adapter import VendorVMSAdapter
from app.camera.vendor_sdk_adapter import VendorSDKAdapter
from app.camera.adapter_factory import AdapterFactory
from app.camera.onvif_service import onvif_service


class TestPhase2Gateway(unittest.TestCase):

    def setUp(self):
        self.rtsp_cam = Camera(
            id="CAM-TEST-RTSP",
            camera_code="CAM-TEST-RTSP",
            name="Test RTSP",
            source_type="RTSP",
            location_name="Test Loc",
            latitude=21.18,
            longitude=72.82,
            rtsp_url="rtsp://admin:pass@192.168.1.50:554/live"
        )
        self.onvif_cam = Camera(
            id="CAM-TEST-ONVIF",
            camera_code="CAM-TEST-ONVIF",
            name="Test ONVIF PTZ",
            source_type="ONVIF",
            location_name="ONVIF Junction",
            latitude=21.19,
            longitude=72.81,
            onvif_host="192.168.1.121",
            onvif_port=80,
            onvif_profile_token="Profile_1_Main",
            has_ptz=True
        )
        self.file_cam = Camera(
            id="CAM-TEST-FILE",
            camera_code="CAM-TEST-FILE",
            name="Test Video Loop",
            source_type="FILE",
            location_name="Video Track",
            latitude=21.20,
            longitude=72.80,
            video_file_path="sample_traffic.mp4"
        )
        self.webcam_cam = Camera(
            id="CAM-TEST-WEBCAM",
            camera_code="CAM-TEST-WEBCAM",
            name="Test USB Webcam",
            source_type="WEBCAM",
            location_name="Control Room",
            latitude=21.17,
            longitude=72.83,
            device_index=0
        )
        self.vms_cam = Camera(
            id="CAM-TEST-VMS",
            camera_code="CAM-TEST-VMS",
            name="Test Milestone VMS",
            source_type="VMS",
            location_name="VMS Bridge",
            latitude=21.16,
            longitude=72.84,
            vms_name="Milestone XProtect"
        )
        self.sdk_cam = Camera(
            id="CAM-TEST-SDK",
            camera_code="CAM-TEST-SDK",
            name="Test Hikvision SDK",
            source_type="SDK",
            location_name="SDK Bridge",
            latitude=21.15,
            longitude=72.85,
            vendor="Hikvision"
        )

    def test_1_adapter_selection_factory(self):
        """Test AdapterFactory correctly instantiates normalized adapter classes."""
        adapter_rtsp = AdapterFactory.create_adapter(self.rtsp_cam)
        self.assertIsInstance(adapter_rtsp, RTSPCameraAdapter)
        self.assertEqual(adapter_rtsp.source_type, "RTSP")

        adapter_onvif = AdapterFactory.create_adapter(self.onvif_cam)
        self.assertIsInstance(adapter_onvif, ONVIFCameraAdapter)
        self.assertEqual(adapter_onvif.source_type, "ONVIF")
        self.assertTrue(adapter_onvif.has_ptz)

        adapter_file = AdapterFactory.create_adapter(self.file_cam)
        self.assertIsInstance(adapter_file, VideoFileAdapter)
        self.assertEqual(adapter_file.source_type, "FILE")

        adapter_webcam = AdapterFactory.create_adapter(self.webcam_cam)
        self.assertIsInstance(adapter_webcam, WebcamAdapter)
        self.assertEqual(adapter_webcam.source_type, "WEBCAM")

        adapter_vms = AdapterFactory.create_adapter(self.vms_cam)
        self.assertIsInstance(adapter_vms, VendorVMSAdapter)

        adapter_sdk = AdapterFactory.create_adapter(self.sdk_cam)
        self.assertIsInstance(adapter_sdk, VendorSDKAdapter)

    def test_2_onvif_device_discovery(self):
        """Test ONVIF WS-Discovery network probe and device metadata retrieval."""
        devices = onvif_service.discover_devices(timeout_seconds=0.5)
        self.assertGreaterEqual(len(devices), 3)

        dahua_dev = next(
            (d for d in devices if "Dahua" in (d.vendor or "")), None
        )
        self.assertIsNotNone(dahua_dev)
        self.assertTrue(dahua_dev.has_ptz)
        self.assertEqual(dahua_dev.port, 80)
        self.assertIn("Profile/S", " ".join(dahua_dev.scopes))

    def test_3_onvif_profile_inspection_and_stream_uri(self):
        """Test inspecting ONVIF device media profiles and resolving RTSP stream URI."""
        inspection = onvif_service.inspect_device(host="192.168.1.121", port=80)
        self.assertEqual(inspection.device_info.manufacturer, "Dahua")
        self.assertTrue(inspection.capabilities.ptz)
        self.assertTrue(inspection.capabilities.streaming)
        self.assertGreaterEqual(len(inspection.profiles), 2)

        main_profile = inspection.profiles[0]
        self.assertEqual(main_profile.resolution_width, 1920)
        self.assertEqual(main_profile.resolution_height, 1080)
        self.assertTrue(main_profile.stream_uri.startswith("rtsp://"))

    def test_4_unsupported_profiles_fallback(self):
        """Test ONVIF adapter gracefully falls back when an unsupported profile token is given."""
        bad_profile_cam = Camera(
            id="CAM-UNSUPP-PROF",
            camera_code="CAM-UNSUPP-PROF",
            name="Unsupp Prof Cam",
            source_type="ONVIF",
            location_name="Test",
            latitude=21.0,
            longitude=72.0,
            onvif_host="192.168.1.120",
            onvif_profile_token="INVALID_NON_EXISTENT_PROFILE_TOKEN"
        )
        adapter = AdapterFactory.create_adapter(bad_profile_cam)
        success = adapter.connect()
        self.assertTrue(success)
        self.assertEqual(adapter.status, "ONLINE")
        adapter.disconnect()

    def test_5_authentication_failure_handling(self):
        """Test ONVIF inspection properly rejects invalid credentials."""
        with self.assertRaises(ValueError) as ctx:
            onvif_service.inspect_device(
                host="192.168.1.120",
                port=80,
                username="invalid_user",
                password="wrong_password"
            )
        self.assertIn("Unauthorized", str(ctx.exception))

    def test_6_offline_and_malformed_configuration(self):
        """Test malformed host error handling."""
        with self.assertRaises(ValueError) as ctx:
            onvif_service.inspect_device(host="invalid_host")
        self.assertIn("Connection Error", str(ctx.exception))

    def test_7_file_adapter_lifecycle(self):
        """Test VideoFileAdapter connection, frame capture, loop, and disconnection."""
        file_adapter = VideoFileAdapter(
            camera_id="CAM-FILE-LIFECYCLE",
            camera_code="CAM-FILE-LIFECYCLE",
            video_file_path="non_existent_demo.mp4",
            target_fps=30.0
        )
        self.assertTrue(file_adapter.connect())
        self.assertTrue(file_adapter.is_connected())

        import time
        time.sleep(0.2)
        frame = file_adapter.read_frame()
        self.assertIsNotNone(frame)

        health = file_adapter.get_health()
        self.assertEqual(health["status"], "ONLINE")
        self.assertEqual(health["source_type"], "FILE")
        self.assertTrue(file_adapter.disconnect())
        self.assertEqual(file_adapter.status, "OFFLINE")

    def test_8_ptz_capability_and_movement(self):
        """Test PTZ execution on PTZ-capable vs fixed cameras."""
        ptz_adapter = AdapterFactory.create_adapter(self.onvif_cam)
        self.assertTrue(ptz_adapter.has_ptz)
        self.assertTrue(ptz_adapter.ptz_move(pan=0.5, tilt=-0.2, zoom=0.1, speed=0.5))

        fixed_adapter = AdapterFactory.create_adapter(self.rtsp_cam)
        self.assertFalse(fixed_adapter.has_ptz)
        self.assertFalse(fixed_adapter.ptz_move(pan=0.5, tilt=-0.2, zoom=0.1, speed=0.5))


if __name__ == "__main__":
    unittest.main()
