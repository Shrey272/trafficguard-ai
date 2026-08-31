from sqlalchemy.orm import Session  # type: ignore
from app.database.connection import SessionLocal  # type: ignore
from app.models.camera import Camera  # type: ignore
from app.models.vehicle_plate import VehiclePlate  # type: ignore
from datetime import datetime, timedelta

def seed_cameras():
    db = SessionLocal()
    try:
        # Check if cameras already exist
        if db.query(Camera).count() == 0:
            cameras = [
                Camera(id="CAM-001", name="Ring Road Majura Gate", latitude=21.1838, longitude=72.8223, is_active=True),
                Camera(id="CAM-002", name="Athwa Gate", latitude=21.1818, longitude=72.8055, is_active=True),
                Camera(id="CAM-003", name="Delhi Gate", latitude=21.1969, longitude=72.8313, is_active=True),
                Camera(id="CAM-004", name="Udhna Darwaja", latitude=21.1738, longitude=72.8335, is_active=True),
                Camera(id="CAM-005", name="Adajan Patiya", latitude=21.1967, longitude=72.7938, is_active=True)
            ]
            db.add_all(cameras)
            db.commit()
            print("Successfully seeded 5 cameras.")
    except Exception as e:
        print(f"Error seeding cameras: {e}")
    finally:
        db.close()

def seed_vehicle_plates():
    db = SessionLocal()
    try:
        if db.query(VehiclePlate).count() == 0:
            now = datetime.utcnow()
            sample_plates = [
                # Vehicle 1: Multi-camera movement timeline (GJ-05-AB-1234)
                VehiclePlate(plate_number="GJ-05-AB-1234", camera_id="CAM-001", camera_name="Ring Road Majura Gate", timestamp=now - timedelta(minutes=45), latitude=21.1838, longitude=72.8223, vehicle_type="Car", confidence=98.2, status="NORMAL"),
                VehiclePlate(plate_number="GJ-05-AB-1234", camera_id="CAM-002", camera_name="Athwa Gate", timestamp=now - timedelta(minutes=30), latitude=21.1818, longitude=72.8055, vehicle_type="Car", confidence=96.7, status="NORMAL"),
                VehiclePlate(plate_number="GJ-05-AB-1234", camera_id="CAM-003", camera_name="Delhi Gate", timestamp=now - timedelta(minutes=10), latitude=21.1969, longitude=72.8313, vehicle_type="Car", confidence=97.5, status="NORMAL"),

                # Vehicle 2: Flagged/Suspicious vehicle (GJ-05-XY-9876)
                VehiclePlate(plate_number="GJ-05-XY-9876", camera_id="CAM-004", camera_name="Udhna Darwaja", timestamp=now - timedelta(minutes=25), latitude=21.1738, longitude=72.8335, vehicle_type="SUV", confidence=94.1, status="FLAGGED"),
                VehiclePlate(plate_number="GJ-05-XY-9876", camera_id="CAM-001", camera_name="Ring Road Majura Gate", timestamp=now - timedelta(minutes=5), latitude=21.1838, longitude=72.8223, vehicle_type="SUV", confidence=95.8, status="FLAGGED"),

                # Additional realistic plates
                VehiclePlate(plate_number="GJ-01-TR-4567", camera_id="CAM-005", camera_name="Adajan Patiya", timestamp=now - timedelta(minutes=18), latitude=21.1967, longitude=72.7938, vehicle_type="Truck", confidence=92.4, status="NORMAL"),
                VehiclePlate(plate_number="GJ-05-MC-8812", camera_id="CAM-002", camera_name="Athwa Gate", timestamp=now - timedelta(minutes=12), latitude=21.1818, longitude=72.8055, vehicle_type="Motorcycle", confidence=91.0, status="NORMAL"),
                VehiclePlate(plate_number="GJ-03-BS-9901", camera_id="CAM-003", camera_name="Delhi Gate", timestamp=now - timedelta(minutes=3), latitude=21.1969, longitude=72.8313, vehicle_type="Bus", confidence=96.0, status="NORMAL")
            ]
            db.add_all(sample_plates)
            db.commit()
            print("Successfully seeded sample ANPR vehicle plates.")
    except Exception as e:
        print(f"Error seeding vehicle plates: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_cameras()
    seed_vehicle_plates()

