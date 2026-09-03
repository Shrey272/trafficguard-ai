import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trafficguard.db")

# Normalize legacy postgres:// scheme to postgresql:// if present
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def create_db_engine():
    global DATABASE_URL
    if "sqlite" in DATABASE_URL:
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        try:
            # Attempt Postgres connection with fast timeout
            eng = create_engine(
                DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=1800,
                connect_args={"connect_timeout": 3}
            )
            # Test connection
            with eng.connect():
                pass
            return eng
        except Exception as e:
            logger.warning(
                f"Could not connect to PostgreSQL ({e}). "
                "Falling back to local SQLite database."
            )
            DATABASE_URL = "sqlite:///./trafficguard.db"
            return create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False}
            )


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
