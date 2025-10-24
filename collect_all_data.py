"""
Toplu Veri Toplama - Tüm hisseler için veri topla
"""
from collectors.market_data_collector import MarketDataCollector
from database.db_manager import DatabaseManager
from config.settings import TEST_HISSELER, TIMEFRAMES

def main():
    print("="*80)
    print("📊 VERİ TOPLAMA SİSTEMİ - FAZ 6")
    print("="*80)
    print()

    collector = MarketDataCollector()
    db = DatabaseManager()

    total_bars = 0
    total_stocks = 0

    for ticker in TEST_HISSELER:
        print(f"\n📈 {ticker}")

        # Hisseyi veritabanına ekle
        db.add_stock(ticker)

        for tf_name, tf_config in TIMEFRAMES.items():
            # Veri topla
            data = collector.collect_data(
                ticker=ticker,
                timeframe=tf_config['interval'],
                period=tf_config['period']
            )

            if data is not None:
                # Veritabanına kaydet
                added = db.add_ohlcv_data(ticker, tf_name, data)
                total_bars += len(data)
                total_stocks += 1

    print("\n" + "="*80)
    print(f"✅ Toplam {total_stocks} hisse-timeframe çifti için {total_bars:,} bar veri toplandı!")
    print("="*80)

if __name__ == "__main__":
    main()
