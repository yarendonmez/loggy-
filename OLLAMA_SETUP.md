# 🚀 Ollama Kurulum Rehberi

## 1. Ollama'yı İndirin ve Kurun

### Windows:
```bash
# PowerShell'de çalıştırın
curl.exe -fsSL https://ollama.ai/install.ps1 | powershell
```

### MacOS:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## 2. Llama 3.2 Modelini İndirin

Ollama kurulduktan sonra terminal/PowerShell'de:

```bash
ollama pull llama3.2
```

Bu işlem 2-3 dakika sürebilir (model boyutu ~2GB).

## 3. Ollama Servisini Başlatın

```bash
ollama serve
```

Bu komut Ollama'yı `http://localhost:11434` adresinde başlatır.

## 4. Test Edin

Yeni bir terminal/PowerShell penceresi açın:

```bash
ollama run llama3.2
```

Çalışıyorsa ">>> " promptu görmelisiniz. `/bye` yazarak çıkabilirsiniz.

## 5. Projeyi Başlatın

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## ⚡ Hızlı Test

Backend çalıştıktan sonra:
- http://localhost:8000/health - API durumunu kontrol edin
- http://localhost:8000/api/upload - Log dosyası yükleyin
- Analiz sonuçları otomatik olarak LLM ile gelecek

## 🔧 Sorun Giderme

**Ollama bağlanamıyorsa:**
1. `ollama serve` komutunu çalıştırdığınızdan emin olun
2. Firewall'ın port 11434'ü engellemediğini kontrol edin
3. Model indirildi mi: `ollama list`

**Model yavaşsa:**
- GPU kullanımı için NVIDIA kartınız varsa otomatik algılar
- CPU'da da çalışır ama biraz yavaş olabilir

## 📊 Performans

- **İlk çalıştırma:** 10-15 saniye (model yüklenir)
- **Sonraki analizler:** 2-5 saniye
- **Dosya boyutu:** 50MB'a kadar desteklenir
