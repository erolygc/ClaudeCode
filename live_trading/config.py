"""
Live Trading Configuration - Tüm ayarlar burada
"""

# ============================================================================
# TRADING MODU
# ============================================================================
TRADING_MODE = 'paper'  # 'paper' (test) veya 'live' (gerçek işlem)

# ============================================================================
# SERMAYE YÖNETİMİ
# ============================================================================
INITIAL_CAPITAL = 100000  # Başlangıç sermayesi (TL)

# ============================================================================
# RİSK YÖNETİMİ
# ============================================================================
RISK_SETTINGS = {
    'max_position_size': 0.10,        # Pozisyon büyüklüğü (sermayenin %10'u)
    'max_positions': 10,              # Maksimum eş zamanlı pozisyon sayısı
    'stop_loss_percent': 0.05,        # Stop loss (%5)
    'take_profit_percent': 0.15,      # Take profit (%15)
    'max_daily_loss_percent': 0.03,   # Günlük maksimum kayıp (%3)
    'min_signal_score': 60,           # Minimum sinyal skoru
}

# ============================================================================
# İŞLEM AYARLARI
# ============================================================================
TRADING_SETTINGS = {
    'active_timeframes': ['1d'],      # Aktif timeframe'ler
    'update_interval': 300,           # Güncelleme aralığı (saniye) - 5 dakika
    'max_stocks': 30,                 # Maksimum hisse sayısı (None = hepsi)
    'trading_hours_only': True,       # Sadece piyasa saatlerinde işlem yap
    'market_open': '10:00',           # Piyasa açılış saati
    'market_close': '18:00',          # Piyasa kapanış saati
}

# ============================================================================
# BİLDİRİMLER
# ============================================================================
NOTIFICATION_SETTINGS = {
    'enabled': True,
    'email_enabled': False,           # E-posta bildirimi
    'email_recipients': [],           # E-posta adresleri
    'telegram_enabled': False,        # Telegram bildirimi
    'telegram_token': '',             # Telegram bot token
    'telegram_chat_id': '',           # Telegram chat ID
    'notify_on_signal': True,         # Sinyal gelince bildir
    'notify_on_trade': True,          # İşlem yapılınca bildir
    'notify_on_position_close': True, # Pozisyon kapanınca bildir
    'min_signal_score_to_notify': 70, # Bildirim için minimum skor
}

# ============================================================================
# LOGLAMA
# ============================================================================
LOG_SETTINGS = {
    'log_level': 'INFO',              # DEBUG, INFO, WARNING, ERROR
    'log_to_file': True,              # Dosyaya log yaz
    'log_to_console': True,           # Console'a log yaz
    'log_directory': 'logs',          # Log klasörü
    'max_log_size_mb': 100,           # Maksimum log dosya boyutu (MB)
    'keep_logs_days': 30,             # Logları kaç gün sakla
}

# ============================================================================
# VERİTABANI
# ============================================================================
DATABASE_SETTINGS = {
    'path': 'trading_data.db',        # Veritabanı dosyası
    'backup_enabled': True,           # Otomatik yedekleme
    'backup_interval_hours': 24,      # Yedekleme aralığı (saat)
    'backup_directory': 'backups',    # Yedek klasörü
    'keep_backups_days': 7,           # Yedekleri kaç gün sakla
}

# ============================================================================
# PERFORMANS
# ============================================================================
PERFORMANCE_SETTINGS = {
    'enable_caching': True,           # Önbellekleme aktif
    'cache_ttl_seconds': 300,         # Önbellek süresi (saniye)
    'parallel_processing': False,     # Paralel işlem (çoklu hisse için)
    'max_workers': 4,                 # Maksimum worker sayısı
}

# ============================================================================
# GÜVENLİK
# ============================================================================
SECURITY_SETTINGS = {
    'require_confirmation': True,     # İşlem onayı gerekli mi?
    'max_loss_shutdown': 0.10,        # Maksimum kayıp (%10) - otomatik durdur
    'emergency_stop': True,           # Acil durdurma aktif
    'daily_loss_limit': 5000,         # Günlük kayıp limiti (TL)
}

# ============================================================================
# BROKER AYARLARI (Gelecekte eklenecek)
# ============================================================================
BROKER_SETTINGS = {
    'name': 'none',                   # Broker adı (ileride: 'enpara', 'isyatirim', vb.)
    'api_key': '',                    # API anahtarı
    'api_secret': '',                 # API secret
    'account_id': '',                 # Hesap ID
    'test_mode': True,                # Test modu (paper trading)
}
