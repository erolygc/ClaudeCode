# Live Trading - Hızlı Başlangıç Rehberi

## 🚀 5 Dakikada Başlayın

### 1. Gerekli Klasörleri Oluşturun

```bash
cd /home/user/ClaudeCode
mkdir -p logs
```

### 2. Paper Trading'i Başlatın (Test Modu)

```bash
# En basit kullanım
python3 run_live_trading.py --mode paper

# Veya özelleştirilmiş
python3 run_live_trading.py --mode paper --capital 50000 --max-stocks 20 --interval 300
```

### 3. Monitoring Dashboard'u Açın (Başka bir terminal'de)

```bash
# Canlı dashboard
python3 run_monitor.py --dashboard
```

### 4. Çalışmasını İzleyin

Sistem otomatik olarak:
- ✅ Hisse fiyatlarını çeker
- ✅ İndikatörleri hesaplar
- ✅ Sinyaller üretir
- ✅ Otomatik işlem yapar (paper trading)
- ✅ Pozisyonları yönetir

### 5. Durdurmak İçin

`Ctrl+C` tuşlarına basın

---

## 📊 Ne Beklemeli?

### İlk Döngü (~30 saniye)
```
🔄 DÖNGÜ #1 BAŞLIYOR...
📊 Timeframe: 1d
✅ 100 hisse için veri çekiliyor...
✅ İndikatörler hesaplanıyor...
✅ Sinyaller üretiliyor...
```

### Sinyal Geldiğinde
```
🟢 GARAN.IS    | BUY  | Skor:  72.5 | Fiyat:   124.50
✅ Pozisyon açıldı: GARAN.IS BUY 80 @ 124.50 TL
   SL: 118.28 | TP: 143.18 | Tutar: 9960.00 TL
```

### Portföy Özeti
```
📊 PORTFÖY ÖZETİ
======================================================================
Toplam Sermaye    : 100,240.00 TL
Nakit             : 89,840.00 TL
Pozisyon Değeri   : 10,400.00 TL
Açık Pozisyonlar  : 1/10
----------------------------------------------------------------------
Günlük PnL        : +240.00 TL (1 işlem)
Toplam PnL        : +240.00 TL (1 işlem)
Toplam Getiri     : +0.24%
======================================================================
```

---

## ⚙️ Yaygın Kullanım Senaryoları

### Hızlı Test (5 Hisse, 5 Dakika)
```bash
python3 run_live_trading.py \
    --mode paper \
    --max-stocks 5 \
    --interval 300 \
    --capital 10000
```

### Konservat if Mod (Günlük, Az Hisse)
```bash
python3 run_live_trading.py \
    --mode paper \
    --timeframes 1d \
    --max-stocks 10 \
    --interval 3600 \
    --capital 50000 \
    --position-size 0.05
```

### Agresif Mod (Çoklu Timeframe, Çok Hisse)
```bash
python3 run_live_trading.py \
    --mode paper \
    --timeframes 1d,1h \
    --max-stocks 50 \
    --interval 600 \
    --capital 200000 \
    --position-size 0.15
```

---

## 🔄 Sürekli Çalıştırma (Systemd)

### 1. Servisi Kur

```bash
# Servisi kopyala
sudo cp systemd/live-trading.service /etc/systemd/system/

# Servisi aktifleştir
sudo systemctl daemon-reload
sudo systemctl enable live-trading
sudo systemctl start live-trading
```

### 2. Durumu Kontrol Et

```bash
# Servis durumu
sudo systemctl status live-trading

# Canlı loglar
sudo journalctl -u live-trading -f
```

### 3. Durdur/Başlat

```bash
sudo systemctl stop live-trading     # Durdur
sudo systemctl start live-trading    # Başlat
sudo systemctl restart live-trading  # Yeniden başlat
```

---

## 📈 Monitoring

### Dashboard (Canlı)
```bash
# Her 60 saniyede yenilenir
python3 run_monitor.py --dashboard

# Daha hızlı (30 saniye)
python3 run_monitor.py --dashboard --refresh 30
```

### Rapor Export
```bash
# Son 24 saatin raporu
python3 run_monitor.py --export

# Son 7 günün raporu
python3 run_monitor.py --export --hours 168
```

---

## ❓ Sık Sorulan Sorular

### Gerçek para kaybedebilir miyim?
**Hayır** - Paper trading modunda gerçek para riski yoktur. Sadece simülasyon yapar.

### Live mode ne zaman kullanılmalı?
**ÇOK DİKKATLİ** - Live mode gerçek para riski taşır. Broker API entegrasyonu gereklidir. Önce paper trading ile iyice test edin.

### Kaç hisse ile başlamalıyım?
**Öneri**: İlk test için 5-10 hisse, sonra 20-30 hisse, deneyim kazandıkça artırın.

### Hangi timeframe'i kullanmalıyım?
**Öneri**: Günlük (1d) ile başlayın. Daha sonra saatlik (1h) ekleyebilirsiniz.

### Ne kadar sermaye ile başlamalıyım?
**Paper trading**: 50,000-100,000 TL simülasyon
**Live trading**: Kaybetmeyi göze alabileceğiniz miktar (10,000 TL önerilir)

### Sistemin çalıştığını nasıl anlarım?
Log dosyalarını ve monitoring dashboard'u kontrol edin. Her döngü sonunda özet yazdırılır.

---

## 🛠️ Sorun Giderme

### Veri çekilemiyor
```bash
# İnternet bağlantısını kontrol et
ping yahoo.com

# yfinance'i güncelle
pip3 install --upgrade yfinance
```

### Pozisyon açılmıyor
- Sinyal skoru 60'ın üzerinde mi? (logları kontrol et)
- Maksimum pozisyon sayısına ulaşıldı mı? (portföy özetine bak)
- Sermaye yeterli mi?

### Servis başlamıyor
```bash
# Logları kontrol et
sudo journalctl -u live-trading -n 50

# Manuel test et
python3 run_live_trading.py --mode paper --max-stocks 1
```

---

## 🎯 Önerilen Başlangıç

1. **İlk 1 Gün**: 5 hisse, 5 dakika interval, paper trading
2. **1 Hafta**: 20 hisse, 5 dakika interval, paper trading
3. **1 Ay**: 50 hisse, 5 dakika interval, paper trading
4. **Live'a Geçiş**: Sadece sistemi çok iyi anladıktan ve karlı sonuçlar aldıktan sonra

---

## 📞 Yardım

- **README**: `live_trading/README.md` - Detaylı dokümantasyon
- **Loglar**: `logs/` klasörü - Hata ayıklama için
- **Monitor**: `python3 run_monitor.py` - Sistem durumu

---

**Başarılar!** 🚀
