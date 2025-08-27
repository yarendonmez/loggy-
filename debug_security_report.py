#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.app.ml_model import LLMLogAnomalyDetector
import json
import traceback

def debug_security_report():
    """Güvenlik raporu debug işlemi"""
    try:
        detector = LLMLogAnomalyDetector()
        print('🔍 Debug: Güvenlik Raporu Test...')

        # Küçük test verisi
        test_logs = [
            "2024-01-15 10:30:45 INFO User login successful - user_id: 123",
            "2024-01-15 10:31:02 ERROR Database connection failed - timeout after 30s",
            "2024-01-15 10:31:15 WARNING High memory usage detected - 95% utilized",
            "2024-01-15 10:31:30 CRITICAL System failure - emergency shutdown initiated",
            "2024-01-15 10:32:00 INFO System restart completed successfully"
        ]

        print(f'📝 Test log satırları: {len(test_logs)}')
        
        # Analiz yap
        result = detector.predict(test_logs)
        
        print(f'✅ Predict sonucu: {result["status"]}')
        print(f'📊 Keys: {list(result.keys())}')
        
        # Security report var mı kontrol et
        if "security_report" in result:
            print('✅ Security report mevcut!')
            report = result["security_report"]
            print(f'📋 Report keys: {list(report.keys())}')
            print(f'🎯 Risk Score: {report.get("summary", {}).get("risk_score", "N/A")}')
            
            # JSON serialize test
            try:
                json_str = json.dumps(report, ensure_ascii=False, indent=2)
                print('✅ JSON serialization başarılı')
                print(f'📄 JSON boyutu: {len(json_str)} karakter')
            except Exception as e:
                print(f'❌ JSON serialization hatası: {e}')
                
        else:
            print('❌ Security report yok!')
            print('🔍 Available keys:', list(result.keys()))
            
            # Manuel rapor oluşturmayı test et
            print('\n🛠️  Manuel rapor oluşturma testi...')
            if "results" in result:
                try:
                    manual_report = detector.generate_security_report(result["results"], test_logs)
                    print('✅ Manuel rapor oluşturma başarılı!')
                    print(f'📋 Manuel report keys: {list(manual_report.keys())}')
                except Exception as e:
                    print(f'❌ Manuel rapor hatası: {e}')
                    traceback.print_exc()
            
    except Exception as e:
        print(f'❌ Debug hatası: {e}')
        traceback.print_exc()

if __name__ == "__main__":
    debug_security_report()
