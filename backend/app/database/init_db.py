from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.camera import Camera

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
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_cameras()
