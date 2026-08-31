import os
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from dotenv import load_dotenv, find_dotenv  # type: ignore


load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/trafficguard")

# Normalize legacy postgres:// scheme to postgresql:// if present
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # High-performance connection pool settings for PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

