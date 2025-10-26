#!/usr/bin/env python3
"""
Live Trading Monitor - Sistem durumunu izle
"""
import sys
import os

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from live_trading.monitor import LiveTradingMonitor


def main():
    """Monitor'u başlat"""

    import argparse

    parser = argparse.ArgumentParser(
        description='📊 Live Trading Monitor - Sistem durumunu izle',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  # Canlı dashboard (her 60 saniyede güncellenir)
  python run_monitor.py --dashboard

  # Dashboard - daha hızlı güncelleme (30 saniye)
  python run_monitor.py --dashboard --refresh 30

  # Rapor export et
  python run_monitor.py --export

  # Son 48 saatin raporunu export et
  python run_monitor.py --export --hours 48

  # Basit özet göster
  python run_monitor.py --hours 24
        """
    )

    parser.add_argument('--dashboard', action='store_true',
                       help='Canlı dashboard göster')

    parser.add_argument('--export', action='store_true',
                       help='Rapor export et')

    parser.add_argument('--hours', type=int, default=24,
                       help='Kaç saatlik veri gösterilsin (varsayılan: 24)')

    parser.add_argument('--refresh', type=int, default=60,
                       help='Dashboard yenileme aralığı (saniye) (varsayılan: 60)')

    args = parser.parse_args()

    monitor = LiveTradingMonitor()

    if args.dashboard:
        print("\n🚀 Live Trading Dashboard başlatılıyor...")
        print(f"   Yenileme: Her {args.refresh} saniye")
        print(f"   Veri aralığı: Son {args.hours} saat")
        print(f"   Çıkış: Ctrl+C\n")
        monitor.print_dashboard(refresh_interval=args.refresh)

    elif args.export:
        print(f"\n📄 Rapor export ediliyor (son {args.hours} saat)...")
        filename = monitor.export_report(hours=args.hours)
        print(f"✅ Rapor kaydedildi: {filename}\n")

    else:
        # Basit özet
        monitor.print_dashboard.__wrapped__ = monitor.print_dashboard
        # Tek seferlik özet göster
        import argparse
        from live_trading.monitor import main as monitor_main
        sys.argv = ['monitor.py', '--hours', str(args.hours)]
        monitor_main()


if __name__ == '__main__':
    main()
