# app/database.py
# This file sets up the connection to our SQLite database.
# SQLite stores everything in a single file (taskapi.db) — no server needed.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This tells SQLAlchemy to use SQLite and save data in a file called taskapi.db
DATABASE_URL = "sqlite:///./taskapi.db"

# connect_args is SQLite-specific — it allows multiple threads to use the DB safely
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Each request gets its own database session, then it closes when done
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our database models will inherit from
Base = declarative_base()


# This is a "dependency" — FastAPI calls this for every request that needs the DB
# It opens a session, gives it to the route, then closes it when done (the finally block)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
