"""
Backtest Engine - Sinyal performansını geriye dönük test eder
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from config.settings import BACKTEST_SETTINGS

class BacktestEngine:
    """Backtest motoru - Sinyalleri geriye dönük test eder"""

    def __init__(self):
        self.db = DatabaseManager()
        self.commission = BACKTEST_SETTINGS['commission']
        self.slippage = BACKTEST_SETTINGS['slippage']

    def run_signal_backtest(self, ticker, timeframe, signal_type, signal_date, signal_score):
        """
        Bir sinyali geriye dönük test eder

        Args:
            ticker: Hisse senedi kodu
            timeframe: Zaman dilimi
            signal_type: Sinyal tipi (BUY/SELL/HOLD)
            signal_date: Sinyal tarihi
            signal_score: Sinyal gücü (0-100)

        Returns:
            dict: Backtest sonuçları
        """
        # HOLD sinyallerini test etme
        if signal_type == 'HOLD':
            return None

        # Sinyal tarihinden sonraki verileri al
        df = self.db.get_ohlcv_data(ticker, timeframe)
        if df is None or len(df) == 0:
            return None

        df = df.reset_index()
        df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
        signal_datetime = pd.to_datetime(signal_date, format='mixed', utc=True)

        # Sinyal tarihinden sonraki verileri filtrele
        future_data = df[df['date'] > signal_datetime].copy()
        if len(future_data) == 0:
            return None

        # Giriş fiyatı (bir sonraki barın açılışı + slippage)
        entry_price = future_data.iloc[0]['Open']
        entry_date = future_data.iloc[0]['date']

        if signal_type == 'BUY':
            entry_price = entry_price * (1 + self.slippage)
        else:  # SELL
            entry_price = entry_price * (1 - self.slippage)

        # İşlem maliyeti
        entry_cost = entry_price * self.commission

        # Holding period için veri
        holding_period_bars = min(len(future_data), BACKTEST_SETTINGS['holding_period'])
        test_data = future_data.iloc[:holding_period_bars].copy()

        # Performans metriklerini hesapla
        results = self._calculate_performance(
            test_data, entry_price, entry_cost, signal_type, ticker, timeframe
        )

        # Ek bilgiler
        results.update({
            'ticker': ticker,
            'timeframe': timeframe,
            'signal_type': signal_type,
            'signal_score': signal_score,
            'signal_date': signal_date,
            'entry_date': str(entry_date),
            'entry_price': entry_price
        })

        return results

    def _calculate_performance(self, data, entry_price, entry_cost, signal_type, ticker, timeframe):
        """Performans metriklerini hesaplar"""

        results = {
            'bars_held': len(data),
            'exit_date': str(data.iloc[-1]['date']),
            'exit_price': data.iloc[-1]['Close']
        }

        if signal_type == 'BUY':
            # BUY için: Fiyat artışı kar, düşüş zarar
            exit_price = results['exit_price'] * (1 - self.slippage)  # Slippage
            exit_cost = exit_price * self.commission

            total_cost = entry_cost + exit_cost
            gross_return = ((exit_price - entry_price) / entry_price) * 100
            net_return = gross_return - (total_cost / entry_price) * 100

            # Max drawdown (holding period boyunca)
            data['return_from_entry'] = ((data['Close'] - entry_price) / entry_price) * 100
            max_dd = data['return_from_entry'].min()

            # Max profit (holding period boyunca)
            max_profit = data['return_from_entry'].max()

        else:  # SELL (short)
            # SELL için: Fiyat düşüşü kar, artış zarar
            exit_price = results['exit_price'] * (1 + self.slippage)  # Slippage
            exit_cost = exit_price * self.commission

            total_cost = entry_cost + exit_cost
            gross_return = ((entry_price - exit_price) / entry_price) * 100
            net_return = gross_return - (total_cost / entry_price) * 100

            # Max drawdown (holding period boyunca)
            data['return_from_entry'] = ((entry_price - data['Close']) / entry_price) * 100
            max_dd = -data['return_from_entry'].max()  # Negatif çünkü fiyat artışı zarar

            # Max profit (holding period boyunca)
            max_profit = -data['return_from_entry'].min()

        results.update({
            'gross_return_pct': round(gross_return, 2),
            'net_return_pct': round(net_return, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'max_profit_pct': round(max_profit, 2),
            'total_cost_pct': round((total_cost / entry_price) * 100, 3),
            'win': 1 if net_return > 0 else 0
        })

        return results

    def backtest_all_signals(self):
        """Tüm sinyalleri test eder"""

        # Veritabanından tüm sinyalleri al
        conn = self.db.get_connection()
        signals_df = pd.read_sql_query("""
            SELECT ticker, timeframe, signal, score, created_at
            FROM signals
            ORDER BY created_at DESC
        """, conn)
        conn.close()

        if len(signals_df) == 0:
            print("⚠️  Veritabanında sinyal bulunamadı!")
            return None

        print(f"📊 {len(signals_df)} sinyal test ediliyor...\n")

        # Her sinyali test et
        results = []
        for idx, row in signals_df.iterrows():
            result = self.run_signal_backtest(
                ticker=row['ticker'],
                timeframe=row['timeframe'],
                signal_type=row['signal'],
                signal_date=row['created_at'],
                signal_score=row['score']
            )

            if result:
                results.append(result)
                status = "✅" if result['win'] == 1 else "❌"
                print(f"{status} {row['ticker']} ({row['timeframe']}) - {row['signal']}: {result['net_return_pct']}%")

        if len(results) == 0:
            print("⚠️  Test edilebilir sinyal bulunamadı!")
            return None

        # DataFrame'e çevir
        results_df = pd.DataFrame(results)

        # Veritabanına kaydet
        self._save_results(results_df)

        return results_df

    def _save_results(self, results_df):
        """Backtest sonuçlarını veritabanına kaydeder"""

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Backtest results tablosu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_score REAL,
                signal_date TEXT,
                entry_date TEXT,
                entry_price REAL,
                exit_date TEXT,
                exit_price REAL,
                bars_held INTEGER,
                gross_return_pct REAL,
                net_return_pct REAL,
                max_drawdown_pct REAL,
                max_profit_pct REAL,
                total_cost_pct REAL,
                win INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sonuçları kaydet
        for _, row in results_df.iterrows():
            cursor.execute("""
                INSERT INTO backtest_results
                (ticker, timeframe, signal_type, signal_score, signal_date, entry_date,
                 entry_price, exit_date, exit_price, bars_held, gross_return_pct,
                 net_return_pct, max_drawdown_pct, max_profit_pct, total_cost_pct, win)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['ticker'], row['timeframe'], row['signal_type'], row['signal_score'],
                row['signal_date'], row['entry_date'], row['entry_price'],
                row['exit_date'], row['exit_price'], row['bars_held'],
                row['gross_return_pct'], row['net_return_pct'],
                row['max_drawdown_pct'], row['max_profit_pct'],
                row['total_cost_pct'], row['win']
            ))

        conn.commit()
        conn.close()
        print(f"\n💾 {len(results_df)} backtest sonucu veritabanına kaydedildi!")

    def generate_performance_report(self, results_df):
        """Performans raporu oluşturur"""

        if results_df is None or len(results_df) == 0:
            return

        print("\n" + "="*80)
        print("📈 BACKTEST PERFORMANS RAPORU")
        print("="*80)

        # Genel istatistikler
        total_trades = len(results_df)
        winning_trades = results_df[results_df['win'] == 1]
        losing_trades = results_df[results_df['win'] == 0]

        win_rate = (len(winning_trades) / total_trades) * 100
        avg_return = results_df['net_return_pct'].mean()
        avg_win = winning_trades['net_return_pct'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['net_return_pct'].mean() if len(losing_trades) > 0 else 0

        print(f"\n📊 GENEL İSTATİSTİKLER:")
        print(f"   Toplam İşlem: {total_trades}")
        print(f"   Kazanan İşlem: {len(winning_trades)} ({win_rate:.1f}%)")
        print(f"   Kaybeden İşlem: {len(losing_trades)} ({100-win_rate:.1f}%)")
        print(f"   Ortalama Getiri: {avg_return:.2f}%")
        print(f"   Ortalama Kazanç: {avg_win:.2f}%")
        print(f"   Ortalama Kayıp: {avg_loss:.2f}%")

        # Sinyal tipine göre performans
        print(f"\n📍 SİNYAL TİPİNE GÖRE PERFORMANS:")
        for signal_type in results_df['signal_type'].unique():
            signal_trades = results_df[results_df['signal_type'] == signal_type]
            signal_wins = signal_trades[signal_trades['win'] == 1]
            signal_win_rate = (len(signal_wins) / len(signal_trades)) * 100
            signal_avg_return = signal_trades['net_return_pct'].mean()

            print(f"   {signal_type}:")
            print(f"      İşlem: {len(signal_trades)}, Kazanma: {signal_win_rate:.1f}%, Ort. Getiri: {signal_avg_return:.2f}%")

        # Hisse bazında performans
        print(f"\n🏆 HİSSE BAZINDA PERFORMANS (En İyi 5):")
        stock_performance = results_df.groupby('ticker').agg({
            'net_return_pct': 'mean',
            'win': 'sum',
            'ticker': 'count'
        }).rename(columns={'ticker': 'count'})
        stock_performance['win_rate'] = (stock_performance['win'] / stock_performance['count']) * 100
        stock_performance = stock_performance.sort_values('net_return_pct', ascending=False)

        for idx, (ticker, row) in enumerate(stock_performance.head(5).iterrows(), 1):
            print(f"   {idx}. {ticker}: {row['net_return_pct']:.2f}% avg return, {row['win_rate']:.1f}% win rate ({int(row['count'])} trades)")

        # Timeframe bazında performans
        print(f"\n⏰ TIMEFRAME BAZINDA PERFORMANS:")
        tf_performance = results_df.groupby('timeframe').agg({
            'net_return_pct': 'mean',
            'win': 'sum',
            'timeframe': 'count'
        }).rename(columns={'timeframe': 'count'})
        tf_performance['win_rate'] = (tf_performance['win'] / tf_performance['count']) * 100

        for tf, row in tf_performance.iterrows():
            print(f"   {tf}: {row['net_return_pct']:.2f}% avg return, {row['win_rate']:.1f}% win rate ({int(row['count'])} trades)")

        # En iyi ve en kötü işlemler
        print(f"\n🌟 EN İYİ 3 İŞLEM:")
        best_trades = results_df.nlargest(3, 'net_return_pct')
        for idx, row in best_trades.iterrows():
            print(f"   {row['ticker']} ({row['timeframe']}) - {row['signal_type']}: {row['net_return_pct']:.2f}%")

        print(f"\n💔 EN KÖTÜ 3 İŞLEM:")
        worst_trades = results_df.nsmallest(3, 'net_return_pct')
        for idx, row in worst_trades.iterrows():
            print(f"   {row['ticker']} ({row['timeframe']}) - {row['signal_type']}: {row['net_return_pct']:.2f}%")

        # Sinyal gücü analizi
        print(f"\n💪 SİNYAL GÜCÜ ANALİZİ:")

        # Güçlü sinyaller (>=65 veya <=35)
        strong_signals = results_df[(results_df['signal_score'] >= 65) | (results_df['signal_score'] <= 35)]
        weak_signals = results_df[(results_df['signal_score'] > 35) & (results_df['signal_score'] < 65)]

        if len(strong_signals) > 0:
            strong_win_rate = (strong_signals['win'].sum() / len(strong_signals)) * 100
            strong_avg_return = strong_signals['net_return_pct'].mean()
            print(f"   Güçlü Sinyaller (Score >=65 or <=35):")
            print(f"      İşlem: {len(strong_signals)}, Kazanma: {strong_win_rate:.1f}%, Ort. Getiri: {strong_avg_return:.2f}%")

        if len(weak_signals) > 0:
            weak_win_rate = (weak_signals['win'].sum() / len(weak_signals)) * 100
            weak_avg_return = weak_signals['net_return_pct'].mean()
            print(f"   Zayıf Sinyaller (Score 35-65):")
            print(f"      İşlem: {len(weak_signals)}, Kazanma: {weak_win_rate:.1f}%, Ort. Getiri: {weak_avg_return:.2f}%")

        print("\n" + "="*80)


if __name__ == "__main__":
    engine = BacktestEngine()
    results = engine.backtest_all_signals()
    if results is not None:
        engine.generate_performance_report(results)
