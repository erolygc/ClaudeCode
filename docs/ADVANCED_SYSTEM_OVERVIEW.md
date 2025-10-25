# Gelişmiş Trading Sistemi - Teknik Özet

## 🎯 Sistem Kapsamı

Bu dokümantasyon, kapsamlı algoritmik trading sisteminin tüm özelliklerini açıklar.

---

## 📊 1. KAPSAM VE VERİ

### 1.1 Hisse Senetleri
- ✅ **BIST100 Tüm Hisseler**: 100 hisse senedi
- ✅ **BIST50**: 50 hisse senedi
- ✅ **BIST30**: 30 hisse senedi
- ✅ **Test Modu**: 5 hisse (hızlı test için)

**Toplam Hisse**: 100 (BIST100)

### 1.2 Zaman Dilimleri (9 Timeframe)
Her hisse için **500 mum** verisi:

| Timeframe | Açıklama | Veri Periyodu |
|-----------|----------|---------------|
| **1m** | 1 dakika | 5 gün |
| **5m** | 5 dakika | 25 gün |
| **15m** | 15 dakika | 60 gün |
| **30m** | 30 dakika | 60 gün |
| **1h** | 1 saat | 90 gün |
| **4h** | 4 saat | 2 yıl |
| **1d** | 1 gün | 2 yıl |
| **1w** | 1 hafta | 10 yıl |
| **1M** | 1 ay | Maksimum |

**Toplam Veri Seti**: 100 hisse × 9 timeframe × 500 mum = **450,000 mum**

### 1.3 Gelişmiş Piyasa Verileri

#### Volume Profile
- ✅ 24 fiyat seviyeli volume dağılımı
- ✅ Value Area (High/Low)
- ✅ Point of Control (POC)

#### Order Flow
- ✅ Volume Delta (Alıcı - Satıcı)
- ✅ Cumulative Delta
- ✅ Alış/Satış Basıncı

#### Market Breadth
- ✅ Advance/Decline Ratio
- ✅ Yeni zirve/dip yapan hisse sayısı
- ✅ Piyasa genişlik indikatörleri

#### Sektor Analizi
- ✅ Finans Sektörü
- ✅ Sanayi Sektörü
- ✅ Teknoloji Sektörü
- ✅ Enerji Sektörü

#### Ekonomik Veriler
- ✅ USD/TRY döviz kuru
- ✅ BIST100 Endeks verisi

---

## 📈 2. TEKNİK İNDİKATÖRLER (50+)

### 2.1 Trend İndikatörleri (16 İndikatör)
| İndikatör | Açıklama | Parametreler |
|-----------|----------|--------------|
| **SMA** | Simple Moving Average | 10, 20, 50, 100, 200 |
| **EMA** | Exponential Moving Average | 9, 12, 21, 26, 50, 100, 200 |
| **WMA** | Weighted Moving Average | 10, 20, 50 |
| **DEMA** | Double Exponential MA | 21, 50 |
| **TEMA** | Triple Exponential MA | 21, 50 |
| **KAMA** | Kaufman Adaptive MA | 30 |
| **MAMA** | MESA Adaptive MA | fastlimit=0.5, slowlimit=0.05 |
| **T3** | Triple Exponential (T3) | period=5, vfactor=0.7 |
| **ADX** | Average Directional Index | 14 |
| **ADXR** | ADX Rating | 14 |
| **AROON** | Aroon Up/Down | 25 |
| **AROONOSC** | Aroon Oscillator | 25 |
| **DX** | Directional Movement Index | 14 |
| **MINUS_DI** | Minus Directional Indicator | 14 |
| **PLUS_DI** | Plus Directional Indicator | 14 |
| **PSAR** | Parabolic SAR | accel=0.02, max=0.2 |

**Trend İndikatörler Toplamı**: 16

### 2.2 Momentum Osilatörleri (18 İndikatör)
| İndikatör | Açıklama | Parametreler |
|-----------|----------|--------------|
| **RSI** | Relative Strength Index | 14 |
| **STOCH** | Stochastic Oscillator | K=14, D=3 |
| **STOCHRSI** | Stochastic RSI | 14, K=5, D=3 |
| **MACD** | MACD | Fast=12, Slow=26, Signal=9 |
| **MACDEXT** | MACD Extended | Fast=12, Slow=26, Signal=9 |
| **MOM** | Momentum | 10 |
| **ROC** | Rate of Change | 10 |
| **ROCP** | Rate of Change Percentage | 10 |
| **ROCR** | Rate of Change Ratio | 10 |
| **PPO** | Percentage Price Oscillator | Fast=12, Slow=26 |
| **CMO** | Chande Momentum Oscillator | 14 |
| **CCI** | Commodity Channel Index | 14 |
| **WILLR** | Williams %R | 14 |
| **ULTOSC** | Ultimate Oscillator | 7/14/28 |
| **MFI** | Money Flow Index | 14 |
| **BOP** | Balance of Power | - |
| **TRIX** | Triple Exponential Average | 30 |

**Momentum İndikatörler Toplamı**: 17

### 2.3 Volatilite İndikatörleri (4 İndikatör)
| İndikatör | Açıklama | Parametreler |
|-----------|----------|--------------|
| **ATR** | Average True Range | 14 |
| **NATR** | Normalized ATR | 14 |
| **TRANGE** | True Range | - |
| **BBANDS** | Bollinger Bands | period=20, std=2 |

### 2.4 Volume İndikatörleri (3 İndikatör)
| İndikatör | Açıklama | Parametreler |
|-----------|----------|--------------|
| **OBV** | On Balance Volume | - |
| **AD** | Chaikin A/D Line | - |
| **ADOSC** | Chaikin A/D Oscillator | Fast=3, Slow=10 |

### 2.5 Cycle İndikatörleri (5 İndikatör)
| İndikatör | Açıklama |
|-----------|----------|
| **HT_DCPERIOD** | Hilbert Transform - Dominant Cycle Period |
| **HT_DCPHASE** | Hilbert Transform - Dominant Cycle Phase |
| **HT_PHASOR** | Hilbert Transform - Phasor Components |
| **HT_SINE** | Hilbert Transform - SineWave |
| **HT_TRENDMODE** | Hilbert Transform - Trend vs Cycle Mode |

### 2.6 Fiyat Transform (4 İndikatör)
| İndikatör | Açıklama |
|-----------|----------|
| **AVGPRICE** | Average Price |
| **MEDPRICE** | Median Price |
| **TYPPRICE** | Typical Price |
| **WCLPRICE** | Weighted Close Price |

### 2.7 Pattern Recognition
- ✅ **60+ Candlestick Patterns** (TA-Lib)

**TOPLAM İNDİKATÖR**: 50+ (Candlestick patterns dahil 110+)

---

## 🎯 3. SİNYAL ÜRETİMİ

### 3.1 Çok Katmanlı Sinyal Sistemi

#### Ağırlık Dağılımı
| Kategori | Ağırlık |
|----------|---------|
| **Trend** | %40 |
| **Momentum** | %30 |
| **Volatilite** | %15 |
| **Volume** | %10 |
| **Pattern** | %5 |

#### Sinyal Eşikleri
| Sinyal | Skor Aralığı |
|--------|-------------|
| **Güçlü AL** | 70-100 |
| **AL** | 60-69 |
| **BEKLE (Üst)** | 55-59 |
| **BEKLE (Alt)** | 45-54 |
| **SAT** | 40-44 |
| **Güçlü SAT** | 0-30 |

### 3.2 Multi-Timeframe Analizi
- ✅ **Üst Timeframe**: %60 ağırlık
- ✅ **Alt Timeframe**: %40 ağırlık

### 3.3 Sinyal Filtreleme
- ✅ Minimum hacim oranı: 1.5x ortalama
- ✅ Minimum volatilite: %0.5
- ✅ Sinyal onayı sistemi

---

## 📊 4. BACKTEST VE OPTİMİZASYON

### 4.1 Backtest Ayarları

#### İşlem Maliyetleri
- Komisyon: %0.1
- Slippage: %0.05

#### Risk Yönetimi
- Başlangıç sermayesi: 100,000 TL
- Pozisyon büyüklüğü: %10
- Maksimum pozisyon: 10 adet
- Stop Loss: %5
- Take Profit: %15

#### Tutma Süresi
- Maksimum: 20 bar
- Minimum: 3 bar

#### Performans Metrikleri
- ✅ Sharpe Ratio
- ✅ Sortino Ratio
- ✅ Calmar Ratio
- ✅ Maximum Drawdown
- ✅ Win Rate
- ✅ Profit Factor
- ✅ Risk/Reward Ratio

### 4.2 Parametre Optimizasyonu

#### Yöntemler
1. **Grid Search**: Tüm parametre kombinasyonları
2. **Random Search**: Rastgele parametre tarama
3. **Genetic Algorithm**: Evrimsel optimizasyon

#### Walk-Forward Optimizasyonu
- Training: %70
- Testing: %30
- 5-Fold Cross-Validation

#### Overfitting Kontrolü
- Validation set kullanımı
- Minimum 30 işlem
- Maksimum %25 drawdown limiti

---

## 🤖 5. MACHINE LEARNING

### 5.1 Model Türleri
- **Random Forest**
- **XGBoost**
- **LightGBM**
- **Ensemble** (3 modelin kombinasyonu)

### 5.2 Feature Engineering
- ✅ Tüm teknik indikatörler
- ✅ Fiyat pattern'leri
- ✅ Volume pattern'leri
- ✅ Market regime detection
- ✅ Lookback periods: 5, 10, 20, 50

### 5.3 Training
- Test set: %20
- Validation set: %10
- 5-Fold Cross-Validation
- Scoring: F1-Weighted

### 5.4 Ensemble Voting
- Random Forest: %30
- XGBoost: %40
- LightGBM: %30
- Voting: Soft (probability-based)

### 5.5 Model Güncelleme
- Frekans: Aylık
- Minimum sample: 1,000

---

## 📈 6. BEKLENEN PERFORMANS

### Veri Miktarı
- **Hisseler**: 100
- **Timeframes**: 9
- **Her timeframe**: 500 mum
- **Toplam mum**: 450,000
- **İndikatör/mum**: ~50
- **Toplam indikatör değeri**: ~22,500,000

### Sinyal Sayısı
- Her hisse × timeframe = 1 sinyal
- Toplam: 100 × 9 = **900 aktif sinyal**

### Backtest Sonuçları (Tahmini)
- İşlem sayısı: 5,000+
- Kazanma oranı hedefi: %60+
- Sharpe Ratio hedefi: >2.0
- Maximum Drawdown: <%20

---

## 🚀 7. KULLANIM

### 7.1 Veri Toplama
```powershell
# Tüm BIST100 için veri çek (gerçek Yahoo Finance)
python collect_all_data.py

# Beklenen süre: ~30-60 dakika (100 hisse × 9 timeframe)
```

### 7.2 İndikatör Hesaplama
```powershell
# 50+ indikatörü hesapla
python calculate_indicators.py

# Beklenen süre: ~10-20 dakika
```

### 7.3 Sinyal Üretimi
```powershell
# ML-based sinyaller üret
python generate_signals.py

# Beklenen süre: ~5-10 dakika
```

### 7.4 Backtest
```powershell
# Parametre optimizasyonu ile backtest
python backtest_all.py

# Beklenen süre: ~30-60 dakika
```

### 7.5 Sistem Durumu
```powershell
# Tüm sistemi kontrol et
python tools/system_status.py
python tools/query_db.py --stats
```

---

## 📁 8. DATABASE YAPISI

### Tablolar
- **stocks**: Hisse bilgileri
- **ohlcv_data**: 450,000 mum verisi
- **indicators**: ~22,500,000 indikatör değeri
- **signals**: 900 aktif sinyal
- **backtest_results**: Backtest sonuçları
- **ml_models**: ML model metadata
- **optimization_results**: Optimizasyon sonuçları

### Beklenen Database Boyutu
- OHLCV: ~100 MB
- İndikatörler: ~5 GB
- Sinyaller: ~10 MB
- Backtest: ~50 MB
- **Toplam**: ~5-6 GB

---

## 🎯 9. GELİŞMİŞ ÖZELLİKLER

### Gelecek Geliştirmeler
- [ ] Real-time data streaming
- [ ] Telegram/Discord bot
- [ ] Web dashboard (React)
- [ ] Portfolio optimization
- [ ] Risk management sistemi
- [ ] Automated trading (live)
- [ ] Multi-exchange support
- [ ] Options & Futures support

---

## 📚 10. DOKÜMANTASYON

- `QUICKSTART.md`: Hızlı başlangıç kılavuzu
- `DEVELOPMENT_GUIDE.md`: Geliştirme kılavuzu
- `PERFORMANCE_OPTIMIZATION.md`: Performans optimizasyonu
- `ADVANCED_SYSTEM_OVERVIEW.md`: Bu dosya

---

## ⚡ 11. PERFORMANS

### Optimizasyonlar
- ✅ Bulk INSERT (65x hız artışı)
- ✅ Database indexing (10x sorgu hızı)
- ✅ NumPy vectorization
- ✅ Multi-processing (gelecek)
- ✅ Caching (gelecek)

### Benchmark
- İndikatör hesaplama: ~7,000 indikatör/saniye
- Query hızı: <100 ms
- Sinyal üretimi: <10 ms/hisse

---

## 🎓 12. KAYNAKLAR

- **TA-Lib**: Technical Analysis Library
- **yfinance**: Yahoo Finance API
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning
- **xgboost/lightgbm**: Gradient boosting

---

**Son Güncelleme**: 2025-10-24
**Versiyon**: 2.0 (Advanced System)
