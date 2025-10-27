"""
End-to-End Test Script - Tüm Sistemi Test Et
"""
import sys
import os

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Tüm import'ları test et"""
    print("\n" + "="*70)
    print("📦 TEST 1: Import'lar Kontrol Ediliyor...")
    print("="*70)

    tests = []

    # Temel kütüphaneler
    try:
        import pandas as pd
        print("✅ pandas:", pd.__version__)
        tests.append(True)
    except ImportError as e:
        print(f"❌ pandas: {e}")
        tests.append(False)

    try:
        import numpy as np
        print("✅ numpy:", np.__version__)
        tests.append(True)
    except ImportError as e:
        print(f"❌ numpy: {e}")
        tests.append(False)

    try:
        import yfinance as yf
        print("✅ yfinance:", yf.__version__)
        tests.append(True)
    except ImportError as e:
        print(f"❌ yfinance: {e}")
        tests.append(False)

    try:
        import talib
        print("✅ talib:", talib.__version__)
        tests.append(True)
    except ImportError as e:
        print(f"❌ talib: {e}")
        print("   ⚠️  TA-Lib kurulu değil. WINDOWS_TALIB_INSTALL.md dosyasına bakın.")
        tests.append(False)

    # Proje modülleri
    try:
        from database.db_manager import DatabaseManager
        print("✅ DatabaseManager")
        tests.append(True)
    except ImportError as e:
        print(f"❌ DatabaseManager: {e}")
        tests.append(False)

    try:
        from collectors.market_data_collector import MarketDataCollector
        print("✅ MarketDataCollector")
        tests.append(True)
    except ImportError as e:
        print(f"❌ MarketDataCollector: {e}")
        tests.append(False)

    try:
        from indicators.technical_indicators import TechnicalIndicators
        print("✅ TechnicalIndicators")
        tests.append(True)
    except ImportError as e:
        print(f"❌ TechnicalIndicators: {e}")
        tests.append(False)

    try:
        from strategies.signal_generator import SignalGenerator
        print("✅ SignalGenerator")
        tests.append(True)
    except ImportError as e:
        print(f"❌ SignalGenerator: {e}")
        tests.append(False)

    try:
        from live_trading.live_engine import LiveTradingEngine
        print("✅ LiveTradingEngine")
        tests.append(True)
    except ImportError as e:
        print(f"❌ LiveTradingEngine: {e}")
        tests.append(False)

    try:
        from live_trading.risk_manager import RiskManager
        print("✅ RiskManager")
        tests.append(True)
    except ImportError as e:
        print(f"❌ RiskManager: {e}")
        tests.append(False)

    try:
        from live_trading.monitor import LiveTradingMonitor
        print("✅ LiveTradingMonitor")
        tests.append(True)
    except ImportError as e:
        print(f"❌ LiveTradingMonitor: {e}")
        tests.append(False)

    passed = sum(tests)
    total = len(tests)

    print(f"\n📊 Sonuç: {passed}/{total} test geçti")

    return all(tests)


def test_database():
    """Veritabanı bağlantısını test et"""
    print("\n" + "="*70)
    print("💾 TEST 2: Veritabanı Test Ediliyor...")
    print("="*70)

    try:
        from database.db_manager import DatabaseManager

        db = DatabaseManager()
        print("✅ Veritabanı bağlantısı başarılı")

        # Test hissesi ekle
        db.add_stock("TEST.IS", "Test Hisse", "Test")
        print("✅ Hisse ekleme başarılı")

        # Test verisi
        import pandas as pd
        test_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [105, 106, 107],
            'Low': [95, 96, 97],
            'Close': [103, 104, 105],
            'Volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3))

        added = db.add_ohlcv_data("TEST.IS", "1d", test_data)
        print(f"✅ OHLCV veri ekleme başarılı: {added} kayıt")

        # Veriyi geri oku
        retrieved = db.get_ohlcv_data("TEST.IS", "1d")
        if retrieved is not None and len(retrieved) > 0:
            print(f"✅ Veri okuma başarılı: {len(retrieved)} kayıt")
        else:
            print("❌ Veri okuma başarısız")
            return False

        print("\n✅ Veritabanı testleri başarılı")
        return True

    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_collection():
    """Veri toplama servisini test et"""
    print("\n" + "="*70)
    print("📡 TEST 3: Veri Toplama Test Ediliyor...")
    print("="*70)

    try:
        from collectors.market_data_collector import MarketDataCollector

        collector = MarketDataCollector()
        print("✅ MarketDataCollector oluşturuldu")

        # Test için küçük bir hisse
        print("\n📊 GARAN.IS için veri çekiliyor (son 5 gün)...")
        data = collector.collect_data("GARAN.IS", timeframe='1d', period='5d')

        if data is not None and len(data) > 0:
            print(f"✅ Veri çekme başarılı: {len(data)} bar")
            print(f"   Son fiyat: {data['Close'].iloc[-1]:.2f}")
            print(f"   Son hacim: {data['Volume'].iloc[-1]:,.0f}")
            return True
        else:
            print("❌ Veri çekme başarısız")
            return False

    except Exception as e:
        print(f"❌ Veri toplama hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_indicators():
    """İndikatör hesaplamasını test et"""
    print("\n" + "="*70)
    print("📈 TEST 4: İndikatör Hesaplama Test Ediliyor...")
    print("="*70)

    try:
        from indicators.technical_indicators import TechnicalIndicators
        from collectors.market_data_collector import MarketDataCollector

        # Önce veri çek
        collector = MarketDataCollector()
        data = collector.collect_data("GARAN.IS", timeframe='1d', period='1y')

        if data is None or len(data) < 200:
            print("❌ Yeterli veri yok")
            return False

        print(f"✅ Veri hazır: {len(data)} bar")

        # İndikatörleri hesapla
        indicators = TechnicalIndicators(data)
        result = indicators.calculate_all()

        if result and len(result) > 0:
            print(f"✅ İndikatör hesaplama başarılı: {len(result)} indikatör")

            # Bazı örnekler göster
            for ind_name in ['RSI_14', 'SMA_20', 'MACD']:
                if ind_name in result:
                    value = result[ind_name][-1]
                    if not pd.isna(value):
                        print(f"   {ind_name}: {value:.2f}")

            return True
        else:
            print("❌ İndikatör hesaplama başarısız")
            return False

    except Exception as e:
        print(f"❌ İndikatör hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_generation():
    """Sinyal üretimini test et"""
    print("\n" + "="*70)
    print("🎯 TEST 5: Sinyal Üretimi Test Ediliyor...")
    print("="*70)

    try:
        from strategies.signal_generator import SignalGenerator
        from collectors.market_data_collector import MarketDataCollector
        from indicators.technical_indicators import TechnicalIndicators
        from database.db_manager import DatabaseManager

        # Veritabanına veri ve indikatör ekle
        db = DatabaseManager()
        collector = MarketDataCollector()

        ticker = "GARAN.IS"
        timeframe = "1d"

        print(f"\n📊 {ticker} için veri çekiliyor...")
        data = collector.collect_data(ticker, timeframe=timeframe, period='1y')

        if data is None or len(data) < 200:
            print("❌ Yeterli veri yok")
            return False

        # Veritabanına kaydet
        db.add_ohlcv_data(ticker, timeframe, data)
        print(f"✅ Veri kaydedildi: {len(data)} bar")

        # İndikatörleri hesapla ve kaydet
        indicators = TechnicalIndicators(data)
        indicators_dict = indicators.calculate_all()

        if indicators_dict:
            count = db.add_indicator_values_bulk(ticker, timeframe, indicators_dict, data.index)
            print(f"✅ İndikatörler kaydedildi: {count} kayıt")

        # Sinyal üret
        signal_gen = SignalGenerator()
        signal = signal_gen.generate_combined_signal(ticker, timeframe)

        if signal:
            print(f"\n✅ Sinyal üretildi:")
            print(f"   Sinyal: {signal['signal']}")
            print(f"   Skor: {signal['score']:.1f}")
            print(f"   Trend: {signal['details']['trend']['signal']}")
            print(f"   Momentum: {signal['details']['momentum']['signal']}")
            print(f"   Volatilite: {signal['details']['volatility']['signal']}")
            return True
        else:
            print("❌ Sinyal üretilemedi")
            return False

    except Exception as e:
        print(f"❌ Sinyal üretimi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_manager():
    """Risk yöneticisini test et"""
    print("\n" + "="*70)
    print("🛡️  TEST 6: Risk Yönetimi Test Ediliyor...")
    print("="*70)

    try:
        from live_trading.risk_manager import RiskManager

        # Risk manager oluştur
        rm = RiskManager(
            initial_capital=100000,
            max_position_size=0.10,
            max_positions=10
        )
        print("✅ RiskManager oluşturuldu")

        # Pozisyon açma testi
        can_open, reason = rm.can_open_position("GARAN.IS", signal_score=75)
        print(f"✅ Pozisyon kontrolü: {can_open} - {reason}")

        # Pozisyon büyüklüğü hesaplama
        quantity, value = rm.calculate_position_size(price=100, signal_score=75)
        print(f"✅ Pozisyon büyüklüğü: {quantity} adet, {value:.2f} TL")

        # Pozisyon aç
        position = rm.open_position(
            ticker="GARAN.IS",
            timeframe="1d",
            side="BUY",
            price=100,
            signal_score=75
        )

        if position:
            print(f"✅ Pozisyon açıldı: {position.ticker} {position.side} {position.quantity} @ {position.entry_price}")

        # İstatistikler
        stats = rm.get_stats()
        print(f"\n📊 Portföy İstatistikleri:")
        print(f"   Toplam Sermaye: {stats['total_capital']:,.2f} TL")
        print(f"   Nakit: {stats['current_capital']:,.2f} TL")
        print(f"   Pozisyonlar: {stats['positions_count']}")

        return True

    except Exception as e:
        print(f"❌ Risk yönetimi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_live_engine():
    """Live trading engine'i test et (başlatma - hemen durdurma)"""
    print("\n" + "="*70)
    print("🤖 TEST 7: Live Trading Engine Test Ediliyor...")
    print("="*70)

    try:
        from live_trading.live_engine import LiveTradingEngine

        print("✅ LiveTradingEngine import edildi")

        # Engine oluştur (ama başlatma)
        engine = LiveTradingEngine(
            mode='paper',
            initial_capital=100000,
            active_timeframes=['1d'],
            update_interval=60,
            max_stocks=1
        )

        print("✅ LiveTradingEngine oluşturuldu")
        print(f"   Mod: {engine.mode}")
        print(f"   Hisse Sayısı: {len(engine.active_stocks)}")
        print(f"   Timeframe'ler: {', '.join(engine.active_timeframes)}")

        # NOT: Gerçek çalıştırma yapmıyoruz, sadece oluşturulabilir mi kontrol ediyoruz

        return True

    except Exception as e:
        print(f"❌ Live engine hatası: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ana test fonksiyonu"""
    print("\n" + "="*80)
    print("🔍 SİSTEM TEST PAKETİ - UÇTAN UCA TEST")
    print("="*80)
    print("\nTüm sistem bileşenleri test edilecek...\n")

    results = []

    # Test 1: Import'lar
    results.append(("Import'lar", test_imports()))

    # Test 2: Veritabanı
    results.append(("Veritabanı", test_database()))

    # Test 3: Veri Toplama
    results.append(("Veri Toplama", test_data_collection()))

    # Test 4: İndikatörler
    results.append(("İndikatörler", test_indicators()))

    # Test 5: Sinyal Üretimi
    results.append(("Sinyal Üretimi", test_signal_generation()))

    # Test 6: Risk Yönetimi
    results.append(("Risk Yönetimi", test_risk_manager()))

    # Test 7: Live Engine
    results.append(("Live Trading Engine", test_live_engine()))

    # Sonuçları göster
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI")
    print("="*80)

    for test_name, passed in results:
        emoji = "✅" if passed else "❌"
        print(f"{emoji} {test_name:30s} - {'BAŞARILI' if passed else 'BAŞARISIZ'}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print("\n" + "="*80)
    print(f"📈 TOPLAM: {passed}/{total} test geçti ({(passed/total)*100:.1f}%)")
    print("="*80)

    if passed == total:
        print("\n🎉 TÜM TESTLER BAŞARILI! Sistem çalışmaya hazır!")
        print("\n💡 Sistemi başlatmak için:")
        print("   python run_live_trading.py --mode paper --max-stocks 5")
    else:
        print("\n⚠️  BAZI TESTLER BAŞARISIZ! Lütfen hataları düzeltin.")
        print("\n📖 Yardım için:")
        print("   - WINDOWS_TALIB_INSTALL.md (TA-Lib kurulumu)")
        print("   - WINDOWS_QUICK_START.md (Windows kurulum rehberi)")
        print("   - live_trading/README.md (Genel dokümantasyon)")

    print()

    return passed == total


if __name__ == '__main__':
    import pandas as pd

    # Pandas uyarılarını kapat
    import warnings
    warnings.filterwarnings('ignore')

    success = main()
    sys.exit(0 if success else 1)
