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
ACTIVE_STOCKS = BIST100_HISSELER     # BIST100 (100 hisse) - TÜM HİSSELER
# ACTIVE_STOCKS = BIST50_HISSELER    # BIST50 (50 hisse)
# ACTIVE_STOCKS = BIST30_HISSELER    # BIST30 (30 hisse)
# ACTIVE_STOCKS = TEST_HISSELER      # Test için 5 hisse

# ============================================================================
# TÜM ZAMAN DİLİMLERİ - 9 Farklı Timeframe (500 mum her biri için)
# ============================================================================
TIMEFRAMES = {
    '1m': {
        'period': '5d',       # 5 günlük veri (5*390 = ~1950 dakika, 500+ mum)
        'interval': '1m',
        'bars': 500
    },
    '5m': {
        'period': '25d',      # 25 günlük veri (25*78 = ~1950 5-dakika, 500+ mum)
        'interval': '5m',
        'bars': 500
    },
    '15m': {
        'period': '60d',      # 60 günlük veri (60*26 = ~1560 15-dakika, 500+ mum)
        'interval': '15m',
        'bars': 500
    },
    '30m': {
        'period': '60d',      # 60 günlük veri (60*13 = ~780 30-dakika, 500+ mum)
        'interval': '30m',
        'bars': 500
    },
    '1h': {
        'period': '90d',      # 90 günlük veri (90*6.5 = ~585 saat, 500+ mum)
        'interval': '1h',
        'bars': 500
    },
    '4h': {
        'period': '730d',     # 2 yıllık veri (~500 4-saatlik mum)
        'interval': '1h',     # Yahoo Finance 4h desteklemiyor, 1h'yi resample edeceğiz
        'bars': 500,
        'resample': '4h'      # 1h veriden 4h'ye dönüştür
    },
    '1d': {
        'period': '2y',       # 2 yıllık veri (~500 iş günü)
        'interval': '1d',
        'bars': 500
    },
    '1w': {
        'period': '10y',      # 10 yıllık veri (~520 hafta, 500+ mum)
        'interval': '1wk',
        'bars': 500
    },
    '1M': {
        'period': 'max',      # Maksimum veri (~500+ ay için yeterli)
        'interval': '1mo',
        'bars': 500
    }
}

# ============================================================================
# 25+ PROFESYONEL TEKNİK İNDİKATÖRLER VE OSİLATÖRLER
# ============================================================================
INDICATORS = {
    # ========== TREND İNDİKATÖRLERİ (Trend Following) ==========
    'SMA': {
        'periods': [10, 20, 50, 100, 200]  # Simple Moving Average
    },
    'EMA': {
        'periods': [9, 12, 21, 26, 50, 100, 200]  # Exponential Moving Average
    },
    'WMA': {
        'periods': [10, 20, 50]  # Weighted Moving Average
    },
    'DEMA': {
        'periods': [21, 50]  # Double Exponential Moving Average
    },
    'TEMA': {
        'periods': [21, 50]  # Triple Exponential Moving Average
    },
    'KAMA': {
        'period': 30  # Kaufman Adaptive Moving Average
    },
    'MAMA': {
        'fastlimit': 0.5,
        'slowlimit': 0.05  # MESA Adaptive Moving Average
    },
    'T3': {
        'period': 5,
        'vfactor': 0.7  # Triple Exponential Moving Average (T3)
    },
    'ADX': {
        'period': 14  # Average Directional Index (Trend Strength)
    },
    'ADXR': {
        'period': 14  # ADX Rating
    },
    'AROON': {
        'period': 25  # Aroon Up/Down (Trend Change)
    },
    'AROONOSC': {
        'period': 25  # Aroon Oscillator
    },
    'DX': {
        'period': 14  # Directional Movement Index
    },
    'MINUS_DI': {
        'period': 14  # Minus Directional Indicator
    },
    'PLUS_DI': {
        'period': 14  # Plus Directional Indicator
    },
    'PSAR': {
        'acceleration': 0.02,
        'maximum': 0.2  # Parabolic SAR
    },

    # ========== MOMENTUM OSİLATÖRLERİ (Momentum Indicators) ==========
    'RSI': {
        'period': 14  # Relative Strength Index
    },
    'STOCH': {
        'fastk_period': 14,
        'slowk_period': 3,
        'slowd_period': 3  # Stochastic Oscillator
    },
    'STOCHRSI': {
        'timeperiod': 14,
        'fastk_period': 5,
        'fastd_period': 3  # Stochastic RSI
    },
    'MACD': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9  # Moving Average Convergence Divergence
    },
    'MACDEXT': {
        'fast_period': 12,
        'slow_period': 26,
        'signal_period': 9  # MACD with controllable MA type
    },
    'MOM': {
        'period': 10  # Momentum
    },
    'ROC': {
        'period': 10  # Rate of Change
    },
    'ROCP': {
        'period': 10  # Rate of Change Percentage
    },
    'ROCR': {
        'period': 10  # Rate of Change Ratio
    },
    'PPO': {
        'fast_period': 12,
        'slow_period': 26  # Percentage Price Oscillator
    },
    'CMO': {
        'period': 14  # Chande Momentum Oscillator
    },
    'CCI': {
        'period': 14  # Commodity Channel Index
    },
    'WILLR': {
        'period': 14  # Williams %R
    },
    'ULTOSC': {
        'timeperiod1': 7,
        'timeperiod2': 14,
        'timeperiod3': 28  # Ultimate Oscillator
    },
    'MFI': {
        'period': 14  # Money Flow Index
    },
    'BOP': {},  # Balance of Power
    'TRIX': {
        'period': 30  # Triple Exponential Average
    },

    # ========== VOLATİLİTE İNDİKATÖRLERİ (Volatility) ==========
    'ATR': {
        'period': 14  # Average True Range
    },
    'NATR': {
        'period': 14  # Normalized ATR
    },
    'TRANGE': {},  # True Range
    'BBANDS': {
        'period': 20,
        'std_dev': 2  # Bollinger Bands
    },

    # ========== VOLUME İNDİKATÖRLERİ (Volume) ==========
    'OBV': {},  # On Balance Volume
    'AD': {},  # Chaikin A/D Line
    'ADOSC': {
        'fast_period': 3,
        'slow_period': 10  # Chaikin A/D Oscillator
    },

    # ========== CYCLE İNDİKATÖRLERİ (Cycle/Pattern) ==========
    'HT_DCPERIOD': {},  # Hilbert Transform - Dominant Cycle Period
    'HT_DCPHASE': {},  # Hilbert Transform - Dominant Cycle Phase
    'HT_PHASOR': {},  # Hilbert Transform - Phasor Components
    'HT_SINE': {},  # Hilbert Transform - SineWave
    'HT_TRENDMODE': {},  # Hilbert Transform - Trend vs Cycle Mode

    # ========== FİYAT TRANSFORM (Price Transform) ==========
    'AVGPRICE': {},  # Average Price
    'MEDPRICE': {},  # Median Price
    'TYPPRICE': {},  # Typical Price
    'WCLPRICE': {},  # Weighted Close Price

    # ========== PATTERN RECOGNITION (Chart Patterns) ==========
    'CDL_PATTERNS': {
        'enabled': True  # 60+ candlestick patterns (TA-Lib)
    }
}

# ============================================================================
# GELİŞMİŞ PİYASA VERİLERİ (Market Data)
# ============================================================================
MARKET_DATA_SETTINGS = {
    # Volume Profile
    'volume_profile': {
        'enabled': True,
        'num_bins': 24  # Volume profile için kaç fiyat seviyesi
    },

    # Order Flow (alış/satış basıncı)
    'order_flow': {
        'enabled': True,
        'volume_delta': True,  # Alıcı-Satıcı volume farkı
        'cumulative_delta': True
    },

    # Market Breadth (piyasa genişliği)
    'market_breadth': {
        'enabled': True,
        'advance_decline': True,  # Yükselen/düşen hisse oranı
        'new_highs_lows': True    # Yeni zirve/dip yapan hisse sayısı
    },

    # Sektor Analizi
    'sector_analysis': {
        'enabled': True,
        'sectors': ['FINANS', 'SANAYI', 'TEKNOLOJI', 'ENERJI']
    },

    # Ekonomik Veriler
    'economic_data': {
        'enabled': True,
        'indicators': ['USDTRY', 'BIST100_INDEX']  # Dolar/TL, BIST100 endeksi
    }
}

# ============================================================================
# SİNYAL ÜRETİM AYARLARI (Signal Generation)
# ============================================================================
SIGNAL_SETTINGS = {
    # Ağırlıklar (Toplamı 1.0 olmalı)
    'trend_weight': 0.40,        # Trend indikatörleri ağırlığı
    'momentum_weight': 0.30,     # Momentum indikatörleri ağırlığı
    'volatility_weight': 0.15,   # Volatilite indikatörleri ağırlığı
    'volume_weight': 0.10,       # Volume indikatörleri ağırlığı
    'pattern_weight': 0.05,      # Pattern recognition ağırlığı

    # Eşikler
    'strong_buy_threshold': 70,   # Güçlü AL sinyali eşiği
    'buy_threshold': 60,          # AL sinyali eşiği
    'hold_threshold_high': 55,    # BEKLE üst eşiği
    'hold_threshold_low': 45,     # BEKLE alt eşiği
    'sell_threshold': 40,         # SAT sinyali eşiği
    'strong_sell_threshold': 30,  # Güçlü SAT sinyali eşiği

    # Multi-timeframe Analizi
    'use_multi_timeframe': True,
    'higher_timeframe_weight': 0.6,  # Üst timeframe ağırlığı
    'lower_timeframe_weight': 0.4,   # Alt timeframe ağırlığı

    # Sinyal Filtreleme
    'min_volume_ratio': 1.5,     # Minimum hacim oranı (ortalamaya göre)
    'min_volatility': 0.005,     # Minimum volatilite (%0.5)
    'require_confirmation': True  # Sinyal onayı gerekli mi?
}

# ============================================================================
# BACKTEST AYARLARI (Backtesting)
# ============================================================================
BACKTEST_SETTINGS = {
    # İşlem Maliyetleri
    'commission': 0.001,         # İşlem komisyonu (%0.1)
    'slippage': 0.0005,          # Slippage (%0.05)

    # Risk Yönetimi
    'initial_capital': 100000,   # Başlangıç sermayesi (TL)
    'position_size': 0.10,       # Pozisyon büyüklüğü (sermayenin %10'u)
    'max_positions': 10,         # Maksimum eş zamanlı pozisyon sayısı
    'stop_loss': 0.05,           # Stop loss (%5)
    'take_profit': 0.15,         # Take profit (%15)

    # Tutma Süresi
    'holding_period': 20,        # Maksimum tutma süresi (bar sayısı)
    'min_holding_period': 3,     # Minimum tutma süresi (bar sayısı)

    # Performans Metrikleri
    'calculate_sharpe': True,    # Sharpe ratio hesapla
    'calculate_sortino': True,   # Sortino ratio hesapla
    'calculate_calmar': True,    # Calmar ratio hesapla
    'calculate_max_dd': True,    # Maximum drawdown hesapla
    'risk_free_rate': 0.15       # Risksiz faiz oranı (yıllık %15 - Türkiye)
}

# ============================================================================
# PARAMETRE OPTİMİZASYONU (Parameter Optimization)
# ============================================================================
OPTIMIZATION_SETTINGS = {
    'enabled': True,

    # Optimizasyon Yöntemi
    'method': 'grid_search',  # 'grid_search', 'random_search', 'genetic_algorithm'

    # Grid Search Parametreleri
    'grid_search': {
        'rsi_periods': [10, 14, 20],
        'macd_fast': [8, 12, 16],
        'macd_slow': [21, 26, 31],
        'sma_periods': [[10, 20, 50], [20, 50, 200]],
        'ema_periods': [[9, 21, 55], [12, 26, 50]]
    },

    # Genetic Algorithm Parametreleri
    'genetic_algorithm': {
        'population_size': 50,
        'generations': 100,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8
    },

    # Walk-Forward Optimizasyonu
    'walk_forward': {
        'enabled': True,
        'in_sample_ratio': 0.7,   # %70 training
        'out_sample_ratio': 0.30,  # %30 testing
        'num_splits': 5            # 5-fold cross-validation
    },

    # Optimizasyon Hedefi
    'objective': 'sharpe_ratio',  # 'sharpe_ratio', 'total_return', 'win_rate', 'profit_factor'

    # Overfitting Kontrolü
    'use_validation_set': True,
    'min_trades': 30,              # Minimum işlem sayısı
    'max_drawdown_limit': 0.25     # Maksimum %25 drawdown
}

# ============================================================================
# MACHINE LEARNING AYARLARI (ML-Based Signal Generation)
# ============================================================================
ML_SETTINGS = {
    'enabled': True,

    # Model Türü
    'model_type': 'ensemble',  # 'random_forest', 'xgboost', 'lightgbm', 'ensemble'

    # Feature Engineering
    'features': {
        'use_indicators': True,
        'use_price_patterns': True,
        'use_volume_patterns': True,
        'use_market_regime': True,
        'lookback_periods': [5, 10, 20, 50]
    },

    # Training
    'training': {
        'test_size': 0.2,
        'validation_size': 0.1,
        'cv_folds': 5,
        'scoring': 'f1_weighted'
    },

    # Ensemble (birden fazla model kullan)
    'ensemble': {
        'models': ['random_forest', 'xgboost', 'lightgbm'],
        'voting': 'soft',  # 'soft' veya 'hard'
        'weights': [0.3, 0.4, 0.3]
    },

    # Model Güncelleme
    'retrain_frequency': 'monthly',  # 'daily', 'weekly', 'monthly'
    'min_samples': 1000               # Minimum training sample sayısı
}

# ============================================================================
# VERİTABANI AYARLARI
# ============================================================================
DATABASE_PATH = 'trading_data.db'

# ============================================================================
# LOGLAMA
# ============================================================================
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_FILE = 'trading_system.log'
