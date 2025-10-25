"""
Sinyal Debug - Neden sinyaller atlanıyor?
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import pandas as pd

def main():
    print("="*80)
    print("🔍 SİNYAL DEBUG ANALİZİ")
    print("="*80)

    db = DatabaseManager()
    conn = db.get_connection()

    # İlk 20 BUY/SELL sinyalini al
    signals_df = pd.read_sql_query("""
        SELECT ticker, timeframe, signal, score, created_at
        FROM signals
        WHERE signal IN ('BUY', 'SELL')
        ORDER BY created_at DESC
        LIMIT 20
    """, conn)

    print(f"\n📊 İlk 20 BUY/SELL Sinyal:")
    print(signals_df.to_string())

    # Her sinyal için veri var mı kontrol et
    print("\n\n🔍 Her sinyal için veri kontrolü:")
    print("-" * 80)

    for idx, row in signals_df.iterrows():
        ticker = row['ticker']
        timeframe = row['timeframe']
        signal_date = row['created_at']

        # Bu ticker-timeframe için veri var mı?
        ohlcv_count = pd.read_sql_query(f"""
            SELECT COUNT(*) as count
            FROM ohlcv_data
            WHERE ticker = '{ticker}' AND timeframe = '{timeframe}'
        """, conn).iloc[0]['count']

        # Sinyal tarihinden sonra veri var mı?
        future_count = pd.read_sql_query(f"""
            SELECT COUNT(*) as count
            FROM ohlcv_data
            WHERE ticker = '{ticker}'
            AND timeframe = '{timeframe}'
            AND date > '{signal_date}'
        """, conn).iloc[0]['count']

        status = "✅" if future_count >= 20 else "❌"
        print(f"{status} {ticker:12} {timeframe:4} - Toplam: {ohlcv_count:4} bar, Sinyal sonrası: {future_count:3} bar")

    conn.close()

if __name__ == "__main__":
    main()
