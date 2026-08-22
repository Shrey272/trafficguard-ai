from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.camera import Camera

def seed_cameras():
    db = SessionLocal()
    try:
        # Check if cameras already exist
        if db.query(Camera).count() == 0:
            cameras = [
                Camera(id="CAM-001", name="Downtown Main St", latitude=40.7128, longitude=-74.0060, is_active=True),
                Camera(id="CAM-002", name="Highway 1 North", latitude=40.7306, longitude=-73.9352, is_active=True),
                Camera(id="CAM-003", name="City Center Intersection", latitude=40.7589, longitude=-73.9851, is_active=True),
                Camera(id="CAM-004", name="Westside Bridge", latitude=40.7484, longitude=-73.9857, is_active=True),
                Camera(id="CAM-005", name="Industrial Park Ave", latitude=40.7829, longitude=-73.9654, is_active=True)
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
