"""
Risk Yönetimi - Pozisyon büyüklüğü, stop loss, take profit
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    """Açık pozisyon bilgisi"""
    ticker: str
    timeframe: str
    side: str  # 'BUY' veya 'SELL'
    entry_price: float
    quantity: int
    entry_time: datetime
    stop_loss: float
    take_profit: float
    current_price: float = 0.0
    trailing_stop_enabled: bool = True
    trailing_stop_percent: float = 0.05  # %5 trailing stop
    highest_price: float = 0.0  # En yüksek fiyat (BUY için)
    lowest_price: float = float('inf')  # En düşük fiyat (SELL için)

    def __post_init__(self):
        """Initialize highest/lowest price with entry price"""
        if self.highest_price == 0.0:
            self.highest_price = self.entry_price
        if self.lowest_price == float('inf'):
            self.lowest_price = self.entry_price
        if self.current_price == 0.0:
            self.current_price = self.entry_price

    @property
    def current_value(self) -> float:
        """Pozisyonun şu anki değeri"""
        return self.current_price * self.quantity

    @property
    def pnl(self) -> float:
        """Kar/Zarar"""
        if self.side == 'BUY':
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity

    @property
    def pnl_percent(self) -> float:
        """Kar/Zarar yüzdesi"""
        if self.side == 'BUY':
            return ((self.current_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.current_price) / self.entry_price) * 100

    def update_trailing_stop(self) -> tuple[bool, float]:
        """
        Trailing stop loss'u güncelle

        Returns:
            tuple: (güncellendi_mi, yeni_stop_loss)
        """
        if not self.trailing_stop_enabled:
            return False, self.stop_loss

        old_stop_loss = self.stop_loss
        updated = False

        if self.side == 'BUY':
            # En yüksek fiyatı güncelle
            if self.current_price > self.highest_price:
                self.highest_price = self.current_price

            # Yeni stop loss hesapla (en yüksek fiyattan %5 aşağı)
            new_stop_loss = self.highest_price * (1 - self.trailing_stop_percent)

            # Stop loss'u sadece yukarı çek (asla aşağı indirme)
            if new_stop_loss > self.stop_loss:
                self.stop_loss = new_stop_loss
                updated = True

        else:  # SELL
            # En düşük fiyatı güncelle
            if self.current_price < self.lowest_price:
                self.lowest_price = self.current_price

            # Yeni stop loss hesapla (en düşük fiyattan %5 yukarı)
            new_stop_loss = self.lowest_price * (1 + self.trailing_stop_percent)

            # Stop loss'u sadece aşağı çek
            if new_stop_loss < self.stop_loss:
                self.stop_loss = new_stop_loss
                updated = True

        return updated, self.stop_loss

    def should_close(self, current_signal: str = None, signal_score: float = 0) -> tuple[bool, str]:
        """
        Pozisyon kapatılmalı mı?

        Args:
            current_signal: Güncel sinyal (BUY/SELL/HOLD)
            signal_score: Sinyal skoru (0-100)

        Returns:
            tuple: (kapatılmalı_mı, sebep)
        """
        # 1. SİNYAL BAZLI KAPATMA (ÖNCELİKLİ)
        if current_signal and signal_score >= 60:
            if self.side == 'BUY' and current_signal == 'SELL':
                return True, 'SIGNAL_SELL'
            elif self.side == 'SELL' and current_signal == 'BUY':
                return True, 'SIGNAL_BUY'

        # 2. FİYAT BAZLI KAPATMA (GÜVENLİK)
        if self.side == 'BUY':
            if self.current_price <= self.stop_loss:
                return True, 'STOP_LOSS'
            if self.current_price >= self.take_profit:
                return True, 'TAKE_PROFIT'
        else:
            if self.current_price >= self.stop_loss:
                return True, 'STOP_LOSS'
            if self.current_price <= self.take_profit:
                return True, 'TAKE_PROFIT'

        return False, ''


class RiskManager:
    """
    Risk Yönetimi Sistemi
    - Pozisyon büyüklüğü hesaplama
    - Stop loss / Take profit belirleme
    - Maksimum pozisyon kontrolü
    - Sermaye koruma
    """

    def __init__(self,
                 initial_capital: float = 100000,
                 max_position_size: float = 0.10,  # Sermayenin maksimum %10'u
                 max_positions: int = 10,
                 stop_loss_percent: float = 0.05,  # %5 stop loss (BIST için uygun)
                 take_profit_percent: float = 0.08,  # %8 take profit (BIST max %10 limit)
                 max_daily_loss_percent: float = 0.03,  # Günlük maksimum %3 kayıp
                 min_signal_score: float = 60,
                 trailing_stop_percent: float = 0.03):  # %3 trailing (BIST için uygun)

        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = max_position_size
        self.max_positions = max_positions
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.max_daily_loss_percent = max_daily_loss_percent
        self.min_signal_score = min_signal_score
        self.trailing_stop_percent = trailing_stop_percent

        # Açık pozisyonlar
        self.positions: Dict[str, Position] = {}

        # Günlük istatistikler
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.daily_trades = 0
        self.total_trades = 0

    def can_open_position(self, ticker: str, signal_score: float) -> tuple[bool, str]:
        """Yeni pozisyon açılabilir mi?"""

        # Sinyal skoru yetersiz mi?
        if signal_score < self.min_signal_score:
            return False, f'Sinyal skoru yetersiz: {signal_score:.1f} < {self.min_signal_score}'

        # Maksimum pozisyon sayısına ulaşıldı mı?
        if len(self.positions) >= self.max_positions:
            return False, f'Maksimum pozisyon sayısına ulaşıldı: {len(self.positions)}/{self.max_positions}'

        # Bu hisse için zaten pozisyon var mı?
        if ticker in self.positions:
            return False, f'{ticker} için zaten açık pozisyon var'

        # Günlük maksimum kayıp aşıldı mı?
        if self.daily_pnl < -(self.initial_capital * self.max_daily_loss_percent):
            return False, f'Günlük maksimum kayıp aşıldı: {self.daily_pnl:.2f} TL'

        # Sermaye yeterli mi?
        required_capital = self.current_capital * self.max_position_size
        available_capital = self.get_available_capital()

        if available_capital < required_capital:
            return False, f'Yetersiz sermaye: {available_capital:.2f} < {required_capital:.2f} TL'

        return True, 'OK'

    def calculate_position_size(self, price: float, signal_score: float) -> tuple[int, float]:
        """
        Pozisyon büyüklüğünü hesapla

        Returns:
            tuple: (adet, tutar)
        """
        # Sinyal skoruna göre pozisyon büyüklüğünü ayarla
        # Yüksek skor = daha büyük pozisyon
        score_multiplier = min(signal_score / 100, 1.0)

        # Maksimum pozisyon tutarı
        max_position_value = self.current_capital * self.max_position_size * score_multiplier

        # Adet hesapla
        quantity = int(max_position_value / price)

        # En az 1 adet
        quantity = max(1, quantity)

        # Gerçek tutar
        actual_value = quantity * price

        return quantity, actual_value

    def calculate_stop_loss_take_profit(self, entry_price: float, side: str) -> tuple[float, float]:
        """Stop loss ve take profit seviyelerini hesapla"""

        if side == 'BUY':
            stop_loss = entry_price * (1 - self.stop_loss_percent)
            take_profit = entry_price * (1 + self.take_profit_percent)
        else:  # SELL
            stop_loss = entry_price * (1 + self.stop_loss_percent)
            take_profit = entry_price * (1 - self.take_profit_percent)

        return stop_loss, take_profit

    def open_position(self,
                     ticker: str,
                     timeframe: str,
                     side: str,
                     price: float,
                     signal_score: float) -> Optional[Position]:
        """Yeni pozisyon aç"""

        # Pozisyon açılabilir mi kontrol et
        can_open, reason = self.can_open_position(ticker, signal_score)
        if not can_open:
            print(f"❌ Pozisyon açılamadı: {reason}")
            return None

        # Pozisyon büyüklüğünü hesapla
        quantity, value = self.calculate_position_size(price, signal_score)

        # Stop loss ve take profit hesapla
        stop_loss, take_profit = self.calculate_stop_loss_take_profit(price, side)

        # Pozisyon oluştur
        position = Position(
            ticker=ticker,
            timeframe=timeframe,
            side=side,
            entry_price=price,
            quantity=quantity,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            current_price=price,
            trailing_stop_percent=self.trailing_stop_percent  # BIST için %3
        )

        # Pozisyonu kaydet
        self.positions[ticker] = position

        # Sermayeden düş
        self.current_capital -= value

        # İstatistik
        self.daily_trades += 1
        self.total_trades += 1

        print(f"✅ Pozisyon açıldı: {ticker} {side} {quantity} @ {price:.2f} TL")
        print(f"   SL: {stop_loss:.2f} | TP: {take_profit:.2f} | Tutar: {value:.2f} TL")

        return position

    def close_position(self, ticker: str, current_price: float, reason: str = 'MANUAL') -> Optional[float]:
        """Pozisyonu kapat"""

        if ticker not in self.positions:
            print(f"❌ {ticker} için açık pozisyon yok")
            return None

        position = self.positions[ticker]
        position.current_price = current_price

        # PnL hesapla
        pnl = position.pnl
        pnl_percent = position.pnl_percent

        # Sermayeye ekle
        closing_value = position.current_value
        self.current_capital += closing_value

        # PnL güncelle
        self.daily_pnl += pnl
        self.total_pnl += pnl

        # Pozisyonu sil
        del self.positions[ticker]

        emoji = "🟢" if pnl > 0 else "🔴"
        print(f"{emoji} Pozisyon kapandı: {ticker} @ {current_price:.2f} TL ({reason})")
        print(f"   PnL: {pnl:+.2f} TL ({pnl_percent:+.2f}%) | Kapanış Tutarı: {closing_value:.2f} TL")

        return pnl

    def update_positions(self, prices: Dict[str, float], signals: Dict[str, tuple] = None, notify_callback=None):
        """
        Tüm pozisyonları güncelle ve gerekirse kapat

        Args:
            prices: Hisse fiyatları dict'i
            signals: Güncel sinyaller dict'i {ticker: (signal, score)}
            notify_callback: Trailing stop güncellemesi için callback fonksiyonu
        """

        positions_to_close = []

        for ticker, position in self.positions.items():
            if ticker in prices:
                old_stop_loss = position.stop_loss

                # Fiyatı güncelle
                position.current_price = prices[ticker]

                # Trailing stop'u güncelle
                updated, new_stop_loss = position.update_trailing_stop()

                if updated:
                    print(f"📈 {ticker} Trailing Stop güncellendi: {old_stop_loss:.2f} → {new_stop_loss:.2f} TL")

                    # Callback varsa bildir
                    if notify_callback:
                        notify_callback(ticker, old_stop_loss, new_stop_loss, position.current_price)

                # Sinyal bilgisini al
                current_signal = None
                signal_score = 0
                if signals and ticker in signals:
                    current_signal, signal_score = signals[ticker]

                # Kapatılmalı mı kontrol et (SİNYAL DAHİL)
                should_close, reason = position.should_close(current_signal, signal_score)
                if should_close:
                    positions_to_close.append((ticker, reason))

        # Pozisyonları kapat
        for ticker, reason in positions_to_close:
            self.close_position(ticker, prices[ticker], reason)

    def get_available_capital(self) -> float:
        """Kullanılabilir sermaye"""
        return self.current_capital

    def get_total_capital(self) -> float:
        """Toplam sermaye (nakit + pozisyonlar)"""
        positions_value = sum(p.current_value for p in self.positions.values())
        return self.current_capital + positions_value

    def get_stats(self) -> Dict:
        """İstatistikleri getir"""
        total_capital = self.get_total_capital()

        return {
            'current_capital': self.current_capital,
            'total_capital': total_capital,
            'positions_count': len(self.positions),
            'positions_value': sum(p.current_value for p in self.positions.values()),
            'daily_pnl': self.daily_pnl,
            'total_pnl': self.total_pnl,
            'daily_trades': self.daily_trades,
            'total_trades': self.total_trades,
            'return_percent': ((total_capital - self.initial_capital) / self.initial_capital) * 100
        }

    def reset_daily_stats(self):
        """Günlük istatistikleri sıfırla"""
        self.daily_pnl = 0.0
        self.daily_trades = 0

    def print_summary(self):
        """Özet rapor yazdır"""
        stats = self.get_stats()

        print("\n" + "="*70)
        print("📊 PORTFÖY ÖZETİ")
        print("="*70)
        print(f"Toplam Sermaye    : {stats['total_capital']:,.2f} TL")
        print(f"Nakit             : {stats['current_capital']:,.2f} TL")
        print(f"Pozisyon Değeri   : {stats['positions_value']:,.2f} TL")
        print(f"Açık Pozisyonlar  : {stats['positions_count']}/{self.max_positions}")
        print(f"-" * 70)
        print(f"Günlük PnL        : {stats['daily_pnl']:+,.2f} TL ({stats['daily_trades']} işlem)")
        print(f"Toplam PnL        : {stats['total_pnl']:+,.2f} TL ({stats['total_trades']} işlem)")
        print(f"Toplam Getiri     : {stats['return_percent']:+.2f}%")
        print("="*70)

        # Açık pozisyonları listele
        if self.positions:
            print("\n📋 AÇIK POZİSYONLAR:")
            print("-" * 70)
            for ticker, pos in self.positions.items():
                emoji = "🟢" if pos.pnl > 0 else "🔴"
                print(f"{emoji} {ticker:12s} | {pos.side:4s} | {pos.quantity:6d} @ {pos.entry_price:8.2f}")
                print(f"   Fiyat: {pos.current_price:8.2f} | PnL: {pos.pnl:+10.2f} TL ({pos.pnl_percent:+6.2f}%)")
                print(f"   SL: {pos.stop_loss:8.2f} | TP: {pos.take_profit:8.2f}")
                print("-" * 70)
        else:
            print("\n✨ Açık pozisyon yok")

        print()
