# Live Trading - Windows Hızlı Başlangıç Rehberi

## 🚀 Windows'ta 5 Dakikada Başlayın

### 1. Gerekli Klasörleri Oluşturun

```powershell
# PowerShell'de çalıştırın
cd C:\Users\Botai\ClaudeCode
mkdir logs -ErrorAction SilentlyContinue
```

### 2. Python Kurulu mu Kontrol Edin

```powershell
python --version
```

Eğer Python kurulu değilse:
- https://www.python.org/downloads/ adresinden Python 3.8+ indirin
- Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

### 3. Gerekli Kütüphaneleri Kurun

```powershell
pip install yfinance pandas numpy ta-lib-binary sqlite3
```

### 4. Paper Trading'i Başlatın (Test Modu)

```powershell
# En basit kullanım
python run_live_trading.py --mode paper

# Veya özelleştirilmiş
python run_live_trading.py --mode paper --capital 50000 --max-stocks 20 --interval 300
```

### 5. Monitoring Dashboard'u Açın (Yeni PowerShell penceresinde)

```powershell
# Yeni bir PowerShell penceresi açın (Ctrl+Shift+N)
cd C:\Users\Botai\ClaudeCode
python run_monitor.py --dashboard
```

### 6. Durdurmak İçin

`Ctrl+C` tuşlarına basın

---

## 📊 Hızlı Test Komutları

### Basit Test (5 Hisse, 5 Dakika)
```powershell
python run_live_trading.py --mode paper --max-stocks 5 --interval 300
```

### Konservatif Mod
```powershell
python run_live_trading.py --mode paper --capital 50000 --max-stocks 10 --interval 600
```

### Monitoring
```powershell
# Dashboard (canlı)
python run_monitor.py --dashboard

# Rapor export
python run_monitor.py --export
```

---

## 🔧 Windows'a Özel Notlar

### Python Komutu
- ✅ Windows'ta: `python` (python3 değil!)
- ✅ Linux/Mac'te: `python3`

### Dizin Ayırıcı
- ✅ Windows: `\` (backslash) veya `/` (her ikisi de çalışır)
- ✅ Linux/Mac: `/` (forward slash)

### Temizlik (Ekran Temizleme)
- ✅ Windows: `cls`
- ✅ Linux/Mac: `clear`

---

## ⚙️ Yaygın Windows Sorunları

### Problem: "Python was not found"

**Çözüm 1**: Python'u kur
```powershell
# Python kurulu mu kontrol et
python --version

# Kurulu değilse indir:
# https://www.python.org/downloads/
```

**Çözüm 2**: PATH'e ekle
```powershell
# Windows Başlat > "Environment Variables" ara
# System Properties > Environment Variables
# PATH'e Python dizinini ekle: C:\Python311\ (veya kurulum dizininiz)
```

### Problem: "pip: command not found"

```powershell
python -m pip install --upgrade pip
```

### Problem: "Permission denied"

```powershell
# PowerShell'i Administrator olarak çalıştırın
# Sağ tık > "Run as Administrator"
```

### Problem: "Module not found"

```powershell
# Tüm gereksinimleri tekrar kur
pip install --upgrade yfinance pandas numpy ta-lib-binary
```

---

## 🎯 Windows İçin Önerilen Kurulum

### 1. Python Kur

```powershell
# Python 3.8+ indir ve kur
# https://www.python.org/downloads/

# Kurulum sırasında mutlaka işaretleyin:
# ☑ Add Python to PATH
# ☑ Install pip
```

### 2. Gerekli Kütüphaneleri Kur

```powershell
# PowerShell'i Administrator olarak aç
python -m pip install --upgrade pip
pip install yfinance pandas numpy ta-lib-binary sqlite3
```

### 3. Klasörleri Oluştur

```powershell
cd C:\Users\Botai\ClaudeCode
mkdir logs
```

### 4. İlk Testi Çalıştır

```powershell
# Hızlı test (sadece 1 hisse, 5 dakika)
python run_live_trading.py --mode paper --max-stocks 1 --interval 300
```

---

## 📈 Windows'ta Sürekli Çalıştırma

### Seçenek 1: Task Scheduler (Önerilen)

1. Windows Başlat > "Task Scheduler" ara
2. "Create Basic Task" tıkla
3. Ad: "Live Trading System"
4. Trigger: "When the computer starts" veya "At a specific time"
5. Action: "Start a program"
6. Program: `C:\Python311\python.exe` (Python yolunuzu kontrol edin)
7. Arguments: `C:\Users\Botai\ClaudeCode\run_live_trading.py --mode paper --max-stocks 20`
8. Start in: `C:\Users\Botai\ClaudeCode`

### Seçenek 2: Batch Script

`start_trading.bat` dosyası oluşturun:

```batch
@echo off
cd C:\Users\Botai\ClaudeCode
python run_live_trading.py --mode paper --capital 100000 --max-stocks 20
pause
```

Çift tıklayarak çalıştırın.

### Seçenek 3: PowerShell Script

`start_trading.ps1` dosyası oluşturun:

```powershell
Set-Location C:\Users\Botai\ClaudeCode
python run_live_trading.py --mode paper --capital 100000 --max-stocks 20
```

PowerShell'de çalıştırın:
```powershell
.\start_trading.ps1
```

---

## 🛠️ Hızlı Sorun Giderme

### Test 1: Python çalışıyor mu?
```powershell
python --version
# Beklenen: Python 3.8.x veya üzeri
```

### Test 2: Pip çalışıyor mu?
```powershell
pip --version
# Beklenen: pip 21.x.x veya üzeri
```

### Test 3: Kütüphaneler kurulu mu?
```powershell
python -c "import yfinance; print('yfinance OK')"
python -c "import pandas; print('pandas OK')"
python -c "import numpy; print('numpy OK')"
```

### Test 4: Script çalışıyor mu?
```powershell
python run_live_trading.py --help
# Beklenen: Yardım mesajı görmelisiniz
```

---

## 📞 Adım Adım İlk Çalıştırma

### Adım 1: PowerShell Aç
```
Windows Başlat > "PowerShell" yaz > Enter
```

### Adım 2: Dizine Git
```powershell
cd C:\Users\Botai\ClaudeCode
```

### Adım 3: Python Kontrol
```powershell
python --version
```
> Eğer hata verirse, Python'u kurun: https://www.python.org/downloads/

### Adım 4: Kütüphaneleri Kur
```powershell
pip install yfinance pandas numpy ta-lib-binary
```

### Adım 5: Logs Klasörü Oluştur
```powershell
mkdir logs
```

### Adım 6: İlk Testi Başlat
```powershell
python run_live_trading.py --mode paper --max-stocks 5
```

### Adım 7: Çalıştığını İzleyin
```
Birkaç dakika içinde şöyle çıktılar görmelisiniz:

🤖 LIVE TRADING ENGINE - PAPER MODE
======================================================================
Mod              : PAPER
Başlangıç Sermaye: 100,000.00 TL
...

🔄 DÖNGÜ #1 BAŞLIYOR...
📊 Timeframe: 1d
...
```

---

## 🎯 Başarı İçin İpuçları

1. **İlk test için**: 1-5 hisse, 5 dakika interval
2. **İnternet bağlantısı**: Sürekli olmalı
3. **Antivirüs**: Python'u beyaz listeye ekleyin
4. **Güvenlik Duvarı**: Python'a izin verin
5. **Loglar**: Her çalıştırmada `logs/` klasörüne bakın

---

## 📖 Daha Fazla Bilgi

- **Detaylı Dokümantasyon**: `live_trading\README.md`
- **Sorun Giderme**: `QUICK_START.md`
- **Log Dosyaları**: `logs\` klasörü

---

**Şimdi deneyin!** 🚀

```powershell
python run_live_trading.py --mode paper --max-stocks 5
```
