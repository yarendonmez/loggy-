from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database import get_db, create_tables, LogFile, LogEntry, AnalysisResult

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Akıllı Log Asistanı API",
    description="AI Tabanlı Log Analizi ve Anomali Tespit Sistemi",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Akıllı Log Asistanı API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "model": "loaded"
    }

@app.get("/api/version")
async def get_version():
    """Get API version"""
    return {
        "version": "1.0.0",
        "build_date": "2025-07-26"
    }

@app.get("/api/db/test")
async def test_database(db: Session = Depends(get_db)):
    """Test database connection and create sample data"""
    try:
        # Test basic connection
        db.execute("SELECT 1")
        
        # Create a test log file entry
        test_log = LogFile(
            filename="test.log",
            file_size=1024,
            total_lines=100,
            anomaly_count=5,
            file_path="/test/path"
        )
        db.add(test_log)
        db.commit()
        
        # Get the count of log files
        log_count = db.query(LogFile).count()
        
        return {
            "status": "success",
            "message": "Database connection and operations working",
            "log_files_count": log_count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database error: {str(e)}"
        }

@app.post("/api/upload")
async def upload_log_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload log file for analysis"""
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.log', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Sadece .csv, .log ve .txt dosyaları desteklenir")
        
        # Validate file size (50MB limit)
        if file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Dosya boyutu 50MB'dan küçük olmalıdır")
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Count lines in file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for _ in f)
        
        # Create database entry
        log_file = LogFile(
            filename=file.filename,
            file_size=file.size,
            total_lines=line_count,
            anomaly_count=0,  # Will be updated after analysis
            file_path=file_path
        )
        db.add(log_file)
        db.commit()
        db.refresh(log_file)
        
        return {
            "status": "success",
            "message": "Dosya başarıyla yüklendi",
            "file_id": log_file.id,
            "filename": file.filename,
            "file_size": file.size,
            "total_lines": line_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya yükleme hatası: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 