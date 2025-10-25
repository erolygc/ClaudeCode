"""
Hızlı Backtest Testi - İlk 10 sinyali test eder
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import pandas as pd

def main():
    print("="*80)
    print("🧪 HIZLI BACKTEST TESTİ - İlk 10 Sinyal")
    print("="*80)

    db = DatabaseManager()
    conn = db.get_connection()

    # İlk 10 sinyali al (HOLD hariç)
    signals_df = pd.read_sql_query("""
        SELECT ticker, timeframe, signal, score, created_at
        FROM signals
        WHERE signal != 'HOLD'
        ORDER BY created_at DESC
        LIMIT 10
    """, conn)

    print(f"\n📊 {len(signals_df)} sinyal bulundu:")
    print(signals_df[['ticker', 'timeframe', 'signal', 'score']].to_string())

    # Database istatistikleri
    ohlcv_count = pd.read_sql_query("SELECT COUNT(*) as count FROM ohlcv_data", conn).iloc[0]['count']
    signals_count = pd.read_sql_query("SELECT COUNT(*) as count FROM signals", conn).iloc[0]['count']

    print(f"\n📈 Database İstatistikleri:")
    print(f"   OHLCV Bars: {ohlcv_count:,}")
    print(f"   Toplam Sinyal: {signals_count}")

    conn.close()
    print("\n✅ Test tamamlandı!")

if __name__ == "__main__":
    main()
