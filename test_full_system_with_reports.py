#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_full_system():
    """Tam sistem testi - dosya yükle, analiz et, rapor kontrol et"""
    base_url = "http://localhost:8000"
    
    print('🔍 TAM SİSTEM TESTİ - RAPOR SİSTEMİ')
    print('=' * 50)
    
    try:
        # 1. Health Check
        print('1. 🏥 Health Check...')
        response = requests.get(f'{base_url}/health')
        if response.status_code == 200:
            print('✅ Backend sağlıklı')
        else:
            print('❌ Backend sağlıksız')
            return
        
        # 2. Dosya yükle
        print('\n2. 📤 Dosya yükleme...')
        with open('data/large_test_1000.log', 'rb') as f:
            files = {'file': ('test_1000.log', f, 'text/plain')}
            response = requests.post(f'{base_url}/api/upload', files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            file_id = upload_result['file_id']
            print(f'✅ Dosya yüklendi - ID: {file_id}')
        else:
            print(f'❌ Dosya yükleme hatası: {response.text}')
            return
        
        # 3. Analiz başlat
        print('\n3. 🔄 Analiz başlatılıyor...')
        response = requests.post(f'{base_url}/api/analyze/{file_id}')
        
        if response.status_code == 200:
            analysis_result = response.json()
            print('✅ Analiz başlatıldı')
            
            # Analiz tamamlanmasını bekle
            print('⏳ Analiz tamamlanması bekleniyor...')
            time.sleep(2)  # Analiz için bekle
            
        else:
            print(f'❌ Analiz hatası: {response.text}')
            return
        
        # 4. Analiz sonuçlarını kontrol et
        print('\n4. 📊 Analiz sonuçları kontrol ediliyor...')
        max_attempts = 30  # 30 saniye bekle
        for attempt in range(max_attempts):
            response = requests.get(f'{base_url}/api/analysis/{file_id}/results')
            if response.status_code == 200:
                results = response.json()
                print('✅ Analiz tamamlandı!')
                print(f'📈 Anomali sayısı: {results.get("anomaly_count", "N/A")}')
                print(f'🚨 Kritik sayısı: {results.get("critical_count", "N/A")}')
                break
            elif response.status_code == 404:
                print(f'⏳ Analiz devam ediyor... ({attempt + 1}/{max_attempts})')
                time.sleep(2)
            else:
                print(f'❌ Analiz sonuç hatası: {response.text}')
                return
        else:
            print('⏰ Analiz zaman aşımı')
            return
        
        # 5. Raporları listele
        print('\n5. 📋 Raporlar listeleniyor...')
        response = requests.get(f'{base_url}/api/reports')
        
        if response.status_code == 200:
            reports_data = response.json()
            reports = reports_data.get('reports', [])
            print(f'✅ {len(reports)} rapor bulundu')
            
            if reports:
                latest_report = reports[0]  # En yeni rapor
                print(f'📄 Son rapor: {latest_report["filename"]}')
                
                # Güvenlik raporunu kontrol et
                if 'security_report' in latest_report:
                    security_report = latest_report['security_report']
                    summary = security_report['summary']
                    
                    print('\n🛡️  GÜVENLİK RAPORU ÖZETİ:')
                    print(f'🎯 Risk Skoru: {summary["risk_score"]}/100')
                    print(f'⚠️  Risk Seviyesi: {summary["risk_level"]}')
                    print(f'📊 Toplam Anomali: {summary["total_anomalies"]}')
                    print(f'🚨 Potansiyel Saldırı: {len(security_report["potential_attacks"])} adet')
                    
                    # Saldırı türlerini göster
                    if security_report["potential_attacks"]:
                        print('\n🚨 TESPİT EDİLEN SALDIRILAR:')
                        for attack in security_report["potential_attacks"][:3]:  # İlk 3
                            print(f'- {attack["attack_type"]} ({attack["severity"]})')
                    
                    # Önerileri göster
                    print('\n💡 GÜVENLİK ÖNERİLERİ:')
                    for i, rec in enumerate(security_report["recommendations"][:3], 1):
                        print(f'{i}. {rec}')
                    
                    print('\n✅ RAPOR SİSTEMİ TAM ÇALIŞIYOR!')
                else:
                    print('❌ Güvenlik raporu bulunamadı')
            else:
                print('📭 Henüz rapor yok')
        else:
            print(f'❌ Rapor listeleme hatası: {response.text}')
        
        print('\n🎉 TAM SİSTEM TESTİ TAMAMLANDI!')
        print('Frontend: http://localhost:3000')
        print('Backend: http://localhost:8000')
        print('Raporlar: http://localhost:3000/reports')
        
    except Exception as e:
        print(f'❌ Test hatası: {e}')

if __name__ == "__main__":
    test_full_system()
