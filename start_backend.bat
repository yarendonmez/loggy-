@echo off
echo Backend sunucu baslatiliyor...
echo.

REM Conda environment aktifleştir (doğru environment)
call conda activate loggy-py311

REM Backend dizinine git
cd backend

REM Python versiyonunu göster
echo Python versiyonu kontrol ediliyor...
python --version
echo.

REM Sunucuyu başlat
echo Backend sunucu http://localhost:8000 adresinde baslatiliyor...
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
