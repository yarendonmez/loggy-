#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def migrate_database():
    """Database'e yeni security_report_json alanını ekle"""
    db_path = "data/loggy.db"
    
    if not os.path.exists(db_path):
        print("❌ Database dosyası bulunamadı")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Yeni alanı ekle
        print("🔄 Database migration başlıyor...")
        
        try:
            cursor.execute("ALTER TABLE log_files ADD COLUMN security_report_json TEXT")
            conn.commit()
            print("✅ security_report_json alanı eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️  security_report_json alanı zaten mevcut")
            else:
                print(f"❌ Migration hatası: {e}")
                return
        
        # Tabloyu kontrol et
        cursor.execute("PRAGMA table_info(log_files)")
        columns = cursor.fetchall()
        
        print("\n📋 log_files tablosu alanları:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Database migration tamamlandı!")
        
    except Exception as e:
        print(f"❌ Migration hatası: {e}")

if __name__ == "__main__":
    migrate_database()
