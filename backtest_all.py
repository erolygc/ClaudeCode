"""
Toplu Backtest - Tüm sinyalleri geriye dönük test eder
"""
from strategies.backtest_engine import BacktestEngine
from datetime import datetime

def main():
    print("="*80)
    print("🚀 BACKTEST SİSTEMİ - FAZ 9")
    print("="*80)
    print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Backtest engine'i başlat
    engine = BacktestEngine()

    # Tüm sinyalleri test et
    print("📊 Sinyaller test ediliyor...\n")
    results = engine.backtest_all_signals()

    # Performans raporu oluştur
    if results is not None:
        engine.generate_performance_report(results)

        # Excel'e kaydet
        try:
            excel_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            results.to_excel(excel_file, index=False)
            print(f"\n📄 Detaylı sonuçlar kaydedildi: {excel_file}")
        except Exception as e:
            print(f"\n⚠️  Excel kaydetme hatası: {e}")
            # CSV'ye kaydet
            csv_file = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results.to_csv(csv_file, index=False)
            print(f"📄 Detaylı sonuçlar CSV olarak kaydedildi: {csv_file}")

    print("\n✅ Backtest tamamlandı!")


if __name__ == "__main__":
    main()
