#!/usr/bin/env python3
"""
Live Trading Başlatıcı - Kolay kullanım için wrapper script
"""
import sys
import os

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from live_trading.live_engine import LiveTradingEngine


def main():
    """Live trading'i başlat"""

    import argparse

    parser = argparse.ArgumentParser(
        description='🤖 Live Trading System - Professional Automated Trading',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Paper trading (test modu) - 100,000 TL ile başla
  python run_live_trading.py --mode paper

  # Paper trading - 50,000 TL ile, sadece 30 hisse, 1 saatte bir güncelle
  python run_live_trading.py --mode paper --capital 50000 --max-stocks 30 --interval 3600

  # Paper trading - Sadece günlük ve saatlik timeframe'ler
  python run_live_trading.py --mode paper --timeframes 1d,1h

  # GERÇEK İŞLEM (DİKKAT!)
  python run_live_trading.py --mode live --capital 10000

  # Hızlı test - 5 hisse, 5 dakikada bir güncelle
  python run_live_trading.py --mode paper --max-stocks 5 --interval 300 --timeframes 1d
        """
    )

    parser.add_argument('--mode', type=str, default='paper',
                       choices=['paper', 'live'],
                       help='Trading modu: paper (test) veya live (gerçek işlem)')

    parser.add_argument('--capital', type=float, default=100000,
                       help='Başlangıç sermayesi (TL) (varsayılan: 100,000)')

    parser.add_argument('--interval', type=int, default=300,
                       help='Güncelleme aralığı (saniye) (varsayılan: 300 = 5 dakika)')

    parser.add_argument('--timeframes', type=str, default='1d',
                       help='Virgülle ayrılmış timeframe listesi (varsayılan: 1d)')

    parser.add_argument('--max-stocks', type=int, default=None,
                       help='Maksimum hisse sayısı (varsayılan: tümü)')

    # Risk yönetimi parametreleri
    parser.add_argument('--max-positions', type=int, default=10,
                       help='Maksimum eş zamanlı pozisyon (varsayılan: 10)')

    parser.add_argument('--position-size', type=float, default=0.10,
                       help='Pozisyon büyüklüğü (sermayenin yüzdesi) (varsayılan: 0.10 = %10)')

    parser.add_argument('--stop-loss', type=float, default=0.05,
                       help='Stop loss yüzdesi (varsayılan: 0.05 = %5)')

    parser.add_argument('--take-profit', type=float, default=0.15,
                       help='Take profit yüzdesi (varsayılan: 0.15 = %15)')

    args = parser.parse_args()

    # Uyarı mesajları
    print("\n" + "="*80)
    print("⚠️  ÖNEMLİ UYARILAR")
    print("="*80)

    if args.mode == 'live':
        print("🔴 GERÇEK İŞLEM MODU AKTIF!")
        print("   Bu mod gerçek para ile işlem yapacaktır!")
        print("   Kayıplardan sorumluluğu kabul ettiğinizden emin olun!")
        response = input("\n   Devam etmek istiyor musunuz? (EVET yazın): ")
        if response != "EVET":
            print("\n❌ İşlem iptal edildi")
            return
    else:
        print("📄 PAPER TRADING MODU AKTIF")
        print("   Bu mod sadece test amaçlıdır, gerçek işlem yapmaz.")
        print("   Gerçek para riski yoktur.")

    print("\n💡 İpuçları:")
    print("   - Ctrl+C ile durdurabilirsiniz")
    print("   - Log dosyası otomatik oluşturulacak")
    print("   - Tüm pozisyonlar kapatıldıktan sonra duracak")
    print("="*80 + "\n")

    # Timeframe'leri parse et
    timeframes = [tf.strip() for tf in args.timeframes.split(',')]

    # Engine oluştur
    from live_trading.risk_manager import RiskManager

    # Risk manager'ı custom parametrelerle oluştur
    risk_manager = RiskManager(
        initial_capital=args.capital,
        max_position_size=args.position_size,
        max_positions=args.max_positions,
        stop_loss_percent=args.stop_loss,
        take_profit_percent=args.take_profit
    )

    # Live engine oluştur
    engine = LiveTradingEngine(
        mode=args.mode,
        initial_capital=args.capital,
        active_timeframes=timeframes,
        update_interval=args.interval,
        max_stocks=args.max_stocks
    )

    # Custom risk manager'ı kullan
    engine.risk_manager = risk_manager

    # Başlat
    try:
        engine.start()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
