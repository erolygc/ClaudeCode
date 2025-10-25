"""
Eski Sinyalleri Kontrol Et
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import pandas as pd

def main():
    print("="*80)
    print("📅 ESKİ SİNYAL KONTROLÜ")
    print("="*80)

    db = DatabaseManager()
    conn = db.get_connection()

    # Tüm sinyallerin tarih dağılımı
    date_dist = pd.read_sql_query("""
        SELECT
            DATE(created_at) as signal_date,
            COUNT(*) as count,
            MIN(created_at) as first_signal,
            MAX(created_at) as last_signal
        FROM signals
        WHERE signal IN ('BUY', 'SELL')
        GROUP BY DATE(created_at)
        ORDER BY signal_date DESC
    """, conn)

    print("\n📊 Sinyal Tarih Dağılımı:")
    print(date_dist.to_string())

    # En son OHLCV verisi ne zaman?
    latest_ohlcv = pd.read_sql_query("""
        SELECT timeframe, MAX(date) as latest_date
        FROM ohlcv_data
        GROUP BY timeframe
        ORDER BY timeframe
    """, conn)

    print("\n\n📈 En Son OHLCV Verisi:")
    print(latest_ohlcv.to_string())

    # Backtest yapılabilecek eski sinyaller var mı?
    # (Sinyal tarihi < en eski OHLCV tarihinden önce)
    testable = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM signals
        WHERE signal IN ('BUY', 'SELL')
        AND created_at < '2025-10-24'
    """, conn).iloc[0]['count']

    print(f"\n\n🎯 Test Edilebilir Eski Sinyal: {testable}")

    if testable == 0:
        print("\n⚠️  ÖNEMLİ NOT:")
        print("   Tüm sinyaller bugün üretildi, henüz gelecek verileri yok.")
        print("   Backtest yapabilmek için:")
        print("   1. Yarın yeni veri geldikten sonra test yapın")
        print("   2. VEYA test için sinyalleri geçmiş tarihe kaydedin")
        print("   3. VEYA forward-test (gelecek tahminleri) yapın")

    conn.close()

if __name__ == "__main__":
    main()
