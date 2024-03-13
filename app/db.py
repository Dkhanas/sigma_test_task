from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

# Configure SQLAlchemy engine

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
