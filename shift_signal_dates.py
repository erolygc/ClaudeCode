"""
Sinyal Tarihlerini Kaydır - Test amaçlı backtest için
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import pandas as pd
from datetime import timedelta

def main():
    print("="*80)
    print("⏰ SİNYAL TARİHLERİNİ KAYDIRMA - TEST AMAÇLI")
    print("="*80)

    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()

    # Mevcut durumu göster
    signals_count = pd.read_sql_query("""
        SELECT COUNT(*) as count FROM signals WHERE signal IN ('BUY', 'SELL')
    """, conn).iloc[0]['count']

    print(f"\n📊 Toplam BUY/SELL Sinyal: {signals_count}")

    # En son sinyal tarihi
    latest_signal = pd.read_sql_query("""
        SELECT MAX(created_at) as latest FROM signals
    """, conn).iloc[0]['latest']

    print(f"📅 En son sinyal: {latest_signal}")

    # 7 gün geriye kaydır
    days_to_shift = 7

    print(f"\n⏪ Tüm sinyalleri {days_to_shift} gün geriye kaydırıyorum...")

    # SQL ile tarihleri güncelle
    cursor.execute(f"""
        UPDATE signals
        SET created_at = datetime(created_at, '-{days_to_shift} days')
    """)

    conn.commit()

    # Yeni durumu göster
    new_latest = pd.read_sql_query("""
        SELECT MAX(created_at) as latest FROM signals
    """, conn).iloc[0]['latest']

    print(f"✅ Güncelleme tamamlandı!")
    print(f"📅 Yeni en son sinyal: {new_latest}")

    # Test edilebilir sinyal sayısı
    testable = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM signals s
        WHERE s.signal IN ('BUY', 'SELL')
        AND EXISTS (
            SELECT 1 FROM ohlcv_data o
            WHERE o.ticker = s.ticker
            AND o.timeframe = s.timeframe
            AND o.date > s.created_at
            LIMIT 1
        )
    """, conn).iloc[0]['count']

    print(f"\n🎯 Test edilebilir sinyal: {testable}")

    if testable > 100:
        print(f"\n✅ Harika! Şimdi backtest çalıştırabilirsiniz:")
        print(f"   python backtest_optimized.py")
    else:
        print(f"\n⚠️  Hala yeterli test edilebilir sinyal yok.")
        print(f"   Belki daha fazla gün geriye kaydırmak gerekebilir.")

    conn.close()

if __name__ == "__main__":
    main()
