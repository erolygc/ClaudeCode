"""
Sample Data Generator - Backtest test etmek için örnek veri oluştur
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from config.settings import TEST_HISSELER, TIMEFRAMES
from indicators.technical_indicators import TechnicalIndicators
from strategies.signal_generator import SignalGenerator
import json

def generate_sample_ohlcv(bars=500, start_price=100, volatility=0.02):
    """
    Rastgele ama gerçekçi OHLCV verisi oluştur

    Args:
        bars: Bar sayısı
        start_price: Başlangıç fiyatı
        volatility: Volatilite (günlük değişim yüzdesi)
    """
    dates = pd.date_range(end=datetime.now(), periods=bars, freq='D')

    # Random walk ile fiyat serisi oluştur
    returns = np.random.normal(0, volatility, bars)
    price = start_price * (1 + returns).cumprod()

    data = []
    for i, (date, close) in enumerate(zip(dates, price)):
        # Her bar için High/Low/Open oluştur
        daily_volatility = close * volatility
        high = close + abs(np.random.normal(0, daily_volatility))
        low = close - abs(np.random.normal(0, daily_volatility))
        open_price = low + (high - low) * np.random.random()

        # Volume (rastgele ama gerçekçi)
        volume = int(np.random.lognormal(15, 1))

        data.append({
            'date': date,
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': volume
        })

    df = pd.DataFrame(data)
    df = df.set_index('date')
    return df


def main():
    print("="*80)
    print("🔧 SAMPLE DATA GENERATOR - Test Verisi Oluştur")
    print("="*80)
    print()

    db = DatabaseManager()

    # 1. OHLCV verisi oluştur
    print("📊 FAZ 6: OHLCV Verisi Oluşturuluyor...")
    total_bars = 0

    for i, ticker in enumerate(TEST_HISSELER[:3]):  # İlk 3 hisse
        print(f"\n📈 {ticker}")
        db.add_stock(ticker)

        for tf_name in TIMEFRAMES.keys():
            # Sample veri oluştur
            if tf_name == '1d':
                bars = 500
                start_price = 50 + i * 20  # Her hisse farklı fiyat seviyesinde
            else:  # 1h
                bars = 400
                start_price = 50 + i * 20

            df = generate_sample_ohlcv(bars=bars, start_price=start_price)

            # Veritabanına kaydet
            db.add_ohlcv_data(ticker, tf_name, df)
            total_bars += len(df)

            print(f"  ✅ {tf_name}: {len(df)} bar")

    print(f"\n📊 Toplam {total_bars:,} bar veri oluşturuldu!")

    # 2. İndikatörleri hesapla
    print("\n" + "="*80)
    print("📐 FAZ 7: İndikatörler Hesaplanıyor...")
    print("="*80)

    total_indicators = 0
    tickers = db.get_all_tickers()

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            print(f"📊 {ticker} ({timeframe})", end=" ")

            df = db.get_ohlcv_data(ticker, timeframe)

            if df is None or len(df) < 200:
                print("⚠️  Yetersiz veri")
                continue

            # İndikatörleri hesapla
            calc = TechnicalIndicators(df)
            indicators = calc.calculate_all()

            # Veritabanına kaydet
            saved = 0
            for ind_name, ind_values in indicators.items():
                for date_idx, value in zip(df.index, ind_values):
                    if not np.isnan(value):
                        db.add_indicator_value(ticker, timeframe, date_idx, ind_name, float(value))
                        saved += 1

            total_indicators += saved
            print(f"✅ {saved:,} indikatör")

    print(f"\n✅ Toplam {total_indicators:,} indikatör değeri hesaplandı!")

    # 3. Sinyalleri üret
    print("\n" + "="*80)
    print("🎯 FAZ 8: Sinyaller Üretiliyor...")
    print("="*80)

    generator = SignalGenerator()
    signals_count = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    strong_signals = []

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            print(f"🎯 {ticker} ({timeframe})", end=" ")

            result = generator.generate_combined_signal(ticker, timeframe)

            # Veritabanına kaydet
            db.add_signal(
                ticker=ticker,
                timeframe=timeframe,
                signal=result['signal'],
                score=result['score'],
                details=json.dumps(result['details'])
            )

            signals_count[result['signal']] += 1

            if result['score'] >= 65 or result['score'] <= 35:
                strong_signals.append({
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'signal': result['signal'],
                    'score': result['score']
                })

            emoji = "🟢" if result['signal'] == 'BUY' else ("🔴" if result['signal'] == 'SELL' else "🟡")
            print(f"{emoji} {result['signal']} ({result['score']:.1f}/100)")

    # Özet
    print("\n" + "="*80)
    total = sum(signals_count.values())
    print(f"✅ Toplam {total} sinyal üretildi!")
    print(f"   🟢 AL: {signals_count['BUY']}, 🔴 SAT: {signals_count['SELL']}, 🟡 BEKLE: {signals_count['HOLD']}")

    if strong_signals:
        print(f"\n💪 Güçlü Sinyaller: {len(strong_signals)}")
        for sig in strong_signals[:5]:
            emoji = "🟢" if sig['signal'] == 'BUY' else "🔴"
            print(f"   {emoji} {sig['ticker']} ({sig['timeframe']}): {sig['score']:.1f}/100")

    print("\n" + "="*80)
    print("✅ Test verisi hazır! Şimdi backtest çalıştırabilirsiniz:")
    print("   python backtest_all.py")
    print("="*80)


if __name__ == "__main__":
    main()
