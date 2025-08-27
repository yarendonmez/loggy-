from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
import math
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database import get_db, create_tables, LogFile, LogEntry, AnalysisResult
from .ml_model import anomaly_detector
import pandas as pd
import json
from datetime import datetime

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
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Test LLM connection
    llm_status = "ready" if anomaly_detector.is_ready else "not_ready"
    
    return {
        "status": "healthy",
        "database": db_status,
        "llm": llm_status,
        "model": "llama3.2"
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
        db.execute(text("SELECT 1"))
        
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
        upload_dir = os.path.join(os.getcwd(), "uploads")
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
            anomaly_count=None,  # NULL = not analyzed, will be updated after analysis
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

@app.get("/api/files")
async def get_uploaded_files(db: Session = Depends(get_db)):
    """Yüklenen dosyaları listele"""
    try:
        files = db.query(LogFile).order_by(LogFile.upload_date.desc()).all()
        return {
            "status": "success",
            "files": [
                {
                    "id": file.id,
                    "filename": file.filename,
                    "file_size": file.file_size,
                    "total_lines": file.total_lines,
                    "anomaly_count": file.anomaly_count,
                    "created_at": file.upload_date.isoformat(),
                    "is_analyzed": file.anomaly_count is not None
                }
                for file in files
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya listesi hatası: {str(e)}")

@app.post("/api/analyze/{file_id}")
async def analyze_log_file(file_id: int, analysis_type: str = "fast", db: Session = Depends(get_db)):
    """Log dosyasını analiz et"""
    try:
        # Dosyayı bul
        log_file = db.query(LogFile).filter(LogFile.id == file_id).first()
        if not log_file:
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
        # Dosyayı oku
        if not os.path.exists(log_file.file_path):
            raise HTTPException(status_code=404, detail="Dosya sistem üzerinde bulunamadı")
        
        # Log satırlarını oku
        log_lines = []
        with open(log_file.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if not log_lines:
            raise HTTPException(status_code=400, detail="Dosya boş veya okunamadı")
        
        # İlk kez analiz ediyorsa, modeli eğit
        if not anomaly_detector.is_trained:
            training_result = anomaly_detector.train_model(log_lines[:1000])  # İlk 1000 satırla eğit
            if training_result["status"] != "success":
                raise HTTPException(status_code=500, detail=f"Model eğitimi başarısız: {training_result.get('message', 'Bilinmeyen hata')}")
        
        # Analiz yap (analiz türünü geç)
        analysis_result = anomaly_detector.predict(log_lines, analysis_type=analysis_type)
        
        if analysis_result["status"] != "success":
            raise HTTPException(status_code=500, detail=f"Analiz başarısız: {analysis_result.get('message', 'Bilinmeyen hata')}")
        
        # Veritabanını güncelle
        log_file.anomaly_count = analysis_result["anomaly_count"]
        db.commit()
        
        # Analiz sonuçlarını kaydet
        analysis_record = AnalysisResult(
            log_file_id=file_id,
            total_lines=analysis_result["total_lines"],
            anomaly_count=analysis_result["anomaly_count"],
            critical_count=analysis_result["critical_count"],
            anomaly_rate=analysis_result["anomaly_rate"],
            confidence_score=analysis_result.get("confidence_score", 0.0),
            results_json=json.dumps(analysis_result["results"], ensure_ascii=False)
        )
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        # Güvenlik raporunu da dosyaya kaydet
        if "security_report" in analysis_result:
            log_file.security_report_json = json.dumps(analysis_result["security_report"], ensure_ascii=False)
            db.commit()
        
        return {
            "status": "success",
            "message": "Analiz tamamlandı",
            "analysis_id": analysis_record.id,
            "summary": {
                "total_lines": analysis_result["total_lines"],
                "anomaly_count": analysis_result["anomaly_count"],
                "critical_count": analysis_result["critical_count"],
                "anomaly_rate": round(analysis_result["anomaly_rate"] * 100, 2) if analysis_result.get("anomaly_rate") is not None and not math.isnan(analysis_result["anomaly_rate"]) else None,
                "confidence_score": analysis_result.get("confidence_score", 0.0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz hatası: {str(e)}")

@app.get("/api/analysis/{file_id}/results")
async def get_analysis_results(file_id: int, page: int = 1, page_size: int = 50, severity_filter: str = None, db: Session = Depends(get_db)):
    """Dosya için analiz sonuçlarını getir"""
    try:
        # Dosya için en son analiz kaydını bul
        analysis = db.query(AnalysisResult).filter(AnalysisResult.log_file_id == file_id).order_by(AnalysisResult.analysis_date.desc()).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Bu dosya için analiz sonucu bulunamadı")
        
        # JSON sonuçları parse et
        results = json.loads(analysis.results_json)
        
        # Filtreleme
        if severity_filter and severity_filter != "all":
            if severity_filter == "anomalies":
                results = [r for r in results if r["is_anomaly"]]
            else:
                results = [r for r in results if r["severity"] == severity_filter]
        
        # Sayfalama
        total_results = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
        return {
            "status": "success",
            "file_id": file_id,
            "analysis_id": analysis.id,
            "total_results": total_results,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_results + page_size - 1) // page_size,
            "summary": {
                "total_lines": analysis.total_lines,
                "anomaly_count": analysis.anomaly_count,
                "critical_count": analysis.critical_count,
                "anomaly_rate": round(analysis.anomaly_rate * 100, 2) if analysis.anomaly_rate is not None and not math.isnan(analysis.anomaly_rate) else None,
                "confidence_score": analysis.confidence_score if analysis.confidence_score is not None else 0.0
            },
            "results": paginated_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sonuç getirme hatası: {str(e)}")

@app.get("/api/file/{file_id}/preview")
async def preview_log_file(file_id: int, lines: int = 10, db: Session = Depends(get_db)):
    """Log dosyasının ilk birkaç satırını önizle"""
    try:
        # Dosyayı bul
        log_file = db.query(LogFile).filter(LogFile.id == file_id).first()
        if not log_file:
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        
        if not os.path.exists(log_file.file_path):
            raise HTTPException(status_code=404, detail="Dosya sistem üzerinde bulunamadı")
        
        # İlk N satırı oku
        preview_lines = []
        with open(log_file.file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= lines:
                    break
                preview_lines.append({
                    "line_number": i + 1,
                    "content": line.strip()
                })
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": log_file.filename,
            "total_lines": log_file.total_lines,
            "preview_lines": len(preview_lines),
            "lines": preview_lines
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Önizleme hatası: {str(e)}")

@app.get("/api/reports")
async def get_reports(db: Session = Depends(get_db)):
    """Güvenlik raporlarını listele"""
    try:
        files = db.query(LogFile).filter(
            LogFile.security_report_json.isnot(None)
        ).order_by(LogFile.upload_date.desc()).all()
        
        reports = []
        for file in files:
            try:
                security_report = json.loads(file.security_report_json) if file.security_report_json else None
                reports.append({
                    "id": file.id,
                    "filename": file.filename,
                    "created_at": file.upload_date.isoformat(),
                    "security_report": security_report
                })
            except json.JSONDecodeError:
                continue
        
        return {
            "status": "success",
            "reports": reports
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rapor listesi hatası: {str(e)}")

@app.get("/api/reports/{report_id}")
async def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    """Rapor detayını getir"""
    try:
        file = db.query(LogFile).filter(LogFile.id == report_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="Rapor bulunamadı")
        
        if not file.security_report_json:
            raise HTTPException(status_code=404, detail="Bu dosya için güvenlik raporu yok")
        
        security_report = json.loads(file.security_report_json)
        
        return {
            "status": "success",
            "report": {
                "id": file.id,
                "filename": file.filename,
                "created_at": file.upload_date.isoformat(),
                "security_report": security_report
            }
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Rapor parse hatası")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rapor detay hatası: {str(e)}")

@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: int, db: Session = Depends(get_db)):
    """Raporu JSON olarak indir"""
    try:
        file = db.query(LogFile).filter(LogFile.id == report_id).first()
        if not file or not file.security_report_json:
            raise HTTPException(status_code=404, detail="Rapor bulunamadı")
        
        from fastapi.responses import Response
        
        return Response(
            content=file.security_report_json,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=security_report_{report_id}.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rapor indirme hatası: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 