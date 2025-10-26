"""
Live Trading Monitor - Sistem durumunu izle
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from database.db_manager import DatabaseManager


class LiveTradingMonitor:
    """Canlı trading sisteminin durumunu izler"""

    def __init__(self):
        self.db = DatabaseManager()

    def get_recent_signals(self, hours: int = 24, min_score: float = 60) -> pd.DataFrame:
        """Son X saatteki sinyalleri getir"""
        conn = self.db.get_connection()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

        df = pd.read_sql_query("""
            SELECT
                ticker,
                timeframe,
                signal,
                score,
                created_at
            FROM signals
            WHERE created_at >= ?
              AND score >= ?
            ORDER BY created_at DESC
        """, conn, params=(cutoff_str, min_score))

        conn.close()
        return df

    def get_signal_distribution(self, hours: int = 24) -> Dict:
        """Sinyal dağılımı"""
        conn = self.db.get_connection()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                signal,
                COUNT(*) as count,
                AVG(score) as avg_score
            FROM signals
            WHERE created_at >= ?
            GROUP BY signal
        """, (cutoff_str,))

        results = cursor.fetchall()
        conn.close()

        distribution = {}
        for signal, count, avg_score in results:
            distribution[signal] = {
                'count': count,
                'avg_score': round(avg_score, 1)
            }

        return distribution

    def get_top_signals(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """En yüksek skorlu sinyaller"""
        df = self.get_recent_signals(hours=hours)

        if len(df) == 0:
            return []

        # Score'a göre sırala
        df = df.sort_values('score', ascending=False)

        # İlk N tanesini al
        top_df = df.head(limit)

        # Dict listesine çevir
        results = []
        for _, row in top_df.iterrows():
            results.append({
                'ticker': row['ticker'],
                'timeframe': row['timeframe'],
                'signal': row['signal'],
                'score': row['score'],
                'created_at': row['created_at']
            })

        return results

    def get_active_tickers(self) -> List[str]:
        """Aktif hisseler"""
        return self.db.get_all_tickers()

    def get_data_freshness(self) -> Dict:
        """Veri güncellik durumu"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                timeframe,
                COUNT(DISTINCT ticker) as ticker_count,
                MAX(created_at) as last_update
            FROM ohlcv_data
            GROUP BY timeframe
        """)

        results = cursor.fetchall()
        conn.close()

        freshness = {}
        for timeframe, ticker_count, last_update in results:
            freshness[timeframe] = {
                'ticker_count': ticker_count,
                'last_update': last_update
            }

        return freshness

    def print_dashboard(self, refresh_interval: int = 60):
        """Dashboard göster (console-based)"""

        try:
            while True:
                # Ekranı temizle (Linux/Mac)
                os.system('clear' if os.name != 'nt' else 'cls')

                # Header
                print("\n" + "="*80)
                print(f"{'🤖 LIVE TRADING MONITOR':^80}")
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
                print("="*80)

                # Son 24 saatteki sinyal dağılımı
                print("\n📊 SİNYAL DAĞILIMI (Son 24 Saat)")
                print("-" * 80)
                distribution = self.get_signal_distribution(hours=24)

                if distribution:
                    for signal, data in distribution.items():
                        emoji = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "⚪")
                        print(f"{emoji} {signal:8s} | Adet: {data['count']:4d} | Ort. Skor: {data['avg_score']:5.1f}")
                else:
                    print("   Henüz sinyal yok")

                # En yüksek skorlu sinyaller
                print("\n🔥 EN YÜKSEK SKORLU SİNYALLER (Son 24 Saat)")
                print("-" * 80)
                top_signals = self.get_top_signals(hours=24, limit=10)

                if top_signals:
                    print(f"{'Hisse':12s} | {'TF':4s} | {'Sinyal':6s} | {'Skor':5s} | {'Tarih':19s}")
                    print("-" * 80)

                    for sig in top_signals:
                        emoji = "🟢" if sig['signal'] == "BUY" else ("🔴" if sig['signal'] == "SELL" else "⚪")
                        print(f"{emoji} {sig['ticker']:10s} | {sig['timeframe']:4s} | {sig['signal']:6s} | "
                              f"{sig['score']:5.1f} | {sig['created_at']}")
                else:
                    print("   Henüz sinyal yok")

                # Veri güncellik durumu
                print("\n📡 VERİ GÜNCELLİK DURUMU")
                print("-" * 80)
                freshness = self.get_data_freshness()

                if freshness:
                    for tf, data in sorted(freshness.items()):
                        print(f"{tf:6s} | Hisse: {data['ticker_count']:3d} | Son: {data['last_update']}")
                else:
                    print("   Henüz veri yok")

                # Aktif hisseler
                active_tickers = self.get_active_tickers()
                print(f"\n📈 Toplam Aktif Hisse: {len(active_tickers)}")

                # Footer
                print("\n" + "="*80)
                print(f"⏳ {refresh_interval} saniye sonra yenilenecek... (Ctrl+C ile çıkış)")
                print("="*80)

                # Bekle
                time.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\n\n✅ Monitor kapatıldı")

    def export_report(self, hours: int = 24, filename: str = None):
        """Rapor export et"""
        if filename is None:
            filename = f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"LIVE TRADING RAPORU\n")
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")

            # Sinyal dağılımı
            f.write("SİNYAL DAĞILIMI (Son {} Saat)\n".format(hours))
            f.write("-" * 80 + "\n")
            distribution = self.get_signal_distribution(hours=hours)

            for signal, data in distribution.items():
                f.write(f"{signal:8s} | Adet: {data['count']:4d} | Ort. Skor: {data['avg_score']:5.1f}\n")

            # En yüksek skorlu sinyaller
            f.write("\n\nEN YÜKSEK SKORLU SİNYALLER (Son {} Saat)\n".format(hours))
            f.write("-" * 80 + "\n")
            top_signals = self.get_top_signals(hours=hours, limit=20)

            for sig in top_signals:
                f.write(f"{sig['ticker']:12s} | {sig['timeframe']:4s} | {sig['signal']:6s} | "
                       f"{sig['score']:5.1f} | {sig['created_at']}\n")

            # Veri güncellik
            f.write("\n\nVERİ GÜNCELLİK DURUMU\n")
            f.write("-" * 80 + "\n")
            freshness = self.get_data_freshness()

            for tf, data in sorted(freshness.items()):
                f.write(f"{tf:6s} | Hisse: {data['ticker_count']:3d} | Son: {data['last_update']}\n")

            f.write("\n" + "="*80 + "\n")

        print(f"✅ Rapor kaydedildi: {filename}")
        return filename


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description='Live Trading Monitor')
    parser.add_argument('--dashboard', action='store_true',
                       help='Show live dashboard')
    parser.add_argument('--export', action='store_true',
                       help='Export report')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours to look back (default: 24)')
    parser.add_argument('--refresh', type=int, default=60,
                       help='Dashboard refresh interval in seconds (default: 60)')

    args = parser.parse_args()

    monitor = LiveTradingMonitor()

    if args.dashboard:
        monitor.print_dashboard(refresh_interval=args.refresh)
    elif args.export:
        monitor.export_report(hours=args.hours)
    else:
        # Basit özet göster
        print("\n📊 SİNYAL DAĞILIMI (Son {} Saat)".format(args.hours))
        print("="*70)
        distribution = monitor.get_signal_distribution(hours=args.hours)

        for signal, data in distribution.items():
            emoji = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "⚪")
            print(f"{emoji} {signal:8s} | Adet: {data['count']:4d} | Ort. Skor: {data['avg_score']:5.1f}")

        print("\n🔥 EN YÜKSEK SKORLU SİNYALLER")
        print("="*70)
        top_signals = monitor.get_top_signals(hours=args.hours, limit=10)

        for sig in top_signals:
            emoji = "🟢" if sig['signal'] == "BUY" else ("🔴" if sig['signal'] == "SELL" else "⚪")
            print(f"{emoji} {sig['ticker']:12s} | {sig['timeframe']:4s} | {sig['signal']:6s} | "
                  f"{sig['score']:5.1f} | {sig['created_at']}")

        print()


if __name__ == '__main__':
    main()
