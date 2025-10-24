"""
Proje Ayarları - Tüm konfigürasyon burada
"""

# Test için 5 hisse (hızlı test için kullanılabilir)
TEST_HISSELER = [
    "GARAN.IS",   # Garanti Bankası
    "THYAO.IS",   # Türk Hava Yolları
    "EREGL.IS",   # Ereğli Demir Çelik
    "AKBNK.IS",   # Akbank
    "SAHOL.IS"    # Sabancı Holding
]

# BIST 30 Hisseleri (en büyük 30 şirket)
BIST30_HISSELER = [
    'AKBNK.IS',   # Akbank
    'ARCLK.IS',   # Arçelik
    'ASELS.IS',   # Aselsan
    'BIMAS.IS',   # BIM
    'DOHOL.IS',   # Doğan Holding
    'EKGYO.IS',   # Emlak Konut GYO
    'ENKAI.IS',   # Enka İnşaat
    'EREGL.IS',   # Ereğli Demir Çelik
    'FROTO.IS',   # Ford Otosan
    'GARAN.IS',   # Garanti Bankası
    'HALKB.IS',   # Halkbank
    'ISCTR.IS',   # İş Bankası (C)
    'KCHOL.IS',   # Koç Holding
    'KRDMD.IS',   # Kardemir
    'ODAS.IS',    # Odaş Elektrik
    'OYAKC.IS',   # Oyak Çimento
    'PETKM.IS',   # Petkim
    'PGSUS.IS',   # Pegasus
    'SAHOL.IS',   # Sabancı Holding
    'SASA.IS',    # Sasa Polyester
    'SISE.IS',    # Şişe Cam
    'TAVHL.IS',   # TAV Havalimanları
    'TCELL.IS',   # Turkcell
    'THYAO.IS',   # Türk Hava Yolları
    'TKFEN.IS',   # Tekfen Holding
    'TOASO.IS',   # Tofaş
    'TTKOM.IS',   # Türk Telekom
    'TUPRS.IS',   # Tüpraş
    'VAKBN.IS',   # Vakıfbank
    'YKBNK.IS',   # Yapı Kredi Bankası
]

# BIST 50 - BIST30 + ek 20 hisse
BIST50_EXTRA = [
    'AEFES.IS',   # Anadolu Efes
    'AHGAZ.IS',   # Ahlatcı Gaz
    'AKSA.IS',    # Aksa Akrilik
    'AKSEN.IS',   # Aksa Enerji
    'ALARK.IS',   # Alarko Holding
    'AYGAZ.IS',   # Aygaz
    'BRISA.IS',   # Brisa
    'CIMSA.IS',   # Çimsa
    'DOAS.IS',    # Doğuş Otomotiv
    'ENJSA.IS',   # Enerjisa
    'GLYHO.IS',   # Global Yatırım Holding
    'GUBRF.IS',   # Gübre Fabrikaları
    'HEKTS.IS',   # Hektaş
    'KOZAA.IS',   # Koza Altın
    'KOZAL.IS',   # Koza Anadolu Metal
    'LOGO.IS',    # Logo Yazılım
    'MAVI.IS',    # Mavi Giyim
    'MGROS.IS',   # Migros
    'SOKM.IS',    # Şok Marketler
    'VESTL.IS',   # Vestel
]

BIST50_HISSELER = BIST30_HISSELER + BIST50_EXTRA

# BIST 100 - BIST50 + ek 50 hisse
BIST100_EXTRA = [
    'AGHOL.IS',   # Ag Anadolu Grubu Holding
    'AKFGY.IS',   # Akfen GYO
    'AKGRT.IS',   # Aksigorta
    'AKSUE.IS',   # Aksu Enerji
    'ALBRK.IS',   # Albaraka Türk
    'ALGYO.IS',   # Albaraka GYO
    'ALKIM.IS',   # Alkim Kağıt
    'ANHYT.IS',   # Anadolu Hayat Emeklilik
    'ANSGR.IS',   # Anadolu Sigorta
    'AYDEM.IS',   # Aydem Enerji
    'BAGFS.IS',   # Bagfaş
    'BANVT.IS',   # Banvit
    'BERA.IS',    # Bera Holding
    'BJKAS.IS',   # Beşiktaş
    'BRSAN.IS',   # Borusan Mannesmann
    'BSOKE.IS',   # Batısöke Söke Çimento
    'BTCIM.IS',   # Batıçim
    'BUCIM.IS',   # Bursa Çimento
    'CCOLA.IS',   # Coca Cola İçecek
    'CEMTS.IS',   # Cemtaş
    'CLEBI.IS',   # Çelebi
    'CONSE.IS',   # Consus Enerji
    'CVKMD.IS',   # Cvk Maden
    'DEVA.IS',    # Deva Holding
    'DYOBY.IS',   # Dyo Boya
    'EGEEN.IS',   # Ege Endüstri
    'EGPRO.IS',   # Ege Profil
    'FENER.IS',   # Fenerbahçe
    'GENIL.IS',   # Gen İlaç
    'GESAN.IS',   # Gizem Sanayi
    'GOZDE.IS',   # Gözde Girişim
    'GSRAY.IS',   # Galatasaray
    'IEYHO.IS',   # İhlas Ev Aletleri
    'IHEVA.IS',   # İheva
    'IPEKE.IS',   # İpek Enerji
    'ISDMR.IS',   # İskenderun Demir Çelik
    'IZMDC.IS',   # İzmir Demir Çelik
    'KARSN.IS',   # Karsan
    'KLMSN.IS',   # Klimasan
    'KONTR.IS',   # Kontrolmatik
    'KONYA.IS',   # Konya Çimento
    'KORDS.IS',   # Kordsa
    'KRTEK.IS',   # Kartonsan
    'MPARK.IS',   # MLP Sağlık
    'NETAS.IS',   # Netaş
    'NTTUR.IS',   # Net Turizm
    'OTKAR.IS',   # Otokar
    'PARSN.IS',   # Parsan
    'PRKME.IS',   # Park Elektrik
    'TTRAK.IS',   # Türk Traktör
]

BIST100_HISSELER = BIST50_HISSELER + BIST100_EXTRA

# Aktif hisse listesi (değiştirerek hangi endeksi kullanacağınızı seçin)
ACTIVE_STOCKS = BIST30_HISSELER      # BIST30 (30 hisse)
# ACTIVE_STOCKS = TEST_HISSELER      # Test için 5 hisse
# ACTIVE_STOCKS = BIST50_HISSELER    # BIST50
# ACTIVE_STOCKS = BIST100_HISSELER   # BIST100 (tüm hisseler)

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
