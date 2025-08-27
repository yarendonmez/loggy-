#!/usr/bin/env python3
"""
LLM entegrasyonunu test etmek için hızlı script
"""

import sys
import os
sys.path.append('backend')

from backend.app.ml_model import LLMLogAnomalyDetector

def test_llm():
    print("🔍 LLM Anomali Tespit Sistemi Test Ediliyor...")
    
    # Detector'ı başlat
    detector = LLMLogAnomalyDetector()
    
    print(f"📡 Ollama URL: {detector.ollama_url}")
    print(f"🤖 Model: {detector.model_name}")
    print(f"✅ Hazır mı: {detector.is_ready}")
    
    if not detector.is_ready:
        print("❌ Ollama hazır değil! Lütfen şu adımları takip edin:")
        print("1. Ollama'yı kurun: https://ollama.ai/download")
        print("2. Modeli indirin: ollama pull llama3.2")
        print("3. Servisi başlatın: ollama serve")
        return
    
    # Test log satırları
    test_logs = [
        "2024-01-15 10:30:45 INFO User login successful - user_id: 123",
        "2024-01-15 10:31:02 ERROR Database connection failed - timeout after 30s",
        "2024-01-15 10:31:15 WARNING High memory usage detected - 95% utilized",
        "2024-01-15 10:31:30 CRITICAL System failure - emergency shutdown initiated",
        "2024-01-15 10:32:00 INFO System restart completed successfully"
    ]
    
    print("\n📝 Test log satırları:")
    for i, log in enumerate(test_logs, 1):
        print(f"{i}: {log}")
    
    print("\n🔄 Analiz başlıyor...")
    
    # Analiz yap
    result = detector.predict(test_logs)
    
    if result["status"] == "success":
        print(f"\n✅ Analiz başarılı!")
        print(f"📊 Toplam satır: {result['total_lines']}")
        print(f"⚠️  Anomali sayısı: {result['anomaly_count']}")
        print(f"🚨 Kritik sayısı: {result['critical_count']}")
        print(f"📈 Anomali oranı: {result['anomaly_rate']:.2%}")
        
        print("\n📋 Detaylar:")
        for res in result['results'][:5]:  # İlk 5 sonuç
            emoji = "🚨" if res['severity'] == 'critical' else "⚠️" if res['is_anomaly'] else "✅"
            print(f"{emoji} Satır {res['line_number']}: {res['severity']} - {res.get('explanation', 'N/A')}")
    
    else:
        print(f"❌ Analiz hatası: {result['message']}")

if __name__ == "__main__":
    test_llm()
