"""
Database Query Helper - Kolay veri sorguları için yardımcı araç

Kullanım:
  python tools/query_db.py --ticker GARAN.IS --timeframe 1d --last 10
  python tools/query_db.py --indicators GARAN.IS --timeframe 1d --last 5
  python tools/query_db.py --signals --last 10
  python tools/query_db.py --stats
"""
import os
import sys
import argparse
from datetime import datetime

# Proje kök dizinini Python path'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.db_manager import DatabaseManager
import pandas as pd


class DatabaseQueryHelper:
    """Database sorguları için yardımcı sınıf"""

    def __init__(self):
        self.db = DatabaseManager()

    def show_ohlcv_data(self, ticker, timeframe, limit=10):
        """OHLCV verisini göster"""
        print(f"\n📊 {ticker} ({timeframe}) - Son {limit} Bar")
        print("=" * 100)

        conn = self.db.get_connection()

        df = pd.read_sql_query(f"""
            SELECT date, open, high, low, close, volume
            FROM ohlcv_data
            WHERE ticker = ? AND timeframe = ?
            ORDER BY date DESC
            LIMIT {limit}
        """, conn, params=(ticker, timeframe))

        conn.close()

        if df.empty:
            print("❌ Veri bulunamadı!")
            return

        # Ters çevir (en eski en üstte)
        df = df.iloc[::-1]

        # Formatla
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M')

        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].apply(lambda x: f"{x:.2f}")

        df['volume'] = df['volume'].apply(lambda x: f"{x:,}")

        print(df.to_string(index=False))
        print()

    def show_indicators(self, ticker, timeframe, limit=5, indicator_names=None):
        """İndikatör değerlerini göster"""
        print(f"\n📐 {ticker} ({timeframe}) - Son {limit} İndikatör Değeri")
        print("=" * 120)

        conn = self.db.get_connection()

        # Tüm indikatörleri al
        query = """
            SELECT date, indicator_name, value
            FROM indicators
            WHERE ticker = ? AND timeframe = ?
        """

        if indicator_names:
            placeholders = ','.join(['?' for _ in indicator_names])
            query += f" AND indicator_name IN ({placeholders})"
            params = (ticker, timeframe) + tuple(indicator_names)
        else:
            params = (ticker, timeframe)

        query += " ORDER BY date DESC"

        df = pd.read_sql_query(query, conn, params=params)

        conn.close()

        if df.empty:
            print("❌ İndikatör verisi bulunamadı!")
            return

        # Pivot table oluştur (tarih x indikatör)
        pivot = df.pivot_table(index='date', columns='indicator_name', values='value')

        # Son N satırı al ve ters çevir
        pivot = pivot.tail(limit).iloc[::-1]

        # Formatla
        pivot.index = pd.to_datetime(pivot.index)
        pivot.index = pivot.index.strftime('%Y-%m-%d %H:%M')

        # Değerleri formatla (2 ondalık)
        pivot = pivot.map(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

        print(pivot.to_string())
        print()

    def show_signals(self, limit=10, ticker=None):
        """Sinyalleri göster"""
        print(f"\n🎯 Sinyaller - Son {limit}")
        print("=" * 100)

        conn = self.db.get_connection()

        query = """
            SELECT ticker, timeframe, signal, score, created_at, details
            FROM signals
        """

        if ticker:
            query += " WHERE ticker = ?"
            params = (ticker,)
        else:
            params = ()

        query += f" ORDER BY created_at DESC LIMIT {limit}"

        df = pd.read_sql_query(query, conn, params=params)

        conn.close()

        if df.empty:
            print("❌ Sinyal bulunamadı!")
            return

        # Formatla
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        df['score'] = df['score'].apply(lambda x: f"{x:.1f}")

        # Emoji ekle
        signal_emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}
        df['signal'] = df.apply(lambda row: f"{signal_emoji.get(row['signal'], '')} {row['signal']}", axis=1)

        print(df.to_string(index=False))
        print()

    def show_statistics(self):
        """Genel istatistikler"""
        print("\n📊 GENEL İSTATİSTİKLER")
        print("=" * 80)

        conn = self.db.get_connection()

        # Hisse sayısı
        stocks = pd.read_sql_query("SELECT COUNT(DISTINCT ticker) as count FROM ohlcv_data", conn)
        print(f"📈 Toplam hisse: {stocks['count'].iloc[0]}")

        # Bar sayısı
        bars = pd.read_sql_query("SELECT COUNT(*) as count FROM ohlcv_data", conn)
        print(f"📊 Toplam bar: {bars['count'].iloc[0]:,}")

        # İndikatör sayısı
        indicators = pd.read_sql_query("SELECT COUNT(*) as count FROM indicators", conn)
        print(f"📐 Toplam indikatör: {indicators['count'].iloc[0]:,}")

        # Sinyal sayısı
        signals = pd.read_sql_query("SELECT COUNT(*) as count FROM signals", conn)
        print(f"🎯 Toplam sinyal: {signals['count'].iloc[0]}")

        print("\n📋 Hisse Detayları:")
        stock_details = pd.read_sql_query("""
            SELECT ticker, timeframe, COUNT(*) as bars,
                   MIN(date) as first_date, MAX(date) as last_date
            FROM ohlcv_data
            GROUP BY ticker, timeframe
            ORDER BY ticker, timeframe
        """, conn)

        for _, row in stock_details.iterrows():
            first = row['first_date'][:10] if row['first_date'] else 'N/A'
            last = row['last_date'][:10] if row['last_date'] else 'N/A'
            print(f"  {row['ticker']} ({row['timeframe']}): {row['bars']:,} bar ({first} → {last})")

        print("\n🎯 Sinyal Dağılımı:")
        signal_dist = pd.read_sql_query("""
            SELECT signal, COUNT(*) as count
            FROM signals
            GROUP BY signal
        """, conn)

        total_signals = signal_dist['count'].sum()
        for _, row in signal_dist.iterrows():
            emoji = '🟢' if row['signal'] == 'BUY' else ('🔴' if row['signal'] == 'SELL' else '🟡')
            pct = (row['count'] / total_signals * 100) if total_signals > 0 else 0
            print(f"  {emoji} {row['signal']}: {row['count']} ({pct:.1f}%)")

        conn.close()
        print()

    def list_tickers(self):
        """Tüm hisseleri listele"""
        print("\n📋 Sistemdeki Hisseler")
        print("=" * 80)

        tickers = self.db.get_all_tickers()

        for ticker in tickers:
            timeframes = self.db.get_all_timeframes_for_ticker(ticker)
            print(f"  {ticker}: {', '.join(timeframes)}")

        print()


def main():
    parser = argparse.ArgumentParser(description='Database Query Helper')

    parser.add_argument('--ticker', type=str, help='Hisse kodu (örn: GARAN.IS)')
    parser.add_argument('--timeframe', type=str, help='Zaman dilimi (örn: 1d, 1h)')
    parser.add_argument('--last', type=int, default=10, help='Gösterilecek kayıt sayısı (varsayılan: 10)')
    parser.add_argument('--indicators', action='store_true', help='İndikatörleri göster')
    parser.add_argument('--signals', action='store_true', help='Sinyalleri göster')
    parser.add_argument('--stats', action='store_true', help='Genel istatistikler')
    parser.add_argument('--list', action='store_true', help='Tüm hisseleri listele')
    parser.add_argument('--indicator-names', nargs='+', help='Gösterilecek indikatör isimleri (örn: RSI_14 SMA_20)')

    args = parser.parse_args()

    helper = DatabaseQueryHelper()

    # Hangi komut verilmiş?
    if args.stats:
        helper.show_statistics()
    elif args.list:
        helper.list_tickers()
    elif args.signals:
        helper.show_signals(limit=args.last, ticker=args.ticker)
    elif args.indicators:
        if not args.ticker or not args.timeframe:
            print("❌ İndikatörler için --ticker ve --timeframe gerekli!")
            print("Örnek: python tools/query_db.py --indicators --ticker GARAN.IS --timeframe 1d")
            return
        helper.show_indicators(args.ticker, args.timeframe, limit=args.last,
                             indicator_names=args.indicator_names)
    elif args.ticker and args.timeframe:
        # OHLCV verisi göster
        helper.show_ohlcv_data(args.ticker, args.timeframe, limit=args.last)
    else:
        # Hiçbir parametre verilmemişse istatistikleri göster
        helper.show_statistics()


if __name__ == "__main__":
    main()
