#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.app.ml_model import LLMLogAnomalyDetector

def test_large_file():
    # Büyük dosyayı test et
    detector = LLMLogAnomalyDetector()
    print('🔍 Büyük Dosya Test Ediliyor...')
    print(f'📡 Ollama URL: {detector.ollama_url}')
    print(f'🤖 Model: {detector.model_name}')
    print(f'✅ Hazır mı: {detector.is_ready}')

    # Log dosyasını oku
    with open('data/large_test_1000.log', 'r', encoding='utf-8') as f:
        log_lines = [line.strip() for line in f.readlines() if line.strip()]

    print(f'📝 Test log satırları: {len(log_lines)}')
    print('🔄 Analiz başlıyor...')

    # Analiz yap
    result = detector.predict(log_lines)

    if result['status'] == 'success':
        print('✅ Analiz başarılı!')
        print(f'📊 Toplam satır: {result["total_lines"]}')
        print(f'⚠️  Anomali sayısı: {result["anomaly_count"]}')
        print(f'🚨 Kritik sayısı: {result["critical_count"]}')
        print(f'📈 Anomali oranı: {result["anomaly_rate"]:.2%}')
        
        # İlk 5 anomaliyi göster
        if result.get("results"):
            print('\n📋 İlk 5 Anomali:')
            for i, res in enumerate(result["results"][:5]):
                if res.get("is_anomaly"):
                    print(f'{i+1}. Satır {res.get("line_number", "?")}: {res.get("severity", "unknown")} - {res.get("explanation", "No explanation")}')
    else:
        print(f'❌ Analiz hatası: {result["message"]}')

if __name__ == "__main__":
    test_large_file()
