ele@echo off
echo.
echo ========================================
echo 🚀 Akıllı Log Asistanı Başlatılıyor...
echo ========================================
echo.

REM Ollama kontrolü
echo 🔍 1/4 - Ollama durumu kontrol ediliyor...
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Ollama kurulu değil!
    echo.
    echo 📥 Kurulum için şu komutu çalıştırın:
    echo    winget install ollama
    echo.
    echo 📖 Veya https://ollama.ai/download adresinden indirin
    pause
    exit /b 1
)

REM Ollama servis kontrolü
curl -s http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 🔄 Ollama servisi başlatılıyor...
    start /B ollama serve
    timeout /t 5 >nul
)

REM Model kontrolü
echo 🤖 2/4 - Llama 3.2 modeli kontrol ediliyor...
ollama list | findstr "llama3.2" >nul
if %ERRORLEVEL% neq 0 (
    echo 📥 Llama 3.2 modeli indiriliyor (2-3 dakika sürebilir)...
    ollama pull llama3.2
    if %ERRORLEVEL% neq 0 (
        echo ❌ Model indirilemedi! İnternet bağlantınızı kontrol edin.
        pause
        exit /b 1
    )
)

REM Backend başlat
echo 🔧 3/4 - Backend başlatılıyor...
cd backend
echo    📦 Python paketleri kuruluyor...
pip install -r requirements.txt >nul 2>nul
echo    🚀 Backend servisi başlatılıyor...
start /B python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM Frontend başlat
echo 🎨 4/4 - Frontend başlatılıyor...
cd ..\frontend
echo    📦 Node.js paketleri kuruluyor...
npm install --legacy-peer-deps >nul 2>nul
echo    🚀 Frontend servisi başlatılıyor...
start /B npm start

echo.
echo ========================================
echo ✅ SİSTEM BAŞARIYLA BAŞLATILDI!
echo ========================================
echo.
echo 🌐 Frontend:          http://localhost:3000
echo 🔧 Backend API:       http://localhost:8000
echo 📚 API Dokümantasyonu: http://localhost:8000/docs
echo 🩺 Health Check:      http://localhost:8000/health
echo.
echo 📋 Test için: python test_llm.py
echo.
echo ⚠️  Kapatmak için bu pencereyi kapatın veya Ctrl+C basın
echo.
pause
