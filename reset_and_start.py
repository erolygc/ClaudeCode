#!/usr/bin/env python3
"""
Sistem Sıfırlama ve Yeni Başlatma Script
Bu script trading sistemini temizler ve fresh data ile başlatır
"""
import os
import sys
import shutil
from datetime import datetime

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import DATABASE_PATH, ACTIVE_STOCKS
from database.db_manager import DatabaseManager
from data.data_fetcher import DataFetcher


def backup_database():
    """Mevcut database'i yedekle"""
    if os.path.exists(DATABASE_PATH):
        backup_path = DATABASE_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        shutil.copy2(DATABASE_PATH, backup_path)
        print(f"✅ Database yedeklendi: {backup_path}")
        return backup_path
    else:
        print("⚠️  Database dosyası bulunamadı, yedekleme atlandı")
        return None


def reset_database():
    """Database'i sıfırla"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print(f"✅ Eski database silindi: {DATABASE_PATH}")

    # Yeni database oluştur
    db = DatabaseManager()
    print(f"✅ Yeni database oluşturuldu: {DATABASE_PATH}")
    return db


def download_fresh_data(stock_count=10):
    """Fresh data indir"""
    print(f"\n{'='*80}")
    print(f"📊 VERİ İNDİRME BAŞLIYOR")
    print(f"{'='*80}")
    print(f"Hisse sayısı: {stock_count}")
    print(f"Timeframe'ler: 1d, 1h")
    print(f"{'='*80}\n")

    fetcher = DataFetcher()
    stocks = ACTIVE_STOCKS[:stock_count]

    success_count = 0
    fail_count = 0

    for ticker in stocks:
        try:
            print(f"📈 {ticker} indiriliyor...")

            # 1d data
            df_1d = fetcher.fetch_ohlcv(ticker, timeframe='1d', limit=500)
            if df_1d is not None and len(df_1d) > 0:
                print(f"   ✅ 1d: {len(df_1d)} bar")
            else:
                print(f"   ❌ 1d: Veri alınamadı")
                fail_count += 1
                continue

            # 1h data
            df_1h = fetcher.fetch_ohlcv(ticker, timeframe='1h', limit=400)
            if df_1h is not None and len(df_1h) > 0:
                print(f"   ✅ 1h: {len(df_1h)} bar")
            else:
                print(f"   ⚠️  1h: Veri alınamadı (1d verisi kaydedildi)")

            success_count += 1

        except Exception as e:
            print(f"   ❌ Hata: {e}")
            fail_count += 1
            continue

    print(f"\n{'='*80}")
    print(f"📊 VERİ İNDİRME TAMAMLANDI")
    print(f"✅ Başarılı: {success_count}/{stock_count}")
    print(f"❌ Başarısız: {fail_count}/{stock_count}")
    print(f"{'='*80}\n")


def calculate_indicators():
    """İndikatörleri hesapla"""
    print(f"\n{'='*80}")
    print(f"📐 İNDİKATÖRLER HESAPLANIYOR")
    print(f"{'='*80}\n")

    from strategies.indicator_calculator import IndicatorCalculator

    calculator = IndicatorCalculator()
    db = DatabaseManager()
    conn = db.get_connection()

    # Tüm ticker ve timeframe'leri al
    import pandas as pd
    stocks = pd.read_sql_query("""
        SELECT DISTINCT ticker, timeframe
        FROM ohlcv_data
        ORDER BY ticker, timeframe
    """, conn)
    conn.close()

    success_count = 0
    for _, row in stocks.iterrows():
        ticker = row['ticker']
        timeframe = row['timeframe']

        try:
            print(f"📊 {ticker} ({timeframe}) hesaplanıyor...")
            calculator.calculate_and_save(ticker, timeframe)
            print(f"   ✅ Tamamlandı")
            success_count += 1
        except Exception as e:
            print(f"   ❌ Hata: {e}")

    print(f"\n{'='*80}")
    print(f"✅ {success_count}/{len(stocks)} indikatör hesaplandı")
    print(f"{'='*80}\n")


def generate_signals():
    """Sinyalleri üret"""
    print(f"\n{'='*80}")
    print(f"🎯 SİNYALLER ÜRETİLİYOR")
    print(f"{'='*80}\n")

    from strategies.signal_generator import SignalGenerator

    generator = SignalGenerator()
    db = DatabaseManager()
    conn = db.get_connection()

    # Tüm ticker ve timeframe'leri al
    import pandas as pd
    stocks = pd.read_sql_query("""
        SELECT DISTINCT ticker, timeframe
        FROM indicators
        ORDER BY ticker, timeframe
    """, conn)
    conn.close()

    success_count = 0
    for _, row in stocks.iterrows():
        ticker = row['ticker']
        timeframe = row['timeframe']

        try:
            signal = generator.generate_signal(ticker, timeframe)
            if signal:
                print(f"{'🟢' if signal['signal'] == 'BUY' else '🔴' if signal['signal'] == 'SELL' else '🟡'} "
                      f"{ticker} ({timeframe}): {signal['signal']} - {signal['score']:.1f}/100")
                success_count += 1
        except Exception as e:
            print(f"❌ {ticker} ({timeframe}): {e}")

    print(f"\n{'='*80}")
    print(f"✅ {success_count}/{len(stocks)} sinyal üretildi")
    print(f"{'='*80}\n")


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description='Sistemi sıfırla ve fresh data ile başlat')
    parser.add_argument('--backup', action='store_true', help='Mevcut database\'i yedekle')
    parser.add_argument('--stocks', type=int, default=50, help='İndirilecek hisse sayısı (default: 50)')
    parser.add_argument('--skip-data', action='store_true', help='Veri indirme adımını atla')
    parser.add_argument('--skip-indicators', action='store_true', help='İndikatör hesaplama adımını atla')
    parser.add_argument('--skip-signals', action='store_true', help='Sinyal üretme adımını atla')

    args = parser.parse_args()

    print(f"\n{'='*80}")
    print(f"🔄 SİSTEM SIFIRLAMA VE YENİDEN BAŞLATMA")
    print(f"{'='*80}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # 1. Yedekleme
    if args.backup:
        print("1️⃣  DATABASE YEDEKLENİYOR...")
        backup_database()
        print()

    # 2. Database sıfırlama
    print("2️⃣  DATABASE SIFIRLANIYOR...")
    db = reset_database()
    print()

    # 3. Fresh data indirme
    if not args.skip_data:
        print("3️⃣  FRESH DATA İNDİRİLİYOR...")
        download_fresh_data(stock_count=args.stocks)
    else:
        print("3️⃣  ⏭️  Veri indirme atlandı (--skip-data)")
        print()

    # 4. İndikatör hesaplama
    if not args.skip_indicators:
        print("4️⃣  İNDİKATÖRLER HESAPLANIYOR...")
        calculate_indicators()
    else:
        print("4️⃣  ⏭️  İndikatör hesaplama atlandı (--skip-indicators)")
        print()

    # 5. Sinyal üretme
    if not args.skip_signals:
        print("5️⃣  SİNYALLER ÜRETİLİYOR...")
        generate_signals()
    else:
        print("5️⃣  ⏭️  Sinyal üretme atlandı (--skip-signals)")
        print()

    # Tamamlandı
    print(f"\n{'='*80}")
    print(f"✅ SİSTEM HAZIR!")
    print(f"{'='*80}")
    print(f"\nŞimdi yapabilecekleriniz:")
    print(f"")
    print(f"1. Paper Trading Başlat (Önerilen):")
    print(f"   python run_live_trading.py --mode paper --capital 100000")
    print(f"")
    print(f"2. Dashboard Başlat:")
    print(f"   python run_dashboard.py")
    print(f"   Tarayıcıda: http://127.0.0.1:5000")
    print(f"")
    print(f"3. Sistem Durumunu Kontrol Et:")
    print(f"   python tools/system_status.py")
    print(f"")
    print(f"4. Chart Pattern Taraması:")
    print(f"   python strategies/chart_patterns.py --scan --top 20")
    print(f"")
    print(f"5. Multi-Timeframe Analiz:")
    print(f"   python strategies/multi_timeframe_analyzer.py --scan --signal BUY --confidence 50 --top 20")
    print(f"")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
