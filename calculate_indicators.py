"""
Toplu İndikatör Hesaplama - Tüm hisseler için indikatörleri hesapla
"""
from database.db_manager import DatabaseManager
from indicators.technical_indicators import TechnicalIndicators

def main():
    print("="*80)
    print("📐 İNDİKATÖR HESAPLAMA SİSTEMİ - FAZ 7")
    print("="*80)
    print()

    db = DatabaseManager()

    # Tüm hisse-timeframe çiftlerini al
    tickers = db.get_all_tickers()

    total_indicators = 0

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            print(f"📊 {ticker} ({timeframe})", end=" ")

            # OHLCV verisini al
            df = db.get_ohlcv_data(ticker, timeframe)

            if df is None or len(df) < 200:  # En az 200 bar olmalı (SMA200 için)
                print("⚠️  Yetersiz veri")
                continue

            # İndikatörleri hesapla
            calc = TechnicalIndicators(df)
            indicators = calc.calculate_all()

            # Veritabanına kaydet
            saved = 0
            for ind_name, ind_values in indicators.items():
                for date_idx, value in zip(df.index, ind_values):
                    if not np.isnan(value):  # NaN değerleri kaydetme
                        db.add_indicator_value(ticker, timeframe, date_idx, ind_name, float(value))
                        saved += 1

            total_indicators += saved
            print(f"✅ {saved:,} indikatör değeri")

    print("\n" + "="*80)
    print(f"✅ Toplam {total_indicators:,} indikatör değeri hesaplandı!")
    print("="*80)

if __name__ == "__main__":
    import numpy as np
    main()
