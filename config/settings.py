"""
Proje Ayarları - Tüm konfigürasyon burada
"""

# Test için 5 hisse (sonra tüm BIST30'a genişleyecek)
TEST_HISSELER = [
    "GARAN.IS",   # Garanti Bankası
    "THYAO.IS",   # Türk Hava Yolları
    "EREGL.IS",   # Ereğli Demir Çelik
    "AKBNK.IS",   # Akbank
    "SAHOL.IS"    # Sabancı Holding
]

# BIST 30 Hisseleri (gelecekte kullanılacak)
BIST30_HISSELER = [
    "AKBNK.IS", "ALARK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS",
    "EKGYO.IS", "ENJSA.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS",
    "GUBRF.IS", "HEKTS.IS", "ISCTR.IS", "KCHOL.IS", "KONTR.IS",
    "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "PETKM.IS", "PGSUS.IS",
    "SAHOL.IS", "SASA.IS", "SISE.IS", "TAVHL.IS", "TCELL.IS",
    "THYAO.IS", "TKFEN.IS", "TOASO.IS", "TUPRS.IS", "YKBNK.IS"
]

# Zaman dilimleri
TIMEFRAMES = {
    '1d': {
        'period': '2y',      # 2 yıllık veri (yaklaşık 500 iş günü)
        'interval': '1d'
    },
    '1h': {
        'period': '60d',     # 60 günlük veri (60*7.5 = 450 saat)
        'interval': '1h'
    }
}

# Teknik İndikatör Parametreleri
INDICATORS = {
    'SMA': {
        'periods': [20, 50, 200]
    },
    'EMA': {
        'periods': [12, 26, 50]
    },
    'RSI': {
        'period': 14
    },
    'MACD': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9
    },
    'BBANDS': {
        'period': 20,
        'std_dev': 2
    },
    'STOCH': {
        'fastk_period': 14,
        'slowk_period': 3,
        'slowd_period': 3
    },
    'ATR': {
        'period': 14
    },
    'ADX': {
        'period': 14
    },
    'OBV': {},
    'WILLR': {
        'period': 14
    }
}

# Sinyal Üretim Ayarları
SIGNAL_SETTINGS = {
    'trend_weight': 0.50,        # Trend indikatörleri ağırlığı
    'momentum_weight': 0.35,     # Momentum indikatörleri ağırlığı
    'volatility_weight': 0.15,   # Volatilite indikatörleri ağırlığı
    'strong_threshold': 65,      # Güçlü AL sinyali eşiği
    'weak_threshold': 35         # Güçlü SAT sinyali eşiği
}

# Backtest Ayarları
BACKTEST_SETTINGS = {
    'commission': 0.001,         # İşlem komisyonu (%0.1)
    'slippage': 0.0005,          # Slippage (%0.05)
    'holding_period': 20,        # Maksimum tutma süresi (bar sayısı)
    'initial_capital': 100000,   # Başlangıç sermayesi (TL)
    'position_size': 0.10        # Pozisyon büyüklüğü (sermayenin %10'u)
}

# Veritabanı Ayarları
DATABASE_PATH = 'trading_data.db'

# Loglama
LOG_LEVEL = 'INFO'
