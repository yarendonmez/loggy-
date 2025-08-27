#!/bin/bash

echo "🚀 Akıllı Log Asistanı Başlatılıyor..."

# Ollama kontrolü
echo "🔍 Ollama durumu kontrol ediliyor..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama kurulu değil!"
    echo "📥 Kurulum için: https://ollama.ai/download"
    exit 1
fi

# Ollama servis kontrolü
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "🔄 Ollama servisi başlatılıyor..."
    ollama serve &
    sleep 5
fi

# Model kontrolü
echo "🤖 Llama 3.2 modeli kontrol ediliyor..."
if ! ollama list | grep -q "llama3.2"; then
    echo "📥 Llama 3.2 modeli indiriliyor..."
    ollama pull llama3.2
fi

# Backend başlat
echo "🔧 Backend başlatılıyor..."
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 &
BACKEND_PID=$!

# Frontend başlat
echo "🎨 Frontend başlatılıyor..."
cd ../frontend
npm install
npm start &
FRONTEND_PID=$!

echo "✅ Sistem başarıyla başlatıldı!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Dokümantasyonu: http://localhost:8000/docs"

# Cleanup function
cleanup() {
    echo "🛑 Sistem kapatılıyor..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
