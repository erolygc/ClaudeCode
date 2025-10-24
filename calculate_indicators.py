"""
Toplu İndikatör Hesaplama - Tüm hisseler için indikatörleri hesapla

PERFORMANS OPTİMİZASYONU:
- Bulk INSERT kullanımı (tek seferde tüm indikatörler)
- Database indexing
- ~10x daha hızlı!
"""
import time
import numpy as np
from database.db_manager import DatabaseManager
from indicators.technical_indicators import TechnicalIndicators


def main():
    print("="*80)
    print("📐 İNDİKATÖR HESAPLAMA SİSTEMİ - FAZ 7 (OPTIMIZED)")
    print("="*80)
    print()

    start_time = time.time()
    db = DatabaseManager()

    # Tüm hisse-timeframe çiftlerini al
    tickers = db.get_all_tickers()

    total_indicators = 0
    total_stocks_processed = 0

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            print(f"📊 {ticker} ({timeframe})", end=" ", flush=True)

            # OHLCV verisini al
            df = db.get_ohlcv_data(ticker, timeframe)

            if df is None or len(df) < 200:  # En az 200 bar olmalı (SMA200 için)
                print("⚠️  Yetersiz veri")
                continue

            # İndikatörleri hesapla
            calc = TechnicalIndicators(df)
            indicators = calc.calculate_all()

            # BULK INSERT - Tüm indikatörleri tek seferde kaydet (ÇOK HIZLI!)
            saved = db.add_indicator_values_bulk(
                ticker=ticker,
                timeframe=timeframe,
                indicators_dict=indicators,
                dates=df.index
            )

            total_indicators += saved
            total_stocks_processed += 1
            print(f"✅ {saved:,} indikatör")

    elapsed_time = time.time() - start_time

    print("\n" + "="*80)
    print(f"✅ Toplam {total_indicators:,} indikatör değeri hesaplandı!")
    print(f"📊 İşlenen hisse-timeframe çifti: {total_stocks_processed}")
    print(f"⏱️  Süre: {elapsed_time:.2f} saniye")
    print(f"🚀 Hız: {total_indicators/elapsed_time:.0f} indikatör/saniye")
    print("="*80)


if __name__ == "__main__":
    main()
