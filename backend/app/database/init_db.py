from sqlalchemy import text, inspect
from app.database.connection import SessionLocal, engine, Base
from app.models.camera import Camera
from app.models.vehicle_observation import VehicleObservation
from app.models.vehicle_journey import VehicleJourney, JourneyPoint
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.incident_log import IncidentLog
from app.models.incident import Incident
from app.models.traffic import TrafficEvent
from app.models.alert import Alert
from app.models.watchlist import WatchlistRecord, WatchlistAlert
from app.models.worker import EdgeWorker
from app.core.security import get_password_hash
from datetime import datetime, timedelta


def migrate_schema():
    """Ensures all tables and newly added columns exist in PostgreSQL or SQLite."""
    # Ensure all tables exist first
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Iterate over all registered models in Base.metadata
        for table_name, table in Base.metadata.tables.items():
            if table_name in existing_tables:
                existing_cols = {col['name'] for col in inspector.get_columns(table_name)}
                for column in table.columns:
                    if column.name not in existing_cols:
                        col_type = column.type.compile(engine.dialect)
                        sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {col_type}'
                        try:
                            db.execute(text(sql))
                            db.commit()
                            print(f"Migrated: added column {column.name} ({col_type}) to {table_name}")
                        except Exception as add_err:
                            db.rollback()
                            print(f"Note on adding {column.name} to {table_name}: {add_err}")

        # Backfill camera_code and location_name for legacy cameras if null
        try:
            db.execute(text("UPDATE cameras SET camera_code = id WHERE camera_code IS NULL"))
            db.execute(text("UPDATE cameras SET location_name = name WHERE location_name IS NULL"))
            db.execute(text(
                "UPDATE cameras SET department = 'Traffic Police' "
                "WHERE department IS NULL"
            ))
            db.execute(text("UPDATE cameras SET status = 'ONLINE' WHERE status IS NULL"))
            db.execute(text("UPDATE cameras SET enabled = TRUE WHERE enabled IS NULL"))
            db.commit()
        except Exception as update_err:
            db.rollback()
            print(f"Note on backfilling camera defaults: {update_err}")
    except Exception as e:
        print(f"Migration note: {e}")
    finally:
        db.close()


def seed_users():
    db = SessionLocal()
    try:
        users_to_seed = [
            (
                "admin", "admin@trafficguard.ai",
                "admin123", "ADMIN", "Traffic HQ & Command"
            ),
            (
                "operator", "operator@trafficguard.ai",
                "operator123", "OPERATOR", "Traffic Operations Center"
            ),
            (
                "viewer", "viewer@trafficguard.ai",
                "viewer123", "VIEWER", "Public Safety & City Audit"
            )
        ]
        for uname, uemail, upass, urole, udept in users_to_seed:
            user = db.query(User).filter(User.username == uname).first()
            if not user:
                u = User(
                    username=uname,
                    email=uemail,
                    hashed_password=get_password_hash(upass),
                    role=urole,
                    department=udept,
                    is_active=True
                )
                db.add(u)
            else:
                user.role = urole
                user.department = udept
                user.hashed_password = get_password_hash(upass)
        db.commit()
        print("Successfully ensured default users (Admin, Operator, Viewer).")
    except Exception as e:
        print(f"Error seeding users: {e}")
    finally:
        db.close()


def seed_cameras():
    db = SessionLocal()
    try:
        sample_cameras = [
            Camera(
                id="CAM-001",
                camera_code="CAM-001",
                name="Ring Road Majura Gate",
                description="High-speed PTZ camera facing Majura intersection",
                department="Traffic Police",
                vendor="Hikvision",
                model="DS-2CD2043G2-I",
                vms_name="Surat VMS Alpha",
                source_type="RTSP",
                location_name="Majura Gate, Ring Road",
                latitude=21.1838,
                longitude=72.8223,
                rtsp_url="rtsp://admin:pass123@192.168.1.101:554/Streaming/Channels/101",
                credential_reference="CRED_HIK_001",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-002",
                camera_code="CAM-002",
                name="Athwa Gate Circle",
                description="Wide-angle 4K traffic monitoring camera",
                department="Traffic Police",
                vendor="Dahua",
                model="IPC-HFW5842E-ZE",
                vms_name="Surat VMS Alpha",
                source_type="RTSP",
                location_name="Athwa Gate Circle",
                latitude=21.1818,
                longitude=72.8055,
                rtsp_url="rtsp://operator:secure456@192.168.1.102:554/cam/realmonitor",
                credential_reference="CRED_DAHUA_002",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-003",
                camera_code="CAM-003",
                name="Delhi Gate Main Junction",
                description="Heavy congestion surveillance camera",
                department="Municipal Corporation",
                vendor="Axis",
                model="Q3538-LVE",
                vms_name="Surat VMS Beta",
                source_type="RTSP",
                location_name="Delhi Gate, Central Ward",
                latitude=21.1969,
                longitude=72.8313,
                rtsp_url="rtsp://axis_user:axis789@192.168.1.103:554/axis-media/media.amp",
                credential_reference="CRED_AXIS_003",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-004",
                camera_code="CAM-004",
                name="Udhna Darwaja Flyover",
                description="Flyover entrance and transit corridor camera",
                department="Highway Authority",
                vendor="Bosch",
                model="FLEXIDOME IP starlight 8000i",
                vms_name="Surat VMS Beta",
                source_type="RTSP",
                location_name="Udhna Darwaja Flyover South",
                latitude=21.1738,
                longitude=72.8335,
                rtsp_url="rtsp://bosch_svc:bosch004@192.168.1.104:554/rtsp_tunnel",
                credential_reference="CRED_BOSCH_004",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-005",
                camera_code="CAM-005",
                name="Adajan Patiya Intersection",
                description="Suburban arterial connector camera",
                department="Traffic Police",
                vendor="Uniview",
                model="IPC2324EBR-DPZ28",
                vms_name="Surat VMS Alpha",
                source_type="RTSP",
                location_name="Adajan Patiya Crossing",
                latitude=21.1967,
                longitude=72.7938,
                rtsp_url="rtsp://unv_user:unv555@192.168.1.105:554/unicast/c1/s0/live",
                credential_reference="CRED_UNV_005",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-NH48-02",
                camera_code="CAM-NH48-02",
                name="Surat-Kadodara Road Highway",
                description="High-speed national corridor camera with ANPR capability",
                department="Highway Authority",
                vendor="Hikvision",
                model="iDS-2CD7A46G0/P-IZHS",
                vms_name="National Highway VMS",
                source_type="RTSP",
                location_name="NH-48 Kadodara Toll Approach",
                latitude=21.1795,
                longitude=72.8850,
                rtsp_url="rtsp://nhai_admin:nhai2026@192.168.2.101:554/live",
                credential_reference="CRED_NHAI_001",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-CTY-12",
                camera_code="CAM-CTY-12",
                name="Chowk Bazar Heritage Corridor",
                description="Dense pedestrian and mixed vehicular zone camera",
                department="Municipal Corporation",
                vendor="Dahua",
                model="IPC-HDBW5442R-ASE",
                vms_name="City Smart VMS",
                source_type="RTSP",
                location_name="Chowk Bazar Central",
                latitude=21.1980,
                longitude=72.8150,
                rtsp_url="rtsp://smartcity:chowk123@192.168.2.102:554/live",
                credential_reference="CRED_CITY_012",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            ),
            Camera(
                id="CAM-RND-03",
                camera_code="CAM-RND-03",
                name="Athwa Gate Roundabout West",
                description="Roundabout flow and merging lane surveillance",
                department="Traffic Police",
                vendor="Axis",
                model="P1378-LE",
                vms_name="Surat VMS Alpha",
                source_type="RTSP",
                location_name="Athwa Roundabout West",
                latitude=21.1825,
                longitude=72.8040,
                rtsp_url="rtsp://axis_cam:round321@192.168.2.103:554/live",
                credential_reference="CRED_AXIS_033",
                status="ONLINE",
                enabled=True,
                last_seen=datetime.utcnow()
            )
        ]
        for cam in sample_cameras:
            existing = db.query(Camera).filter(
                (Camera.id == cam.id) |
                (Camera.camera_code == cam.camera_code)
            ).first()
            if not existing:
                db.add(cam)
            else:
                existing.camera_code = cam.camera_code
                existing.location_name = cam.location_name
                existing.department = cam.department
                existing.vendor = cam.vendor
                existing.model = cam.model
                existing.vms_name = cam.vms_name
                existing.source_type = cam.source_type
                existing.rtsp_url = cam.rtsp_url
                existing.credential_reference = cam.credential_reference
                existing.status = cam.status
                existing.enabled = cam.enabled
        db.commit()
        print("Successfully ensured CCTV camera seeds.")
    except Exception as e:
        print(f"Error seeding cameras: {e}")
    finally:
        db.close()


def seed_vehicle_observations():
    db = SessionLocal()
    try:
        if db.query(VehicleObservation).count() == 0:
            now = datetime.utcnow()
            sample_obs = [
                VehicleObservation(
                    plate_text="GJ-05-AB-1234", normalized_plate="GJ05AB1234",
                    camera_id="CAM-001", track_id=1,
                    timestamp=now - timedelta(minutes=45),
                    latitude=21.1838, longitude=72.8223,
                    ocr_confidence=0.98, detection_confidence=0.99,
                    vehicle_class="CAR"),
                VehicleObservation(
                    plate_text="GJ-05-AB-1234", normalized_plate="GJ05AB1234",
                    camera_id="CAM-002", track_id=2,
                    timestamp=now - timedelta(minutes=30),
                    latitude=21.1818, longitude=72.8055,
                    ocr_confidence=0.96, detection_confidence=0.99,
                    vehicle_class="CAR"),
                VehicleObservation(
                    plate_text="GJ-05-AB-1234", normalized_plate="GJ05AB1234",
                    camera_id="CAM-003", track_id=3,
                    timestamp=now - timedelta(minutes=10),
                    latitude=21.1969, longitude=72.8313,
                    ocr_confidence=0.97, detection_confidence=0.99,
                    vehicle_class="CAR"),
                VehicleObservation(
                    plate_text="GJ-05-XY-9876", normalized_plate="GJ05XY9876",
                    camera_id="CAM-004", track_id=4,
                    timestamp=now - timedelta(minutes=25),
                    latitude=21.1738, longitude=72.8335,
                    ocr_confidence=0.94, detection_confidence=0.99,
                    vehicle_class="TRUCK"),
                VehicleObservation(
                    plate_text="GJ-05-XY-9876", normalized_plate="GJ05XY9876",
                    camera_id="CAM-001", track_id=5,
                    timestamp=now - timedelta(minutes=5),
                    latitude=21.1838, longitude=72.8223,
                    ocr_confidence=0.95, detection_confidence=0.99,
                    vehicle_class="TRUCK"),
                VehicleObservation(
                    plate_text="GJ-01-TR-4567", normalized_plate="GJ01TR4567",
                    camera_id="CAM-005", track_id=6,
                    timestamp=now - timedelta(minutes=18),
                    latitude=21.1967, longitude=72.7938,
                    ocr_confidence=0.92, detection_confidence=0.99,
                    vehicle_class="CAR"),
                VehicleObservation(
                    plate_text="GJ-05-MC-8812", normalized_plate="GJ05MC8812",
                    camera_id="CAM-002", track_id=7,
                    timestamp=now - timedelta(minutes=12),
                    latitude=21.1818, longitude=72.8055,
                    ocr_confidence=0.91, detection_confidence=0.99,
                    vehicle_class="MOTORCYCLE"),
                VehicleObservation(
                    plate_text="GJ-03-BS-9901", normalized_plate="GJ03BS9901",
                    camera_id="CAM-003", track_id=8,
                    timestamp=now - timedelta(minutes=3),
                    latitude=21.1969, longitude=72.8313,
                    ocr_confidence=0.96, detection_confidence=0.99,
                    vehicle_class="BUS"),
            ]
            db.add_all(sample_obs)
            db.commit()

            # Seed corresponding Journeys
            journey1 = VehicleJourney(
                normalized_plate="GJ05AB1234",
                first_seen=now - timedelta(minutes=45),
                last_seen=now - timedelta(minutes=10)
            )
            journey2 = VehicleJourney(
                normalized_plate="GJ05XY9876",
                first_seen=now - timedelta(minutes=25),
                last_seen=now - timedelta(minutes=5)
            )
            db.add_all([journey1, journey2])
            db.commit()
            db.refresh(journey1)
            db.commit()

            points = [
                JourneyPoint(
                    journey_id=journey1.id, camera_id="CAM-001",
                    timestamp=now - timedelta(minutes=45),
                    latitude=21.1838, longitude=72.8223, confidence=0.98),
                JourneyPoint(
                    journey_id=journey1.id, camera_id="CAM-002",
                    timestamp=now - timedelta(minutes=30),
                    latitude=21.1818, longitude=72.8055, confidence=0.96),
                JourneyPoint(
                    journey_id=journey1.id, camera_id="CAM-003",
                    timestamp=now - timedelta(minutes=10),
                    latitude=21.1969, longitude=72.8313, confidence=0.97),
                JourneyPoint(
                    journey_id=journey2.id, camera_id="CAM-004",
                    timestamp=now - timedelta(minutes=25),
                    latitude=21.1738, longitude=72.8335, confidence=0.94),
                JourneyPoint(
                    journey_id=journey2.id, camera_id="CAM-001",
                    timestamp=now - timedelta(minutes=5),
                    latitude=21.1838, longitude=72.8223, confidence=0.95),
            ]
            db.add_all(points)
            db.commit()

            print("Successfully seeded sample vehicle observations and journeys.")
    except Exception as e:
        print(f"Error seeding vehicle observations: {e}")
    finally:
        db.close()


def seed_audit_logs():
    db = SessionLocal()
    try:
        if db.query(AuditLog).count() == 0:
            initial_logs = [
                AuditLog(
                    username="admin",
                    role="ADMIN",
                    action="SYSTEM_INIT",
                    resource_type="SYSTEM",
                    details="TrafficGuard AI initialized CCTV registry and RBAC",
                    timestamp=datetime.utcnow() - timedelta(hours=1)
                ),
                AuditLog(
                    username="admin",
                    role="ADMIN",
                    action="CAMERA_CREATED",
                    resource_type="CAMERA",
                    resource_id="CAM-001",
                    details="Registered camera Ring Road Majura Gate",
                    timestamp=datetime.utcnow() - timedelta(minutes=50)
                )
            ]
            db.add_all(initial_logs)
            db.commit()
    except Exception as e:
        print(f"Error seeding audit logs: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate_schema()
    seed_users()
    seed_cameras()
    seed_vehicle_observations()
    seed_audit_logs()
