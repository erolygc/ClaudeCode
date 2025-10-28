"""
Live Trading Engine - Canlı işlem yapan ana motor
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

from database.db_manager import DatabaseManager
from collectors.market_data_collector import MarketDataCollector
from indicators.technical_indicators import TechnicalIndicators
from strategies.signal_generator import SignalGenerator
from live_trading.risk_manager import RiskManager
from config.settings import ACTIVE_STOCKS, TIMEFRAMES

# Telegram bot (opsiyonel)
try:
    from notifications.telegram_bot import TelegramNotifier
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class LiveTradingEngine:
    """
    Canlı Trading Motoru
    - Real-time veri toplama
    - İndikatör hesaplama
    - Sinyal üretimi
    - Otomatik işlem
    - Risk yönetimi
    """

    def __init__(self,
                 mode: str = 'paper',  # 'paper' veya 'live'
                 initial_capital: float = 100000,
                 active_timeframes: List[str] = None,
                 update_interval: int = 60,  # saniye
                 max_stocks: int = None):
        """
        Args:
            mode: 'paper' (kağıt üzerinde) veya 'live' (gerçek işlem)
            initial_capital: Başlangıç sermayesi
            active_timeframes: Aktif zaman dilimleri (None = hepsi)
            update_interval: Güncelleme aralığı (saniye)
            max_stocks: Maksimum hisse sayısı (None = hepsi)
        """
        self.mode = mode
        self.update_interval = update_interval

        # Bileşenler
        self.db = DatabaseManager()
        self.collector = MarketDataCollector()
        self.signal_gen = SignalGenerator()

        # RiskManager - BIST için optimize edilmiş parametreler
        self.risk_manager = RiskManager(
            initial_capital=initial_capital,
            stop_loss_percent=0.05,      # %5 stop loss
            take_profit_percent=0.08,    # %8 take profit (BIST %10 limit)
            trailing_stop_percent=0.03   # %3 trailing stop
        )

        # Telegram bot (opsiyonel)
        self.telegram = None
        if TELEGRAM_AVAILABLE:
            self.telegram = TelegramNotifier()

        # Aktif hisseler ve timeframe'ler
        self.active_stocks = ACTIVE_STOCKS[:max_stocks] if max_stocks else ACTIVE_STOCKS
        self.active_timeframes = active_timeframes or ['1d', '1h', '15m']

        # Durum
        self.is_running = False
        self.last_update = {}
        self.cycle_count = 0

        # Log dosyası
        self.log_file = f'live_trading_{mode}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

        print(f"\n{'='*70}")
        print(f"🤖 LIVE TRADING ENGINE - {mode.upper()} MODE")
        print(f"{'='*70}")
        print(f"Mod              : {mode.upper()}")
        print(f"Başlangıç Sermaye: {initial_capital:,.2f} TL")
        print(f"Hisse Sayısı     : {len(self.active_stocks)}")
        print(f"Timeframe'ler    : {', '.join(self.active_timeframes)}")
        print(f"Güncelleme Aralığı: {update_interval} saniye")
        print(f"Log Dosyası      : {self.log_file}")
        print(f"{'='*70}\n")

    def log(self, message: str):
        """Log mesajı yaz"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        # Dosyaya yaz
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def fetch_latest_data(self, ticker: str, timeframe: str) -> Optional[pd.DataFrame]:
        """En son veriyi çek"""
        try:
            # Timeframe'e göre period belirle (İndikatörler için yeterli veri: 200+ bar)
            if timeframe == '1m':
                period = '5d'       # 5 gün * 390 dakika = 1950 bar
            elif timeframe == '5m':
                period = '25d'      # 25 gün * 78 5-dakika = 1950 bar
            elif timeframe == '15m':
                period = '60d'      # 60 gün * 26 15-dakika = 1560 bar
            elif timeframe == '30m':
                period = '60d'      # 60 gün * 13 30-dakika = 780 bar
            elif timeframe == '1h':
                period = '90d'      # 90 gün * 6.5 saat = 585 bar
            elif timeframe == '4h':
                period = '2y'       # 2 yıl = ~500 4-saatlik bar
            elif timeframe == '1d':
                period = '2y'       # 2 yıl = ~500 günlük bar
            elif timeframe == '1w':
                period = '10y'      # 10 yıl = ~520 hafta
            else:
                period = '1y'       # Varsayılan 1 yıl

            # Veriyi çek
            data = self.collector.collect_data(
                ticker=ticker,
                timeframe=TIMEFRAMES[timeframe]['interval'],
                period=period
            )

            if data is not None and len(data) > 0:
                # Veritabanına kaydet
                self.db.add_ohlcv_data(ticker, timeframe, data)
                return data

            return None

        except Exception as e:
            self.log(f"❌ {ticker} ({timeframe}) veri çekme hatası: {e}")
            return None

    def calculate_indicators_for_ticker(self, ticker: str, timeframe: str) -> bool:
        """Bir hisse için indikatörleri hesapla"""
        try:
            # Veriyi getir
            data = self.db.get_ohlcv_data(ticker, timeframe)
            if data is None or len(data) < 200:
                return False

            # İndikatörleri hesapla (her seferinde yeni instance oluştur)
            indicators = TechnicalIndicators(data)
            indicators_dict = indicators.calculate_all()

            if indicators_dict:
                # Veritabanına kaydet (bulk insert)
                self.db.add_indicator_values_bulk(
                    ticker=ticker,
                    timeframe=timeframe,
                    indicators_dict=indicators_dict,
                    dates=data.index
                )
                return True

            return False

        except Exception as e:
            self.log(f"❌ {ticker} ({timeframe}) indikatör hatası: {e}")
            return False

    def generate_signals_for_ticker(self, ticker: str, timeframe: str) -> Optional[Dict]:
        """Bir hisse için sinyal üret"""
        try:
            signal_result = self.signal_gen.generate_combined_signal(ticker, timeframe)

            if signal_result:
                # Sinyali veritabanına kaydet
                self.db.add_signal(
                    ticker=ticker,
                    timeframe=timeframe,
                    signal=signal_result['signal'],
                    score=signal_result['score'],
                    details=json.dumps(signal_result['details'])
                )

                return signal_result

            return None

        except Exception as e:
            self.log(f"❌ {ticker} ({timeframe}) sinyal hatası: {e}")
            return None

    def execute_signal(self, ticker: str, timeframe: str, signal: Dict, current_price: float):
        """Sinyal üzerine işlem yap"""

        signal_type = signal['signal']
        signal_score = signal['score']

        # BUY sinyali
        if signal_type == 'BUY':
            # Pozisyon aç
            position = self.risk_manager.open_position(
                ticker=ticker,
                timeframe=timeframe,
                side='BUY',
                price=current_price,
                signal_score=signal_score
            )

            if position:
                self.log(f"✅ {ticker} BUY pozisyon açıldı @ {current_price:.2f} TL (Skor: {signal_score:.1f})")

        # SELL sinyali - mevcut pozisyonu kapat
        elif signal_type == 'SELL':
            if ticker in self.risk_manager.positions:
                pnl = self.risk_manager.close_position(ticker, current_price, 'SIGNAL')
                if pnl is not None:
                    self.log(f"✅ {ticker} pozisyon kapatıldı @ {current_price:.2f} TL (PnL: {pnl:+.2f} TL)")

    def update_cycle(self):
        """Bir güncelleme döngüsü çalıştır"""
        self.cycle_count += 1
        self.log(f"\n{'='*70}")
        self.log(f"🔄 DÖNGÜ #{self.cycle_count} BAŞLIYOR...")
        self.log(f"{'='*70}")

        cycle_start = time.time()
        signals_generated = []

        # Her timeframe için
        for timeframe in self.active_timeframes:
            self.log(f"\n📊 Timeframe: {timeframe}")
            self.log("-" * 70)

            # Her hisse için
            for ticker in self.active_stocks:
                try:
                    # 1. En son veriyi çek
                    data = self.fetch_latest_data(ticker, timeframe)
                    if data is None or len(data) < 200:
                        continue

                    # 2. İndikatörleri hesapla
                    if not self.calculate_indicators_for_ticker(ticker, timeframe):
                        continue

                    # 3. Sinyal üret
                    signal = self.generate_signals_for_ticker(ticker, timeframe)
                    if signal is None:
                        continue

                    # 4. Önemli sinyalleri kaydet
                    if signal['signal'] != 'HOLD' and signal['score'] >= 60:
                        current_price = data['Close'].iloc[-1]

                        signals_generated.append({
                            'ticker': ticker,
                            'timeframe': timeframe,
                            'signal': signal['signal'],
                            'score': signal['score'],
                            'price': current_price
                        })

                        # Sinyal bildir
                        emoji = "🟢" if signal['signal'] == 'BUY' else "🔴"
                        self.log(f"{emoji} {ticker:12s} | {signal['signal']:4s} | Skor: {signal['score']:5.1f} | Fiyat: {current_price:8.2f}")

                        # İşlem yap (sadece 1d timeframe için)
                        if timeframe == '1d' and self.mode != 'disabled':
                            self.execute_signal(ticker, timeframe, signal, current_price)

                except Exception as e:
                    self.log(f"❌ {ticker} işlem hatası: {e}")
                    continue

        # Pozisyonları güncelle
        if self.risk_manager.positions:
            self.log(f"\n📋 Pozisyonlar güncelleniyor...")
            prices = {}
            signals = {}

            for ticker in self.risk_manager.positions.keys():
                data = self.fetch_latest_data(ticker, '1d')
                if data is not None and len(data) > 0:
                    prices[ticker] = data['Close'].iloc[-1]

                    # Bu pozisyon için güncel sinyali al
                    try:
                        signal_result = self.generate_signals_for_ticker(ticker, '1d')
                        if signal_result:
                            signals[ticker] = (signal_result['signal'], signal_result['score'])
                    except:
                        pass  # Sinyal alınamazsa fiyat bazlı kapatmaya devam et

            if prices:
                self.risk_manager.update_positions(prices, signals)

        # Döngü özeti
        cycle_time = time.time() - cycle_start
        self.log(f"\n{'='*70}")
        self.log(f"✅ DÖNGÜ #{self.cycle_count} TAMAMLANDI")
        self.log(f"Süre: {cycle_time:.1f} saniye | Sinyal: {len(signals_generated)}")
        self.log(f"{'='*70}")

        # Portföy özeti
        self.risk_manager.print_summary()

        # Dashboard için JSON export
        self.export_to_dashboard()

        return signals_generated

    def export_to_dashboard(self):
        """Dashboard için JSON dosyaları oluştur"""
        try:
            # Portföy istatistiklerini al (RiskManager.get_stats() kullan)
            stats = self.risk_manager.get_stats()

            # Portföy verilerini hazırla
            portfolio_data = {
                'total_capital': stats['total_capital'],
                'cash': stats['current_capital'],
                'positions_value': stats['positions_value'],
                'positions_count': stats['positions_count'],
                'daily_pnl': stats['daily_pnl'],
                'total_pnl': stats['total_pnl'],
                'return_percent': stats['return_percent'],
                'last_update': datetime.now().isoformat()
            }

            # Pozisyon verilerini hazırla
            positions_data = []
            for ticker, pos in self.risk_manager.positions.items():
                positions_data.append({
                    'ticker': ticker,
                    'side': pos.side,
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': pos.current_price,
                    'pnl': pos.pnl,
                    'pnl_percent': pos.pnl_percent,
                    'stop_loss': pos.stop_loss,
                    'take_profit': pos.take_profit
                })

            # JSON dosyalarına yaz
            portfolio_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'live_portfolio.json')
            positions_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'live_positions.json')

            with open(portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(portfolio_data, f, indent=2, ensure_ascii=False)

            with open(positions_file, 'w', encoding='utf-8') as f:
                json.dump(positions_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.log(f"⚠️  Dashboard export hatası: {e}")

    def start(self):
        """Trading motorunu başlat"""
        self.is_running = True
        self.log(f"\n🚀 LIVE TRADING BAŞLATILDI - {self.mode.upper()} MODE")
        self.log(f"{'='*70}\n")

        try:
            while self.is_running:
                # Güncelleme döngüsü
                self.update_cycle()

                # Bekle
                self.log(f"\n⏳ {self.update_interval} saniye bekleniyor...")
                time.sleep(self.update_interval)

        except KeyboardInterrupt:
            self.log("\n\n⚠️  Kullanıcı tarafından durduruldu (Ctrl+C)")
            self.stop()

        except Exception as e:
            self.log(f"\n\n❌ HATA: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.stop()

    def stop(self):
        """Trading motorunu durdur"""
        self.is_running = False

        self.log(f"\n{'='*70}")
        self.log("🛑 LIVE TRADING DURDURULUYOR...")
        self.log(f"{'='*70}\n")

        # Tüm pozisyonları kapat
        if self.risk_manager.positions:
            self.log("📋 Açık pozisyonlar kapatılıyor...")

            for ticker in list(self.risk_manager.positions.keys()):
                # En son fiyatı al
                data = self.fetch_latest_data(ticker, '1d')
                if data is not None and len(data) > 0:
                    current_price = data['Close'].iloc[-1]
                    self.risk_manager.close_position(ticker, current_price, 'SHUTDOWN')

        # Final özet
        self.log("\n" + "="*70)
        self.log("📊 FİNAL RAPOR")
        self.log("="*70)
        self.risk_manager.print_summary()

        stats = self.risk_manager.get_stats()
        self.log(f"\nToplam Döngü: {self.cycle_count}")
        self.log(f"Toplam İşlem: {stats['total_trades']}")
        self.log(f"Final Sermaye: {stats['total_capital']:,.2f} TL")
        self.log(f"Getiri: {stats['return_percent']:+.2f}%")

        self.log(f"\n{'='*70}")
        self.log("✅ LIVE TRADING DURDURULDU")
        self.log(f"{'='*70}\n")


def main():
    """Ana fonksiyon"""
    import argparse

    parser = argparse.ArgumentParser(description='Live Trading Engine')
    parser.add_argument('--mode', type=str, default='paper',
                       choices=['paper', 'live'],
                       help='Trading mode (paper/live)')
    parser.add_argument('--capital', type=float, default=100000,
                       help='Initial capital (default: 100000 TL)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Update interval in seconds (default: 300)')
    parser.add_argument('--timeframes', type=str, default='1d',
                       help='Comma-separated timeframes (default: 1d)')
    parser.add_argument('--max-stocks', type=int, default=None,
                       help='Maximum number of stocks (default: all)')

    args = parser.parse_args()

    # Timeframe'leri parse et
    timeframes = [tf.strip() for tf in args.timeframes.split(',')]

    # Engine oluştur
    engine = LiveTradingEngine(
        mode=args.mode,
        initial_capital=args.capital,
        active_timeframes=timeframes,
        update_interval=args.interval,
        max_stocks=args.max_stocks
    )

    # Başlat
    engine.start()


if __name__ == '__main__':
    main()
