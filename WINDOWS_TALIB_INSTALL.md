# Windows TA-Lib Kurulum Rehberi

## Sorun

Windows'ta `pip install ta-lib-binary` çalışmıyor çünkü bu paket Linux içindir.

## Çözüm (3 Seçenek)

### Seçenek 1: Önceden Derlenmiş Wheel Dosyası (ÖNERİLEN) ⭐

1. **Python versiyonunuzu kontrol edin:**
   ```powershell
   python --version
   # Örnek: Python 3.11.9
   ```

2. **Bilgisayar mimarisini kontrol edin:**
   ```powershell
   python -c "import platform; print(platform.machine())"
   # Örnek: AMD64 (64-bit) veya x86 (32-bit)
   ```

3. **Uygun wheel dosyasını indirin:**

   Aşağıdaki linkten Python versiyonunuza uygun wheel dosyasını indirin:

   **https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib**

   Örnek dosya isimleri:
   - Python 3.11, 64-bit: `TA_Lib-0.4.28-cp311-cp311-win_amd64.whl`
   - Python 3.10, 64-bit: `TA_Lib-0.4.28-cp310-cp310-win_amd64.whl`
   - Python 3.9, 64-bit: `TA_Lib-0.4.28-cp39-cp39-win_amd64.whl`

4. **İndirdiğiniz wheel dosyasını kurun:**
   ```powershell
   # İndirme klasörüne gidin
   cd C:\Users\Botai\Downloads

   # Wheel dosyasını kurun (dosya adını kendi indirdiğinizle değiştirin)
   pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
   ```

5. **Kurulumu test edin:**
   ```powershell
   python -c "import talib; print('TA-Lib kuruldu!')"
   ```

---

### Seçenek 2: Ta-Lib C Library Manuel Kurulum

1. **TA-Lib C library'yi indirin:**
   - https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-msvc.zip/download

2. **Zip'i açın ve C:\ta-lib klasörüne kopyalayın**

3. **Visual Studio Build Tools kurun:**
   - https://visualstudio.microsoft.com/downloads/
   - "Build Tools for Visual Studio" seçin
   - C++ build tools'u seçin ve kurun

4. **TA-Lib Python paketini kurun:**
   ```powershell
   pip install TA-Lib
   ```

---

### Seçenek 3: Alternatif - TA-Lib olmadan çalıştır (GEÇİCİ ÇÖZÜM)

Eğer TA-Lib kurulumu çok sorun çıkarıyorsa, pandas-ta kullanabilirsiniz:

```powershell
pip install pandas-ta
```

Ancak bu durumda `indicators/technical_indicators.py` dosyasını düzenlemeniz gerekir.

---

## Hızlı Test İçin (TA-Lib Olmadan)

Sistemin çalışıp çalışmadığını test etmek için geçici olarak TA-Lib'i atlayabilirsiniz:

```powershell
# Basit indikatör testi
python -c "import pandas as pd; print('Pandas OK')"
python -c "import numpy as np; print('Numpy OK')"
python -c "import yfinance as yf; print('yfinance OK')"
```

---

## Önerilen: En Kolay Yol (Sizin için)

**Python 3.11.9, 64-bit için:**

1. **Wheel dosyasını indirin:**
   ```
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   ```

   Arayın: `TA_Lib-0.4.28-cp311-cp311-win_amd64.whl`

2. **İndirdiğiniz dosyayı kurun:**
   ```powershell
   cd C:\Users\Botai\Downloads
   pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
   ```

3. **Test edin:**
   ```powershell
   python -c "import talib; print('TA-Lib kuruldu!')"
   ```

4. **Sistemi çalıştırın:**
   ```powershell
   cd C:\Users\Botai\ClaudeCode
   python run_live_trading.py --mode paper --max-stocks 5
   ```

---

## Sorun Çözümü

### "Microsoft Visual C++ 14.0 is required" hatası
- Visual Studio Build Tools kurun: https://visualstudio.microsoft.com/downloads/

### "error: command 'cl.exe' failed"
- Wheel dosyası kullanın (Seçenek 1)

### "ImportError: DLL load failed"
- Visual C++ Redistributable kurun: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Alternatif: Docker Kullanımı

Eğer Windows'ta kurulum çok sorunlu olursa, Docker ile Linux container'da çalıştırabilirsiniz:

```powershell
docker pull python:3.11
docker run -it -v C:\Users\Botai\ClaudeCode:/app python:3.11 bash
cd /app
pip install -r requirements.txt
python run_live_trading.py --mode paper
```

---

**TA-Lib Kurulduktan Sonra:**

```powershell
cd C:\Users\Botai\ClaudeCode
python run_live_trading.py --mode paper --max-stocks 5 --interval 300
```

Başarılar! 🚀
