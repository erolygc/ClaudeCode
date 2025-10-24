# Turkish Stock Market Algorithmic Trading System
## BIST Algoritmik Ticaret Platformu

Türkiye Borsası (BIST) için kapsamlı bir algoritmik ticaret ve backtest sistemi.

---

## 📋 Proje Özeti

Bu proje, Türkiye hisse senetleri için tam otomatik bir trading sistemi sunar:

- **Çoklu Veri Katmanı**: BIST30 hisseleri, çoklu timeframe'ler (1d, 1h)
- **10+ Teknik İndikatör**: SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic, ATR, ADX, OBV, Williams %R
- **Akıllı Sinyal Sistemi**: Ağırlıklı konsensüs yaklaşımı (Trend %50, Momentum %35, Volatilite %15)
- **Profesyonel Backtest**: Komisyon/slippage modelleme, performans metrikleri
- **Azure Deployment**: Otomatik günlük execution, email bildirimleri
- **Modüler Yapı**: Kolayca genişletilebilir, bakımı kolay

---

## 🏗️ Sistem Mimarisi

```
ClaudeCode/
├── config/
│   └── settings.py          # Merkezi konfigürasyon
├── database/
│   └── db_manager.py         # SQLite veritabanı yönetimi
├── collectors/
│   └── market_data_collector.py  # Piyasa verisi toplama
├── indicators/
│   └── technical_indicators.py   # TA-Lib indikatör hesaplamaları
├── strategies/
│   ├── signal_generator.py       # Sinyal üretim motoru
│   └── backtest_engine.py        # Backtest motoru (FAZ 9)
├── collect_all_data.py           # Toplu veri toplama
├── calculate_indicators.py       # Toplu indikatör hesaplama
├── generate_signals.py           # Toplu sinyal üretimi
└── backtest_all.py              # Toplu backtest (FAZ 9)
```

---

## 🚀 Kurulum

### Gereksinimler

```bash
# Python paketleri
python -m pip install pandas numpy ta-lib openpyxl

# yfinance için (opsiyonel - gerçek veri için)
python -m pip install yfinance
```

### Veritabanı İlk Kurulum

```bash
# 1. Test verisi oluştur (hızlı demo için)
python create_sample_data.py

# VEYA: Gerçek veri topla (yfinance gerekli)
python collect_all_data.py
python calculate_indicators.py
python generate_signals.py
```

---

## 📊 Kullanım

### FAZ 6: Veri Toplama

```bash
python collect_all_data.py
```

**Çıktı**:
- BIST30 hisseleri için OHLCV verisi
- 1d: ~500 bar (2 yıllık)
- 1h: ~400 bar (60 günlük)

### FAZ 7: İndikatör Hesaplama

```bash
python calculate_indicators.py
```

**Hesaplanan İndikatörler**:
- **Trend**: SMA (20/50/200), EMA (12/26/50), MACD, ADX
- **Momentum**: RSI, Stochastic, Williams %R
- **Volatilite**: Bollinger Bands, ATR
- **Volume**: OBV

### FAZ 8: Sinyal Üretimi

```bash
python generate_signals.py
```

**Sinyal Sistemi**:
- **BUY**: Score >= 65/100 (Güçlü AL sinyali)
- **SELL**: Score <= 35/100 (Güçlü SAT sinyali)
- **HOLD**: 35 < Score < 65 (Nötr)

**Örnek Çıktı**:
```
🎯 GARAN.IS (1h) 🟢 BUY (71.5/100)
🎯 EREGL.IS (1d) 🔴 SELL (31.5/100)
🎯 THYAO.IS (1d) 🟡 HOLD (63.1/100)
```

### FAZ 9: Backtest (Bu Faz)

```bash
python backtest_all.py
```

**Backtest Özellikleri**:
- ✅ Gerçekçi komisyon modelleme (%0.1)
- ✅ Slippage simülasyonu (%0.05)
- ✅ Performans metrikleri (getiri %, kazanma oranı, max drawdown)
- ✅ Sinyal gücü korelasyon analizi
- ✅ Hisse/timeframe bazında performans karşılaştırması
- ✅ Excel export ile detaylı raporlama

**Örnek Backtest Raporu**:
```
================================================================================
📈 BACKTEST PERFORMANS RAPORU
================================================================================

📊 GENEL İSTATİSTİKLER:
   Toplam İşlem: 10
   Kazanan İşlem: 6 (60.0%)
   Kaybeden İşlem: 4 (40.0%)
   Ortalama Getiri: 2.35%
   Ortalama Kazanç: 4.12%
   Ortalama Kayıp: -1.23%

🏆 HİSSE BAZINDA PERFORMANS:
   1. GARAN.IS: 3.45% avg return, 66.7% win rate (3 trades)
   2. THYAO.IS: 2.10% avg return, 50.0% win rate (2 trades)

💪 SİNYAL GÜCÜ ANALİZİ:
   Güçlü Sinyaller (Score >=65): 75.0% win rate, 3.89% avg return
   Zayıf Sinyaller (Score 35-65): 40.0% win rate, 0.45% avg return
```

---

## ⚙️ Konfigürasyon

`config/settings.py` dosyasından tüm parametreler ayarlanabilir:

```python
# Test hisseleri
TEST_HISSELER = ["GARAN.IS", "THYAO.IS", "EREGL.IS", "AKBNK.IS", "SAHOL.IS"]

# Backtest ayarları
BACKTEST_SETTINGS = {
    'commission': 0.001,         # %0.1 komisyon
    'slippage': 0.0005,          # %0.05 slippage
    'holding_period': 20,        # Max 20 bar tutma süresi
    'initial_capital': 100000,   # 100K TL başlangıç
    'position_size': 0.10        # Sermayenin %10'u
}

# Sinyal ağırlıkları
SIGNAL_SETTINGS = {
    'trend_weight': 0.50,        # Trend %50
    'momentum_weight': 0.35,     # Momentum %35
    'volatility_weight': 0.15,   # Volatilite %15
    'strong_threshold': 65,      # Güçlü AL eşiği
    'weak_threshold': 35         # Güçlü SAT eşiği
}
```

---

## 📈 Performans ve Ölçeklenebilirlik

**Mevcut Durum (Test)**:
- 3 hisse × 2 timeframe = 6 çift
- ~2,700 OHLCV bar
- ~47,000 indikatör değeri
- ~6 sinyal

**Production için (BIST30)**:
- 30 hisse × 2 timeframe = 60 çift
- ~81,000 OHLCV bar
- ~1,500,000 indikatör değeri
- ~60+ sinyal

**Optimizasyon Fırsatları**:
- Batch INSERT ile veritabanı hızlandırma
- PostgreSQL migration (SQLite'dan)
- Paralel indikatör hesaplama
- Redis caching
- Async data collection

---

## 🔮 Gelecek Geliştirmeler

### ✅ FAZ 10: Azure Deployment (TAMAMLANDI!)

Sistem artık Azure'da otomatik olarak çalışabilir:

**Özellikler:**
- ⏰ **Otomatik Günlük Execution**: Timer trigger ile her iş günü saat 18:00
- 📧 **Email Bildirimleri**: Günlük raporlar ve güçlü sinyal alerts
- ☁️ **Serverless Architecture**: Azure Functions (Consumption Plan)
- 🗄️ **PostgreSQL Ready**: Production için database migration desteği
- 📊 **Monitoring**: Application Insights entegrasyonu
- 🔐 **Secrets Management**: Azure Key Vault ready

**Deployment:**
```bash
# Quick start
./scripts/deploy_azure.sh

# Detaylı guide
docs/DEPLOYMENT_GUIDE.md
```

**Dosyalar:**
- `azure_functions/function_app.py` - Ana Azure Function
- `utils/email_sender.py` - Email notification system
- `scripts/deploy_azure.sh` - Deployment script
- `docs/DEPLOYMENT_GUIDE.md` - Deployment dokümantasyonu

### Gelecek Özellikler
- ⏰ Daha fazla timeframe (15m, 5m)
- 📊 Order Book / Trade Book entegrasyonu (paid API)
- 🤖 Machine Learning modelleri
- 📱 Web dashboard (React + FastAPI)
- 🔔 Telegram/Discord bot bildirimleri
- 📈 Gerçek zamanlı trading

---

## 🛠️ Teknik Detaylar

### Veritabanı Şeması

**hisseler**: Hisse listesi
**ohlcv_data**: Fiyat/volume verisi
**indicators**: Teknik indikatör değerleri
**signals**: Üretilen sinyaller
**backtest_results**: Backtest sonuçları

### Backtest Motoru Algoritması

1. Sinyali al (ticker, timeframe, signal_type, date, score)
2. Sinyal tarihinden SONRA ki verileri getir
3. Entry: Bir sonraki barın OPEN fiyatı (+ slippage)
4. Holding period boyunca takip et (max 20 bar)
5. Exit: Son barın CLOSE fiyatı (- slippage)
6. Metrikleri hesapla:
   - Net Return % (komisyon dahil)
   - Max Drawdown %
   - Max Profit %
   - Win/Loss durumu

### Sinyal Üretim Algoritması

```python
# Her kategori için analiz
trend_score = analyze_trend_indicators()      # SMA, EMA, MACD, ADX
momentum_score = analyze_momentum_indicators() # RSI, Stoch, Williams%R
volatility_score = analyze_volatility_indicators() # BB, ATR

# Ağırlıklı kombine skor
final_score = (
    trend_score * 0.50 +
    momentum_score * 0.35 +
    volatility_score * 0.15
)

# Sinyal belirle
if final_score >= 65: return "BUY"
elif final_score <= 35: return "SELL"
else: return "HOLD"
```

---

## 📄 Lisans

Bu proje Claude Code tarafından geliştirilmiştir.

---

## 🤝 Katkıda Bulunma

Bu açık kaynak bir proje değildir, ancak öneriler ve geri bildirimler memnuniyetle karşılanır.

---

## 📞 İletişim

Sorularınız için issue açabilir veya proje sahibi ile iletişime geçebilirsiniz.

---

**Not**: Bu sistem eğitim ve araştırma amaçlıdır. Gerçek trading kararlarınızı vermeden önce profesyonel finansal danışmanlık alınız. Geçmiş performans gelecekteki sonuçları garanti etmez.
