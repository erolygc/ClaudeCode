# Sistem Test Rehberi

## 🔍 Uçtan Uca Test

Tüm sistemi test etmek için özel bir test scripti hazırladık.

## Kullanım

### Windows'ta

```powershell
cd C:\Users\Botai\ClaudeCode
python test_system.py
```

### Linux/Mac'te

```bash
cd /path/to/ClaudeCode
python3 test_system.py
```

## Test Edilen Bileşenler

Test scripti aşağıdaki 7 ana bileşeni test eder:

### ✅ Test 1: Import'lar
- pandas, numpy, yfinance kurulu mu?
- TA-Lib kurulu mu?
- Tüm proje modülleri import edilebiliyor mu?

### ✅ Test 2: Veritabanı
- SQLite bağlantısı çalışıyor mu?
- Hisse ekleme/okuma çalışıyor mu?
- OHLCV veri kaydetme/okuma çalışıyor mu?

### ✅ Test 3: Veri Toplama
- yfinance ile veri çekme çalışıyor mu?
- GARAN.IS için canlı veri alınabiliyor mu?

### ✅ Test 4: İndikatör Hesaplama
- TA-Lib indikatörleri hesaplanabiliyor mu?
- RSI, SMA, MACD, Bollinger Bands çalışıyor mu?

### ✅ Test 5: Sinyal Üretimi
- Trend analizi çalışıyor mu?
- Momentum analizi çalışıyor mu?
- BUY/SELL/HOLD sinyalleri üretiliyor mu?

### ✅ Test 6: Risk Yönetimi
- Pozisyon açma/kapatma çalışıyor mu?
- Stop loss/take profit hesaplanıyor mu?
- Portföy takibi çalışıyor mu?

### ✅ Test 7: Live Trading Engine
- Engine başlatılabiliyor mu?
- Tüm bileşenler entegre çalışıyor mu?

## Beklenen Çıktı

```
================================================================================
🔍 SİSTEM TEST PAKETİ - UÇTAN UCA TEST
================================================================================

Tüm sistem bileşenleri test edilecek...


======================================================================
📦 TEST 1: Import'lar Kontrol Ediliyor...
======================================================================
✅ pandas: 2.3.3
✅ numpy: 2.3.4
✅ yfinance: 0.2.66
✅ talib: 0.4.28
✅ DatabaseManager
✅ MarketDataCollector
✅ TechnicalIndicators
✅ SignalGenerator
✅ LiveTradingEngine
✅ RiskManager
✅ LiveTradingMonitor

📊 Sonuç: 11/11 test geçti

======================================================================
💾 TEST 2: Veritabanı Test Ediliyor...
======================================================================
✅ Veritabanı bağlantısı başarılı
✅ Hisse ekleme başarılı
✅ OHLCV veri ekleme başarılı: 3 kayıt
✅ Veri okuma başarılı: 3 kayıt

✅ Veritabanı testleri başarılı

======================================================================
📡 TEST 3: Veri Toplama Test Ediliyor...
======================================================================
✅ MarketDataCollector oluşturuldu

📊 GARAN.IS için veri çekiliyor (son 5 gün)...
  GARAN.IS (1d) indiriliyor... ✅ 5 bar
✅ Veri çekme başarılı: 5 bar
   Son fiyat: 124.50
   Son hacim: 15,234,567

======================================================================
📈 TEST 4: İndikatör Hesaplama Test Ediliyor...
======================================================================
✅ Veri hazır: 250 bar
✅ İndikatör hesaplama başarılı: 12 indikatör
   RSI_14: 58.45
   SMA_20: 122.30
   MACD: 1.25

======================================================================
🎯 TEST 5: Sinyal Üretimi Test Ediliyor...
======================================================================

📊 GARAN.IS için veri çekiliyor...
✅ Veri kaydedildi: 250 bar
✅ İndikatörler kaydedildi: 3000 kayıt

✅ Sinyal üretildi:
   Sinyal: BUY
   Skor: 72.5
   Trend: BUY
   Momentum: BUY
   Volatilite: HOLD

======================================================================
🛡️  TEST 6: Risk Yönetimi Test Ediliyor...
======================================================================
✅ RiskManager oluşturuldu
✅ Pozisyon kontrolü: True - OK
✅ Pozisyon büyüklüğü: 75 adet, 7500.00 TL
✅ Pozisyon açıldı: GARAN.IS BUY 75 @ 100

📊 Portföy İstatistikleri:
   Toplam Sermaye: 100,000.00 TL
   Nakit: 92,500.00 TL
   Pozisyonlar: 1

======================================================================
🤖 TEST 7: Live Trading Engine Test Ediliyor...
======================================================================
✅ LiveTradingEngine import edildi

======================================================================
🤖 LIVE TRADING ENGINE - PAPER MODE
======================================================================
Mod              : PAPER
Başlangıç Sermaye: 100,000.00 TL
Hisse Sayısı     : 1
Timeframe'ler    : 1d
Güncelleme Aralığı: 60 saniye
Log Dosyası      : live_trading_paper_20251026_143022.log
======================================================================

✅ LiveTradingEngine oluşturuldu
   Mod: paper
   Hisse Sayısı: 1
   Timeframe'ler: 1d

================================================================================
📊 TEST SONUÇLARI
================================================================================
✅ Import'lar                    - BAŞARILI
✅ Veritabanı                    - BAŞARILI
✅ Veri Toplama                  - BAŞARILI
✅ İndikatörler                  - BAŞARILI
✅ Sinyal Üretimi                - BAŞARILI
✅ Risk Yönetimi                 - BAŞARILI
✅ Live Trading Engine           - BAŞARILI

================================================================================
📈 TOPLAM: 7/7 test geçti (100.0%)
================================================================================

🎉 TÜM TESTLER BAŞARILI! Sistem çalışmaya hazır!

💡 Sistemi başlatmak için:
   python run_live_trading.py --mode paper --max-stocks 5
```

## Hata Durumunda

### TA-Lib Hatası

```
❌ talib: No module named 'talib'
   ⚠️  TA-Lib kurulu değil. WINDOWS_TALIB_INSTALL.md dosyasına bakın.
```

**Çözüm**: `WINDOWS_TALIB_INSTALL.md` dosyasındaki adımları takip edin.

### İnternet Bağlantısı Hatası

```
❌ Veri çekme başarısız
```

**Çözüm**: İnternet bağlantınızı kontrol edin.

### Import Hatası

```
❌ DatabaseManager: No module named 'database'
```

**Çözüm**: Doğru dizinde olduğunuzdan emin olun:
```powershell
cd C:\Users\Botai\ClaudeCode
```

## Hızlı Sorun Giderme

```powershell
# 1. Kütüphaneleri kontrol et
pip list | findstr "yfinance pandas numpy"

# 2. TA-Lib'i kontrol et
python -c "import talib; print('TA-Lib OK')"

# 3. Dizini kontrol et
cd C:\Users\Botai\ClaudeCode
dir run_live_trading.py

# 4. Testi çalıştır
python test_system.py
```

## Test Başarılı Olduktan Sonra

Sistem çalışmaya hazır! Şimdi live trading'i başlatabilirsiniz:

```powershell
# Hızlı test (5 hisse)
python run_live_trading.py --mode paper --max-stocks 5 --interval 300

# Tam sistem (20 hisse)
python run_live_trading.py --mode paper --max-stocks 20 --interval 300

# Monitoring
python run_monitor.py --dashboard
```

## Otomatik Test (CI/CD)

Test scripti exit code döndürür:
- `0`: Tüm testler başarılı
- `1`: En az bir test başarısız

```bash
# Script ile otomatik test
python test_system.py
if [ $? -eq 0 ]; then
    echo "Testler başarılı, deployment yapılabilir"
else
    echo "Testler başarısız, deployment yapılamaz"
fi
```

## İpuçları

1. **İlk test uzun sürebilir**: İlk çalıştırmada veri indiriliyor
2. **İnternet gereklidir**: yfinance canlı veri çeker
3. **TA-Lib şart**: Tüm testler için TA-Lib kurulu olmalı
4. **Hata logları**: Her test detaylı hata mesajı ve stack trace gösterir

## Yardım

- **WINDOWS_TALIB_INSTALL.md**: TA-Lib kurulum rehberi
- **WINDOWS_QUICK_START.md**: Windows hızlı başlangıç
- **live_trading/README.md**: Genel dokümantasyon

---

**Test et, kontrol et, başlat!** 🚀
