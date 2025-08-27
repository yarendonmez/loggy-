#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from backend.app.database import engine, Base

def recreate_database():
    """Database'i tamamen yeniden oluştur"""
    db_path = "data/loggy.db"
    
    # Eski database'i sil
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Eski database silindi")
        except Exception as e:
            print(f"⚠️  Database silinemedi: {e}")
    
    # Yeni database oluştur
    try:
        print("🔄 Yeni database oluşturuluyor...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database başarıyla oluşturuldu!")
        
        # Tabloları listele
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Oluşturulan tablolar ({len(tables)} adet):")
        for table in tables:
            print(f"  - {table}")
            columns = inspector.get_columns(table)
            for col in columns:
                print(f"    • {col['name']} ({col['type']})")
        
    except Exception as e:
        print(f"❌ Database oluşturma hatası: {e}")

if __name__ == "__main__":
    recreate_database()
