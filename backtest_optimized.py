"""
Optimize Edilmiş Backtest - Hızlı ve verimli backtest
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from config.settings import BACKTEST_SETTINGS
import pandas as pd
import numpy as np
from datetime import datetime

class OptimizedBacktest:
    """Optimize edilmiş backtest engine"""

    def __init__(self):
        self.db = DatabaseManager()
        self.commission = BACKTEST_SETTINGS.get('commission', 0.001)
        self.slippage = BACKTEST_SETTINGS.get('slippage', 0.001)
        self.holding_period = BACKTEST_SETTINGS.get('holding_period', 20)

    def backtest_all_signals(self):
        """Tüm sinyalleri hızlı test et"""

        print("="*80)
        print("🚀 OPTİMİZE EDİLMİŞ BACKTEST - FAZ 9")
        print("="*80)
        print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        conn = self.db.get_connection()

        # Sadece BUY ve SELL sinyallerini al
        signals_df = pd.read_sql_query("""
            SELECT ticker, timeframe, signal, score, created_at
            FROM signals
            WHERE signal IN ('BUY', 'SELL')
            ORDER BY created_at DESC
        """, conn)

        if len(signals_df) == 0:
            print("⚠️  Test edilebilir sinyal bulunamadı!")
            conn.close()
            return None

        print(f"📊 {len(signals_df)} sinyal test ediliyor...")
        print(f"⚙️  Holding Period: {self.holding_period} bar")
        print(f"💰 Commission: {self.commission*100}%, Slippage: {self.slippage*100}%")
        print()

        # Her ticker-timeframe kombinasyonu için OHLCV verisini bir kez çek
        ohlcv_cache = {}

        results = []
        tested = 0
        skipped = 0

        for idx, row in signals_df.iterrows():
            ticker = row['ticker']
            timeframe = row['timeframe']
            signal_type = row['signal']
            signal_score = row['score']
            signal_date = row['created_at']

            # Cache key
            cache_key = f"{ticker}_{timeframe}"

            # OHLCV verisini cache'den al veya çek
            if cache_key not in ohlcv_cache:
                ohlcv_df = pd.read_sql_query(f"""
                    SELECT date, open, high, low, close, volume
                    FROM ohlcv_data
                    WHERE ticker = '{ticker}' AND timeframe = '{timeframe}'
                    ORDER BY date ASC
                """, conn)

                if len(ohlcv_df) == 0:
                    skipped += 1
                    continue

                # Column isimlerini büyük harfe çevir
                ohlcv_df.columns = ['date', 'Open', 'High', 'Low', 'Close', 'Volume']
                ohlcv_df['date'] = pd.to_datetime(ohlcv_df['date'])
                ohlcv_cache[cache_key] = ohlcv_df

            ohlcv_df = ohlcv_cache[cache_key]

            # Backtest yap
            result = self._test_signal(
                ohlcv_df, signal_date, signal_type, signal_score, ticker, timeframe
            )

            if result:
                results.append(result)
                tested += 1

                # İlerleme göster (her 50 sinyalde bir)
                if tested % 50 == 0:
                    status = "✅" if result['win'] == 1 else "❌"
                    print(f"  [{tested}/{len(signals_df)}] {status} {ticker} ({timeframe}) {signal_type}: {result['net_return_pct']:.2f}%")
            else:
                skipped += 1

        conn.close()

        print(f"\n✅ Test tamamlandı!")
        print(f"   Test edilen: {tested}")
        print(f"   Atlanan: {skipped}")

        if len(results) == 0:
            print("\n⚠️  Hiç backtest sonucu üretilmedi!")
            return None

        # DataFrame'e çevir
        results_df = pd.DataFrame(results)

        # Performans raporu
        self._print_report(results_df)

        # Excel'e kaydet
        try:
            excel_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            results_df.to_excel(excel_file, index=False)
            print(f"\n💾 Detaylı sonuçlar kaydedildi: {excel_file}")
        except Exception as e:
            print(f"\n⚠️  Excel kaydetme hatası: {e}")
            csv_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"💾 CSV olarak kaydedildi: {csv_file}")

        return results_df

    def _test_signal(self, ohlcv_df, signal_date, signal_type, signal_score, ticker, timeframe):
        """Tek bir sinyali test et"""

        signal_dt = pd.to_datetime(signal_date)

        # Sinyal tarihinden sonraki verileri bul
        future_data = ohlcv_df[ohlcv_df['date'] > signal_dt].copy()

        if len(future_data) == 0:
            return None

        # Giriş: Bir sonraki barın açılışı
        entry_price = future_data.iloc[0]['Open']
        entry_date = future_data.iloc[0]['date']

        if signal_type == 'BUY':
            entry_price = entry_price * (1 + self.slippage)
        else:  # SELL
            entry_price = entry_price * (1 - self.slippage)

        # Holding period kadar veri al
        test_period = min(len(future_data), self.holding_period)
        test_data = future_data.iloc[:test_period].copy()

        # Çıkış: Holding period sonundaki kapanış
        exit_price = test_data.iloc[-1]['Close']
        exit_date = test_data.iloc[-1]['date']

        if signal_type == 'BUY':
            exit_price = exit_price * (1 - self.slippage)
            gross_return = ((exit_price - entry_price) / entry_price) * 100

            # Max drawdown ve profit
            test_data['return_pct'] = ((test_data['Close'] - entry_price) / entry_price) * 100
            max_dd = test_data['return_pct'].min()
            max_profit = test_data['return_pct'].max()

        else:  # SELL (short)
            exit_price = exit_price * (1 + self.slippage)
            gross_return = ((entry_price - exit_price) / entry_price) * 100

            # Max drawdown ve profit (short için ters)
            test_data['return_pct'] = ((entry_price - test_data['Close']) / entry_price) * 100
            max_dd = -test_data['return_pct'].max()
            max_profit = -test_data['return_pct'].min()

        # Net return (komisyon dahil)
        total_cost = (entry_price * self.commission) + (exit_price * self.commission)
        net_return = gross_return - ((total_cost / entry_price) * 100)

        return {
            'ticker': ticker,
            'timeframe': timeframe,
            'signal_type': signal_type,
            'signal_score': signal_score,
            'signal_date': str(signal_date),
            'entry_date': str(entry_date),
            'entry_price': round(entry_price, 4),
            'exit_date': str(exit_date),
            'exit_price': round(exit_price, 4),
            'bars_held': len(test_data),
            'gross_return_pct': round(gross_return, 2),
            'net_return_pct': round(net_return, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'max_profit_pct': round(max_profit, 2),
            'win': 1 if net_return > 0 else 0
        }

    def _print_report(self, results_df):
        """Performans raporu yazdır"""

        print("\n" + "="*80)
        print("📈 BACKTEST PERFORMANS RAPORU")
        print("="*80)

        total = len(results_df)
        wins = results_df[results_df['win'] == 1]
        losses = results_df[results_df['win'] == 0]

        win_rate = (len(wins) / total) * 100
        avg_return = results_df['net_return_pct'].mean()
        avg_win = wins['net_return_pct'].mean() if len(wins) > 0 else 0
        avg_loss = losses['net_return_pct'].mean() if len(losses) > 0 else 0

        print(f"\n📊 GENEL İSTATİSTİKLER:")
        print(f"   Toplam İşlem: {total}")
        print(f"   Kazanan: {len(wins)} ({win_rate:.1f}%)")
        print(f"   Kaybeden: {len(losses)} ({100-win_rate:.1f}%)")
        print(f"   Ortalama Getiri: {avg_return:.2f}%")
        print(f"   Ortalama Kazanç: {avg_win:.2f}%")
        print(f"   Ortalama Kayıp: {avg_loss:.2f}%")

        # Sinyal tipine göre
        print(f"\n📍 SİNYAL TİPİNE GÖRE:")
        for signal_type in ['BUY', 'SELL']:
            sig_data = results_df[results_df['signal_type'] == signal_type]
            if len(sig_data) == 0:
                continue
            sig_wins = sig_data[sig_data['win'] == 1]
            sig_wr = (len(sig_wins) / len(sig_data)) * 100
            sig_avg = sig_data['net_return_pct'].mean()
            print(f"   {signal_type}: {len(sig_data)} işlem, {sig_wr:.1f}% kazanma, {sig_avg:.2f}% ort. getiri")

        # En iyi hisseler
        print(f"\n🏆 EN İYİ 5 HİSSE:")
        stock_perf = results_df.groupby('ticker')['net_return_pct'].agg(['mean', 'count'])
        stock_perf = stock_perf.sort_values('mean', ascending=False).head(5)
        for idx, (ticker, row) in enumerate(stock_perf.iterrows(), 1):
            print(f"   {idx}. {ticker}: {row['mean']:.2f}% ort. getiri ({int(row['count'])} işlem)")

        # En iyi timeframe'ler
        print(f"\n⏰ TIMEFRAME PERFORMANSI:")
        tf_perf = results_df.groupby('timeframe')['net_return_pct'].agg(['mean', 'count'])
        tf_perf = tf_perf.sort_values('mean', ascending=False)
        for tf, row in tf_perf.iterrows():
            print(f"   {tf}: {row['mean']:.2f}% ort. getiri ({int(row['count'])} işlem)")

        # En iyi 3 işlem
        print(f"\n🌟 EN İYİ 3 İŞLEM:")
        best = results_df.nlargest(3, 'net_return_pct')
        for idx, row in best.iterrows():
            print(f"   {row['ticker']} ({row['timeframe']}) {row['signal_type']}: {row['net_return_pct']:.2f}%")

        # En kötü 3 işlem
        print(f"\n💔 EN KÖTÜ 3 İŞLEM:")
        worst = results_df.nsmallest(3, 'net_return_pct')
        for idx, row in worst.iterrows():
            print(f"   {row['ticker']} ({row['timeframe']}) {row['signal_type']}: {row['net_return_pct']:.2f}%")

        print("\n" + "="*80)


def main():
    engine = OptimizedBacktest()
    results = engine.backtest_all_signals()

    if results is not None:
        print(f"\n✅ Backtest başarıyla tamamlandı!")
    else:
        print(f"\n⚠️  Backtest tamamlanamadı!")


if __name__ == "__main__":
    main()
