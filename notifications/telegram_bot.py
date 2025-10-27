"""
Telegram Bot - Live Trading Bildirimleri
"""
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict
import requests


class TelegramNotifier:
    """Telegram üzerinden bildirim gönderen sınıf"""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Args:
            bot_token: Telegram bot token (BotFather'dan alınır)
            chat_id: Telegram chat ID (kullanıcı/grup ID)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)

        if not self.enabled:
            print("⚠️  Telegram bildirimleri devre dışı (token/chat_id eksik)")
        else:
            print(f"✅ Telegram bildirimleri aktif (Chat ID: {self.chat_id})")

    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        Telegram mesajı gönder

        Args:
            message: Gönderilecek mesaj
            parse_mode: 'Markdown' veya 'HTML'

        Returns:
            bool: Başarılı ise True
        """
        if not self.enabled:
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }

            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"❌ Telegram mesaj gönderme hatası: {e}")
            return False

    def notify_signal(self, ticker: str, timeframe: str, signal: str, score: float, price: float) -> bool:
        """Sinyal bildirimi"""
        emoji = "🟢" if signal == 'BUY' else ("🔴" if signal == 'SELL' else "⚪")

        message = f"""
{emoji} *{signal} SİNYALİ*

📊 *Hisse:* {ticker}
⏰ *Timeframe:* {timeframe}
📈 *Skor:* {score:.1f}/100
💰 *Fiyat:* {price:.2f} TL

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_position_opened(self, ticker: str, side: str, quantity: int,
                              price: float, stop_loss: float, take_profit: float) -> bool:
        """Pozisyon açılışı bildirimi"""
        emoji = "🟢" if side == 'BUY' else "🔴"

        message = f"""
{emoji} *POZİSYON AÇILDI*

📊 *Hisse:* {ticker}
📌 *Yön:* {side}
📦 *Adet:* {quantity}
💰 *Fiyat:* {price:.2f} TL
💵 *Tutar:* {quantity * price:,.2f} TL

🛑 *Stop Loss:* {stop_loss:.2f} TL ({((stop_loss/price - 1) * 100):+.1f}%)
🎯 *Take Profit:* {take_profit:.2f} TL ({((take_profit/price - 1) * 100):+.1f}%)

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_position_closed(self, ticker: str, side: str, entry_price: float,
                              exit_price: float, pnl: float, pnl_percent: float,
                              reason: str) -> bool:
        """Pozisyon kapanışı bildirimi"""
        emoji = "🟢" if pnl > 0 else "🔴"

        message = f"""
{emoji} *POZİSYON KAPANDI*

📊 *Hisse:* {ticker}
📌 *Yön:* {side}
📍 *Neden:* {reason}

💰 *Giriş:* {entry_price:.2f} TL
💰 *Çıkış:* {exit_price:.2f} TL

{'📈' if pnl > 0 else '📉'} *Kar/Zarar:* {pnl:+,.2f} TL ({pnl_percent:+.2f}%)

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_daily_summary(self, stats: Dict) -> bool:
        """Günlük özet bildirimi"""
        emoji = "🟢" if stats['daily_pnl'] > 0 else ("🔴" if stats['daily_pnl'] < 0 else "⚪")

        message = f"""
{emoji} *GÜNLÜK ÖZET*

💰 *Toplam Sermaye:* {stats['total_capital']:,.2f} TL
💵 *Nakit:* {stats['current_capital']:,.2f} TL
📊 *Pozisyon Değeri:* {stats['positions_value']:,.2f} TL
📦 *Açık Pozisyon:* {stats['positions_count']}/{stats.get('max_positions', 10)}

{'📈' if stats['daily_pnl'] > 0 else '📉'} *Günlük PnL:* {stats['daily_pnl']:+,.2f} TL
💼 *Toplam PnL:* {stats['total_pnl']:+,.2f} TL
📊 *Getiri:* {stats['return_percent']:+.2f}%

🔢 *Günlük İşlem:* {stats['daily_trades']}
🔢 *Toplam İşlem:* {stats['total_trades']}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_error(self, error_message: str) -> bool:
        """Hata bildirimi"""
        message = f"""
⚠️ *SISTEM HATASI*

❌ {error_message}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_system_start(self, mode: str, capital: float, stocks_count: int) -> bool:
        """Sistem başlatma bildirimi"""
        message = f"""
🚀 *SİSTEM BAŞLATILDI*

⚙️ *Mod:* {mode.upper()}
💰 *Sermaye:* {capital:,.2f} TL
📊 *Hisse Sayısı:* {stocks_count}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_system_stop(self, stats: Dict) -> bool:
        """Sistem durdurma bildirimi"""
        emoji = "🟢" if stats['total_pnl'] > 0 else ("🔴" if stats['total_pnl'] < 0 else "⚪")

        message = f"""
🛑 *SİSTEM DURDURULDU*

💰 *Final Sermaye:* {stats['total_capital']:,.2f} TL
{'📈' if stats['total_pnl'] > 0 else '📉'} *Toplam PnL:* {stats['total_pnl']:+,.2f} TL
📊 *Getiri:* {stats['return_percent']:+.2f}%
🔢 *Toplam İşlem:* {stats['total_trades']}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

    def notify_trailing_stop_update(self, ticker: str, old_sl: float, new_sl: float,
                                   current_price: float) -> bool:
        """Trailing stop güncelleme bildirimi"""
        message = f"""
📈 *TRAILING STOP GÜNCELLENDİ*

📊 *Hisse:* {ticker}
💰 *Fiyat:* {current_price:.2f} TL

🛑 *Eski SL:* {old_sl:.2f} TL
🛑 *Yeni SL:* {new_sl:.2f} TL

📊 *Artış:* {((new_sl/old_sl - 1) * 100):+.2f}%

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)


def setup_telegram_bot():
    """
    Telegram Bot Kurulum Rehberi

    1. Telegram'da BotFather'ı bulun: @BotFather
    2. /newbot komutunu kullanın
    3. Bot adı ve username verin
    4. Bot token'ı alın

    5. Chat ID almak için:
       - https://api.telegram.org/bot<TOKEN>/getUpdates
       - Bota bir mesaj gönderin
       - "chat":{"id": <CHAT_ID>} değerini bulun

    6. Environment variables:
       export TELEGRAM_BOT_TOKEN="your_bot_token"
       export TELEGRAM_CHAT_ID="your_chat_id"

    Windows için:
       set TELEGRAM_BOT_TOKEN=your_bot_token
       set TELEGRAM_CHAT_ID=your_chat_id

    Veya .env dosyası:
       TELEGRAM_BOT_TOKEN=your_bot_token
       TELEGRAM_CHAT_ID=your_chat_id
    """
    print(__doc__)


if __name__ == '__main__':
    # Test
    notifier = TelegramNotifier()

    if notifier.enabled:
        print("✅ Telegram bot test ediliyor...")

        # Test mesajı
        success = notifier.send_message("🤖 Test mesajı - Sistem çalışıyor!")

        if success:
            print("✅ Test mesajı gönderildi!")
        else:
            print("❌ Test mesajı gönderilemedi")
    else:
        print("\n📖 Telegram Bot Kurulum Rehberi:")
        setup_telegram_bot()
