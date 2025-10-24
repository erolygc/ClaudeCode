# Geliştirme ve Sistem Kontrolü Kılavuzu

Bu kılavuz, trading sistemini nasıl kontrol edeceğinizi ve geliştireceğinizi açıklar.

## 📋 İçindekiler

1. [Sistem Kontrolü](#sistem-kontrolü)
2. [Geliştirme Araçları](#geliştirme-araçları)
3. [Veritabanı Yönetimi](#veritabanı-yönetimi)
4. [Test ve Debug](#test-ve-debug)
5. [Performans Optimizasyonu](#performans-optimizasyonu)
6. [Yeni Özellik Ekleme](#yeni-özellik-ekleme)

---

## 🔍 Sistem Kontrolü

### Sistem Durumu Kontrolü

Sistemin sağlıklı çalışıp çalışmadığını kontrol etmek için:

```bash
python tools/system_status.py
```

Bu komut şunları kontrol eder:
- ✅ Database bağlantısı
- ✅ Veri kalitesi (bar sayıları, tarih aralıkları)
- ✅ İndikatör hesaplamaları
- ✅ Sinyal üretimi
- ✅ Query performansı
- ✅ Database index'leri

**Çıktı örneği:**
```
================================================================================
🔍 SİSTEM DURUMU KONTROLÜ
================================================================================
📅 Tarih: 2025-10-24 19:29:32

📁 DATABASE KONTROLÜ
✅ Database dosyası: trading_data.db
   Boyut: 8.07 MB
✅ Database bağlantısı: OK

📊 VERİ KALİTESİ KONTROLÜ
📈 Toplam hisse sayısı: 3
📊 Toplam OHLCV bar: 2,700
...

📋 ÖZET
✅ Sistem durumu: MÜKEMMEL!
```

---

## 🛠️ Geliştirme Araçları

### 1. Database Query Helper

Veritabanındaki verileri hızlıca incelemek için:

#### Genel İstatistikler
```bash
python tools/query_db.py --stats
```

#### Tüm Hisseleri Listele
```bash
python tools/query_db.py --list
```

#### OHLCV Verisi Göster
```bash
python tools/query_db.py --ticker GARAN.IS --timeframe 1d --last 10
```

#### İndikatörleri Göster
```bash
# Tüm indikatörler
python tools/query_db.py --indicators --ticker GARAN.IS --timeframe 1d --last 5

# Belirli indikatörler
python tools/query_db.py --indicators --ticker GARAN.IS --timeframe 1d \
  --indicator-names RSI_14 SMA_20 SMA_50 --last 10
```

#### Sinyalleri Göster
```bash
# Tüm sinyaller
python tools/query_db.py --signals --last 20

# Belirli bir hisse için
python tools/query_db.py --signals --ticker GARAN.IS --last 10
```

### 2. VS Code Debugging

Projeyi VS Code'da açtıktan sonra, F5 tuşuna basarak debug modunu başlatabilirsiniz.

**Hazır Debug Konfigürasyonları:**
- **FAZ 6: Data Collection** - Veri toplama sürecini debug et
- **FAZ 7: Calculate Indicators** - İndikatör hesaplamalarını debug et
- **FAZ 8: Generate Signals** - Sinyal üretimini debug et
- **FAZ 9: Run Backtest** - Backtest sürecini debug et
- **Create Sample Data** - Örnek veri oluşturmayı debug et

**Breakpoint Kullanımı:**
1. Kodda bir satıra tıklayın (sol tarafta kırmızı nokta)
2. F5 ile debug başlatın
3. F10: Adım adım ilerle
4. F11: Fonksiyonun içine gir
5. Shift+F11: Fonksiyondan çık

---

## 💾 Veritabanı Yönetimi

### Veritabanı Konumu
```
trading_data.db
```

### Direct SQL Sorguları

SQLite komut satırı aracını kullanarak:

```bash
sqlite3 trading_data.db
```

**Yaygın Sorgular:**

```sql
-- Toplam bar sayısı
SELECT COUNT(*) FROM ohlcv_data;

-- Hisse başına bar sayısı
SELECT ticker, timeframe, COUNT(*) as count
FROM ohlcv_data
GROUP BY ticker, timeframe;

-- En son 10 sinyal
SELECT * FROM signals
ORDER BY created_at DESC
LIMIT 10;

-- Belirli bir hissenin tüm indikatörleri
SELECT date, indicator_name, value
FROM indicators
WHERE ticker = 'GARAN.IS' AND timeframe = '1d'
ORDER BY date DESC
LIMIT 100;

-- Çıkış
.quit
```

### Veritabanı Yedekleme

```bash
# Yedek oluştur
cp trading_data.db trading_data_backup_$(date +%Y%m%d).db

# Windows PowerShell
Copy-Item trading_data.db -Destination "trading_data_backup_$(Get-Date -Format 'yyyyMMdd').db"
```

### Veritabanı Temizleme

```bash
# Tüm veriyi sil (DİKKATLİ!)
python
>>> from database.db_manager import DatabaseManager
>>> import sqlite3
>>> conn = sqlite3.connect('trading_data.db')
>>> cursor = conn.cursor()
>>> cursor.execute("DELETE FROM ohlcv_data")
>>> cursor.execute("DELETE FROM indicators")
>>> cursor.execute("DELETE FROM signals")
>>> conn.commit()
>>> conn.close()
```

---

## 🧪 Test ve Debug

### Sample Data Oluşturma

Test için örnek veri oluşturmak:

```bash
python create_sample_data.py
```

Bu komut:
- 3 hisse için veri oluşturur (GARAN.IS, THYAO.IS, EREGL.IS)
- 1d ve 1h timeframe'ler için
- İndikatörleri hesaplar
- Sinyalleri üretir

### Manuel Test Senaryoları

#### 1. Veri Toplama Testi
```bash
python collect_data.py
```

#### 2. İndikatör Hesaplama Testi
```bash
python calculate_indicators.py
```

#### 3. Sinyal Üretimi Testi
```bash
python generate_signals.py
```

#### 4. Backtest Testi
```bash
python backtest_all.py
```

### Performans Testi

İndikatör hesaplama performansını test etmek:

```bash
time python calculate_indicators.py

# Windows PowerShell
Measure-Command { python calculate_indicators.py }
```

**Beklenen Performans:**
- ~65,000 indikatör/saniye (optimized bulk INSERT)
- <1 saniye toplam süre (3 hisse, 2 timeframe için)

---

## ⚡ Performans Optimizasyonu

### Mevcut Optimizasyonlar

1. **Bulk INSERT** (65x hız artışı)
   - `db_manager.py:add_indicator_values_bulk()`
   - Tek seferde tüm indikatörleri kaydet

2. **Database Indexes** (10x query hızı)
   - `idx_ohlcv_ticker_timeframe`
   - `idx_indicators_ticker_timeframe`
   - `idx_signals_ticker_timeframe`

3. **NumPy Vectorization**
   - Tüm indikatör hesaplamaları vektörize

### Yeni Optimizasyon Fırsatları

#### 1. Parallel Processing

Birden fazla hisse için paralel işlem:

```python
from multiprocessing import Pool

def process_ticker(ticker):
    # İndikatör hesapla + sinyal üret
    pass

with Pool(processes=4) as pool:
    pool.map(process_ticker, tickers)
```

#### 2. Caching

Sık kullanılan veri için cache:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_ohlcv(ticker, timeframe):
    return db.get_ohlcv_data(ticker, timeframe)
```

#### 3. Database Optimization

PostgreSQL'e geçiş için:
- Daha hızlı query performansı
- Concurrent access
- Advanced indexing

---

## 🚀 Yeni Özellik Ekleme

### 1. Yeni İndikatör Ekleme

**Adım 1:** İndikatörü tanımla (`indicators/technical_indicators.py`)

```python
def calculate_new_indicator(self):
    """Yeni indikatör hesapla"""
    # Hesaplama
    values = ...  # NumPy array

    # Sonucu ekle
    self.indicators['NEW_IND_NAME'] = values
    return values
```

**Adım 2:** `calculate_all()` metoduna ekle

```python
def calculate_all(self):
    # ...
    self.calculate_new_indicator()
    # ...
```

**Adım 3:** Test et

```bash
python calculate_indicators.py
python tools/query_db.py --indicators --ticker GARAN.IS --timeframe 1d \
  --indicator-names NEW_IND_NAME
```

### 2. Yeni Sinyal Stratejisi Ekleme

**Adım 1:** Stratejiyi tanımla (`signals/signal_generator.py`)

```python
def new_strategy_signal(self, df, indicators):
    """Yeni strateji sinyali"""
    score = 50  # Nötr başla

    # Sinyal mantığı
    if ...:
        score += 10

    return self._interpret_score(score), score
```

**Adım 2:** `generate_signals()` metoduna ekle

```python
def generate_signals(self, ticker, timeframe):
    # ...
    new_signal, new_score = self.new_strategy_signal(df, indicators)
    signals.append((new_signal, new_score, "New Strategy"))
    # ...
```

**Adım 3:** Test et

```bash
python generate_signals.py
python tools/query_db.py --signals --last 10
```

### 3. Yeni Veri Kaynağı Ekleme

**Adım 1:** Data collector güncelle (`data/data_collector.py`)

```python
class NewDataSource:
    def fetch_data(self, ticker, timeframe, start_date, end_date):
        # Veri toplama mantığı
        pass
```

**Adım 2:** Test et

```bash
python collect_data.py
python tools/query_db.py --ticker NEWSTOCK --timeframe 1d
```

---

## 📝 Geliştirme Best Practices

### 1. Git Workflow

```bash
# Yeni feature branch oluştur
git checkout -b feature/yeni-ozellik

# Değişiklikleri commit et
git add .
git commit -m "Add: Yeni özellik açıklaması"

# Push et
git push -u origin feature/yeni-ozellik
```

### 2. Code Style

- **PEP 8** standartlarına uy
- **Type hints** kullan
- **Docstrings** yaz
- **Meaningful variable names** kullan

**Örnek:**

```python
def calculate_rsi(self, period: int = 14) -> np.ndarray:
    """
    RSI (Relative Strength Index) hesapla

    Args:
        period: RSI periyodu (varsayılan: 14)

    Returns:
        np.ndarray: RSI değerleri (0-100 arası)
    """
    # Hesaplama...
    pass
```

### 3. Error Handling

```python
try:
    # Riskli işlem
    result = some_operation()
except SpecificException as e:
    print(f"❌ Hata: {e}")
    # Hata yönetimi
finally:
    # Temizlik
    pass
```

### 4. Testing

```python
# Test dosyası: tests/test_indicators.py
import unittest
from indicators.technical_indicators import TechnicalIndicators

class TestTechnicalIndicators(unittest.TestCase):
    def test_rsi_calculation(self):
        # Test mantığı
        pass
```

---

## 🔧 Yaygın Sorunlar ve Çözümler

### Problem: "No module named 'database'"

**Çözüm:**
```bash
# Proje kök dizininden çalıştır
cd /path/to/ClaudeCode
python tools/system_status.py
```

### Problem: Database locked

**Çözüm:**
```bash
# Tüm Python süreçlerini kapat
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill python
```

### Problem: Yavaş performans

**Çözüm:**
1. Database index'lerini kontrol et
2. Bulk INSERT kullan
3. Query optimizasyonu yap

---

## 📚 Kaynaklar

- **Python Documentation**: https://docs.python.org/3/
- **pandas Documentation**: https://pandas.pydata.org/docs/
- **NumPy Documentation**: https://numpy.org/doc/
- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **TA-Lib Documentation**: https://ta-lib.github.io/ta-lib-python/

---

## 🎯 Sonraki Adımlar

1. ✅ Sistem durumu kontrolü yap
2. ✅ Veritabanı verilerini incele
3. 🔄 Yeni indikatör ekle
4. 🔄 Yeni strateji geliştir
5. 🔄 Backtesting iyileştir
6. 🔄 Azure deployment yap

---

**İyi geliştirmeler!** 🚀
