import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from the .env file
load_dotenv()

# The engine is the main entry point to the database, managing connections.
DATABASE_URL = os.getenv("DATABASE_URL")
# New, more resilient line
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# SessionLocal is a factory that will create new, configured database sessions when called.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a declarative base class that our ORM models (tables) will inherit from.
Base = declarative_base()


# FastAPI dependency used to manage database sessions for each API request.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()