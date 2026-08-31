"""
TrafficGuard AI - SQLite to PostgreSQL Data Migration Script
Transfers existing records from trafficguard.db (SQLite) into PostgreSQL.
"""

import os
import sys

# Ensure backend directory is in sys.path before loading app modules
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv, find_dotenv  # type: ignore
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from app.database.connection import Base, DATABASE_URL as PG_DATABASE_URL  # type: ignore
from app.models.camera import Camera  # type: ignore
from app.models.incident import Incident  # type: ignore
from app.models.traffic import TrafficEvent  # type: ignore
from app.models.alert import Alert  # type: ignore


def migrate_sqlite_to_postgres(sqlite_path="trafficguard.db"):
    if not os.path.exists(sqlite_path):
        print(f"[SKIP] SQLite database file '{sqlite_path}' not found. Nothing to migrate.")
        return

    sqlite_url = f"sqlite:///{sqlite_path}"
    print(f"[*] Source SQLite DB: {sqlite_url}")
    print(f"[*] Target PostgreSQL DB: {PG_DATABASE_URL}")

    if "sqlite" in PG_DATABASE_URL:
        print("[ERROR] Target DATABASE_URL is set to SQLite. Please update .env DATABASE_URL to a PostgreSQL URL before running migration.")
        return

    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    pg_engine = create_engine(PG_DATABASE_URL, pool_pre_ping=True)

    # Ensure tables exist in PostgreSQL
    print("[*] Creating schema in PostgreSQL if not already present...")
    Base.metadata.create_all(bind=pg_engine)

    SqliteSession = sessionmaker(bind=sqlite_engine)
    PgSession = sessionmaker(bind=pg_engine)

    sqlite_db = SqliteSession()
    pg_db = PgSession()

    try:
        # Migrate Cameras
        cameras = sqlite_db.query(Camera).all()
        cam_count = 0
        for c in cameras:
            if not pg_db.query(Camera).filter(Camera.id == c.id).first():
                pg_db.add(Camera(
                    id=c.id,
                    name=c.name,
                    latitude=c.latitude,
                    longitude=c.longitude,
                    is_active=c.is_active,
                    video_url=c.video_url
                ))
                cam_count += 1
        pg_db.commit()
        print(f"[+] Migrated {cam_count} new Cameras.")

        # Migrate Incidents
        incidents = sqlite_db.query(Incident).all()
        inc_count = 0
        for i in incidents:
            if not pg_db.query(Incident).filter(Incident.id == i.id).first():
                pg_db.add(Incident(
                    id=i.id,
                    camera_id=i.camera_id,
                    incident_type=i.incident_type,
                    severity=i.severity,
                    confidence=i.confidence,
                    latitude=i.latitude,
                    longitude=i.longitude,
                    timestamp=i.timestamp,
                    vehicle_count=i.vehicle_count,
                    status=i.status,
                    description=i.description
                ))
                inc_count += 1
        pg_db.commit()
        print(f"[+] Migrated {inc_count} new Incidents.")

        # Migrate Traffic Events
        traffic_events = sqlite_db.query(TrafficEvent).all()
        tr_count = 0
        for t in traffic_events:
            if not pg_db.query(TrafficEvent).filter(TrafficEvent.id == t.id).first():
                pg_db.add(TrafficEvent(
                    id=t.id,
                    camera_id=t.camera_id,
                    timestamp=t.timestamp,
                    total_vehicles=t.total_vehicles,
                    congestion_status=t.congestion_status
                ))
                tr_count += 1
        pg_db.commit()
        print(f"[+] Migrated {tr_count} new Traffic Events.")

        # Migrate Alerts
        alerts = sqlite_db.query(Alert).all()
        alt_count = 0
        for a in alerts:
            if not pg_db.query(Alert).filter(Alert.id == a.id).first():
                pg_db.add(Alert(
                    id=a.id,
                    incident_id=a.incident_id,
                    message=a.message,
                    timestamp=a.timestamp,
                    recipient=a.recipient,
                    status=a.status
                ))
                alt_count += 1
        pg_db.commit()
        print(f"[+] Migrated {alt_count} new Alerts.")

        print("\n[SUCCESS] Migration from SQLite to PostgreSQL completed successfully!")

    except Exception as e:
        pg_db.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
    finally:
        sqlite_db.close()
        pg_db.close()

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    sqlite_db_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "trafficguard.db")
    migrate_sqlite_to_postgres(sqlite_db_file)
