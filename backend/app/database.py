from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/loggy.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database Models
class LogFile(Base):
    __tablename__ = "log_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, error
    total_lines = Column(Integer, default=0)
    anomaly_count = Column(Integer, default=0)
    file_path = Column(String)

class LogEntry(Base):
    __tablename__ = "log_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    log_file_id = Column(Integer, index=True)
    line_number = Column(Integer)
    timestamp = Column(DateTime, nullable=True)
    log_level = Column(String)
    message = Column(Text)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    anomaly_type = Column(String, nullable=True)
    severity = Column(String, default="info")  # info, warning, error, critical

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    log_file_id = Column(Integer, index=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)
    total_anomalies = Column(Integer, default=0)
    critical_anomalies = Column(Integer, default=0)
    processing_time = Column(Float)
    model_accuracy = Column(Float, nullable=True)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine) 