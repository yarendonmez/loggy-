# 🚀 Hızlı Başlangıç Rehberi

## 📋 Gereksinimler

- Windows 10/11 (macOS/Linux da desteklenir)
- Python 3.11+ 
- Node.js 16+
- En az 4GB RAM
- İnternet bağlantısı (model indirme için)

## ⚡ 3 Dakikada Çalıştırın

### 1️⃣ Ollama Kurulumu (2 dakika)

```powershell
# PowerShell'i yönetici olarak açın
winget install ollama

# Model indirin
ollama pull llama3.2

# Servisi başlatın
ollama serve
```

### 2️⃣ Projeyi Başlatın (1 dakika)

```bash
# Proje dizinine gidin
cd C:\path\to\Loggy

# Tek komutla başlatın
start.bat
```

### 3️⃣ Test Edin

```bash
# Backend test
curl http://localhost:8000/health

# LLM test
python test_llm.py

# Web arayüzü
# http://localhost:3000
```

## 🔧 Sorun mu Yaşıyorsunuz?

### Ollama Bulunamıyor
```powershell
$env:PATH += ";C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama"
```

### Port 8000 Kullanımda
```powershell
tasklist | findstr python
taskkill /PID [PID] /F
```

### Model İndirilemiyor
```bash
# VPN kullanın veya farklı ağ deneyin
ollama pull llama3.2
```

### Frontend Hatası
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

## 🎯 İlk Log Analizinizi Yapın

1. **http://localhost:3000** adresini açın
2. `data/sample_logs.csv` dosyasını yükleyin
3. "Analiz Et" butonuna tıklayın
4. Sonuçları inceleyin!

## 📞 Destek

- **Dokümantasyon:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health  
- **Test Script:** `python test_llm.py`

---

**🎉 Başarılar! Artık AI destekli log analiziniz hazır!**
