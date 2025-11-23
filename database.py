"""Database setup for MovieServices using SQLAlchemy.

Environment:
  - DATABASE_URL: SQLAlchemy connection string (default: sqlite:///./movies.db)
"""

import os

from sqlalchemy import create_engine, Column, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

# --- CONFIGURATION START ---
DB_USER = "mysql-movies-user"
DB_PASSWORD = ""     
DB_HOST = "35.225.220.144"          
DB_PORT = "3306"
DB_NAME = "movies"        

# Connection String Format: dialect+driver://username:password@host:port/database
DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# --- CONFIGURATION END ---

# Create engine
engine = create_engine(
    DATABASE_URI,
    # 'pool_pre_ping' is crucial for Cloud SQL to handle dropped connections automatically
    pool_pre_ping=True, 
    # Recycles connections before the cloud firewall cuts them off
    pool_recycle=1800, 
    # Set to True to see raw SQL queries in your terminal (great for debugging)
    echo=True  
)

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()
Base.query = db_session.query_property()


class DatabaseManager:
    def __init__(self):
        self.Base = Base
        self.session = db_session
        self.engine = engine

    def init_app(self, app):
        pass

    def create_all(self):
        self.Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.Base.metadata.drop_all(bind=self.engine)


db = DatabaseManager()


def get_db():
    db_inst = SessionLocal()
    try:
        yield db_inst
    finally:
        db_inst.close()
