#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from backend.app.ml_model import LLMLogAnomalyDetector
import json

def test_security_report():
    # Güvenlik raporu testini yap
    detector = LLMLogAnomalyDetector()
    print('🔍 Güvenlik Raporu Test Ediliyor...')

    # Log dosyasını oku
    with open('data/large_test_1000.log', 'r', encoding='utf-8') as f:
        log_lines = [line.strip() for line in f.readlines() if line.strip()]

    print(f'📝 Test log satırları: {len(log_lines)}')
    print('🔄 Analiz ve rapor oluşturma başlıyor...')

    # Analiz yap
    result = detector.predict(log_lines)

    if result['status'] == 'success':
        print('✅ Analiz ve rapor başarılı!')
        print(f'📊 Toplam satır: {result["total_lines"]}')
        print(f'⚠️  Anomali sayısı: {result["anomaly_count"]}')
        print(f'🚨 Kritik sayısı: {result["critical_count"]}')
        print(f'📈 Anomali oranı: {result["anomaly_rate"]:.2%}')
        
        # Güvenlik raporunu kontrol et
        if 'security_report' in result:
            report = result['security_report']
            print('\n🛡️  GÜVENLİK RAPORU:')
            print(f'🎯 Risk Skoru: {report["summary"]["risk_score"]}/100')
            print(f'⚠️  Risk Seviyesi: {report["summary"]["risk_level"]}')
            print(f'🔍 Potansiyel Saldırı: {len(report["potential_attacks"])} adet')
            
            # Saldırı türlerini göster
            if report["potential_attacks"]:
                print('\n🚨 TESPİT EDİLEN SALDIRILAR:')
                for attack in report["potential_attacks"]:
                    print(f'- {attack["attack_type"]} ({attack["severity"]})')
                    print(f'  {attack["description"]}')
                    print(f'  Öneri: {attack["recommendation"]}\n')
            
            # Kategorileri göster
            print('📊 ANOMALI KATEGORİLERİ:')
            for category, count in report["attack_categories"].items():
                print(f'- {category.replace("_", " ").title()}: {count} adet')
            
            # İlk 5 öneriyi göster
            print('\n💡 GÜVENLİK ÖNERİLERİ:')
            for i, rec in enumerate(report["recommendations"][:5], 1):
                print(f'{i}. {rec}')
                
            print('\n📋 ANALİZ METODOLOJİSİ:')
            print(f'🤖 AI Modeli: {report["analysis_methodology"]["ai_model"]}')
            print('🔍 Tespit Kriterleri:')
            for criteria in report["analysis_methodology"]["analysis_criteria"][:3]:
                print(f'  - {criteria}')
        else:
            print('❌ Güvenlik raporu oluşturulamadı')
    else:
        print(f'❌ Analiz hatası: {result["message"]}')

if __name__ == "__main__":
    test_security_report()
