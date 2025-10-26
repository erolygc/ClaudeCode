# Live Trading System - Profesyonel Otomatik Hisse Senedi İşlem Sistemi

## Genel Bakış

Bu sistem, teknik analiz tabanlı otomatik hisse senedi alım-satım işlemleri yapan profesyonel bir live trading motorudur.

### Özellikler

- ✅ **Paper Trading**: Gerçek para riski olmadan test modu
- ✅ **Live Trading**: Gerçek işlem desteği (broker entegrasyonu gerekli)
- ✅ **Risk Yönetimi**: Otomatik stop loss, take profit, pozisyon limitleri
- ✅ **Multi-Timeframe Analiz**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
- ✅ **25+ Teknik İndikatör**: SMA, EMA, RSI, MACD, Bollinger Bands, ADX, vb.
- ✅ **Otomatik Sinyal Üretimi**: Trend, momentum ve volatilite analizi
- ✅ **Real-time Monitoring**: Canlı dashboard ve raporlama
- ✅ **Systemd Servis**: Sürekli çalışma ve otomatik yeniden başlatma
- ✅ **Logging**: Detaylı işlem ve hata logları

## Kurulum

### 1. Gereksinimler

```bash
python3 --version  # Python 3.8+
pip3 install -r requirements.txt
```

### 2. Dizin Yapısı

```
ClaudeCode/
├── live_trading/
│   ├── live_engine.py        # Ana trading motoru
│   ├── risk_manager.py       # Risk yönetimi
│   ├── monitor.py            # Monitoring sistemi
│   ├── config.py             # Konfigürasyon
│   └── README.md             # Bu dosya
├── run_live_trading.py       # Başlatıcı script
├── run_monitor.py            # Monitor script
├── systemd/
│   └── live-trading.service  # Systemd servis dosyası
└── logs/                     # Log dosyaları (otomatik oluşur)
```

### 3. Log Klasörü Oluştur

```bash
mkdir -p logs
```

## Kullanım

### Paper Trading (Test Modu)

Gerçek para riski olmadan test edin:

```bash
# Basit başlatma - 100,000 TL ile, 5 dakikada bir güncelleme
python run_live_trading.py --mode paper

# Özelleştirilmiş - 50,000 TL, 30 hisse, 1 saat aralık
python run_live_trading.py --mode paper --capital 50000 --max-stocks 30 --interval 3600

# Sadece günlük timeframe
python run_live_trading.py --mode paper --timeframes 1d

# Hızlı test - 5 hisse, 5 dakikada bir
python run_live_trading.py --mode paper --max-stocks 5 --interval 300
```

### Live Trading (Gerçek İşlem)

⚠️ **DİKKAT**: Gerçek para riski vardır!

```bash
# Gerçek işlem modu
python run_live_trading.py --mode live --capital 10000 --timeframes 1d
```

### Parametreler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `--mode` | Trading modu (paper/live) | paper |
| `--capital` | Başlangıç sermayesi (TL) | 100000 |
| `--interval` | Güncelleme aralığı (saniye) | 300 |
| `--timeframes` | Timeframe listesi (virgülle ayrılmış) | 1d |
| `--max-stocks` | Maksimum hisse sayısı | Hepsi |
| `--max-positions` | Maksimum eş zamanlı pozisyon | 10 |
| `--position-size` | Pozisyon büyüklüğü (%0.10 = %10) | 0.10 |
| `--stop-loss` | Stop loss yüzdesi | 0.05 (%5) |
| `--take-profit` | Take profit yüzdesi | 0.15 (%15) |

## Monitoring

### Canlı Dashboard

```bash
# Her 60 saniyede güncellenir
python run_monitor.py --dashboard

# Daha hızlı güncelleme (30 saniye)
python run_monitor.py --dashboard --refresh 30
```

Dashboard şunları gösterir:
- Sinyal dağılımı (BUY/SELL/HOLD)
- En yüksek skorlu sinyaller
- Veri güncellik durumu
- Aktif hisse sayısı

### Rapor Export

```bash
# Son 24 saatin raporu
python run_monitor.py --export

# Son 48 saatin raporu
python run_monitor.py --export --hours 48
```

## Systemd Servisi (Sürekli Çalışma)

### 1. Servisi Kur

```bash
# Servisi kopyala
sudo cp systemd/live-trading.service /etc/systemd/system/

# Kullanıcı adını düzenle (gerekirse)
sudo nano /etc/systemd/system/live-trading.service

# Servisi yenile
sudo systemctl daemon-reload
```

### 2. Servisi Yönet

```bash
# Servisi başlat
sudo systemctl start live-trading

# Servisi durdur
sudo systemctl stop live-trading

# Servisi yeniden başlat
sudo systemctl restart live-trading

# Durumu kontrol et
sudo systemctl status live-trading

# Otomatik başlatmayı aktifleştir
sudo systemctl enable live-trading

# Logları takip et
sudo journalctl -u live-trading -f
```

### 3. Servis Ayarları

`/etc/systemd/system/live-trading.service` dosyasını düzenleyin:

```ini
# Paper trading için (varsayılan)
ExecStart=/usr/bin/python3 /home/user/ClaudeCode/run_live_trading.py --mode paper --capital 100000 --interval 300

# Live trading için (DİKKAT!)
ExecStart=/usr/bin/python3 /home/user/ClaudeCode/run_live_trading.py --mode live --capital 10000 --interval 300
```

Değiştirdikten sonra:
```bash
sudo systemctl daemon-reload
sudo systemctl restart live-trading
```

## Risk Yönetimi

Sistem otomatik olarak şu kontrolleri yapar:

### Pozisyon Kontrolü
- Maksimum pozisyon sayısı (varsayılan: 10)
- Pozisyon başına maksimum sermaye (%10)
- Aynı hisse için çift pozisyon engelleme

### Zarar Kontrolü
- Otomatik stop loss (%5)
- Otomatik take profit (%15)
- Günlük maksimum kayıp (%3)

### Sinyal Filtreleme
- Minimum sinyal skoru (60/100)
- Multi-timeframe onay
- Volume ve volatilite kontrolü

## Çalışma Mantığı

### 1. Güncelleme Döngüsü

```
┌─────────────────────────────────────┐
│   Güncelleme Döngüsü Başla          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Her timeframe için:                │
│   ├─ Veri çek (yfinance)             │
│   ├─ İndikatörleri hesapla           │
│   ├─ Sinyal üret                     │
│   └─ İşlem yap (BUY/SELL)            │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Pozisyonları güncelle              │
│   ├─ Fiyatları kontrol et            │
│   ├─ Stop loss / Take profit         │
│   └─ Gerekirse kapat                 │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Rapor yazdır                       │
│   ├─ Portföy özeti                   │
│   ├─ PnL                             │
│   └─ Açık pozisyonlar                │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Bekle (interval kadar)             │
└─────────────┬───────────────────────┘
              │
              └──────────► (Tekrar)
```

### 2. Sinyal Üretimi

```python
# Her hisse için:
1. Trend analizi (40% ağırlık)
   - SMA crossover
   - MACD
   - ADX

2. Momentum analizi (30% ağırlık)
   - RSI
   - Stochastic
   - Williams %R

3. Volatilite analizi (15% ağırlık)
   - Bollinger Bands
   - ATR

4. Kombine skor (0-100)
   - >= 60: BUY
   - <= 40: SELL
   - 40-60: HOLD
```

## Log Dosyaları

Sistem otomatik olarak log dosyaları oluşturur:

```
logs/
├── live_trading_paper_YYYYMMDD_HHMMSS.log  # Ana log
└── live-trading-error.log                  # Hata logları (systemd)
```

Log formatı:
```
[2025-10-26 14:30:15] 🔄 DÖNGÜ #42 BAŞLIYOR...
[2025-10-26 14:30:16] 📊 Timeframe: 1d
[2025-10-26 14:30:18] 🟢 GARAN.IS    | BUY  | Skor:  72.5 | Fiyat:   124.50
[2025-10-26 14:30:18] ✅ GARAN.IS BUY pozisyon açıldı @ 124.50 TL (Skor: 72.5)
```

## Güvenlik ve Uyarılar

### ⚠️ ÖNEMLİ UYARILAR

1. **Paper Trading ile Başlayın**: Önce test modunda çalıştırın
2. **Gerçek Para Riski**: Live modda gerçek para kaybedebilirsiniz
3. **Broker Entegrasyonu**: Şu anda gerçek işlem broker API'si yok
4. **İnternet Bağlantısı**: Sürekli internet gereklidir
5. **Piyasa Saatleri**: BIST piyasa saatleri 10:00-18:00
6. **Yasal Sorumluluk**: Kayıplardan kullanıcı sorumludur

### Önerilen Güvenlik Ayarları

```python
# live_trading/config.py dosyasında:

SECURITY_SETTINGS = {
    'require_confirmation': True,     # İşlem onayı
    'max_loss_shutdown': 0.10,        # %10 kayıpta otomatik durdur
    'daily_loss_limit': 5000,         # Günlük 5000 TL kayıp limiti
}
```

## Troubleshooting

### Problem: Veri çekilemiyor

```bash
# yfinance güncel mi?
pip3 install --upgrade yfinance

# İnternet bağlantısı var mı?
ping yahoo.com
```

### Problem: Pozisyon açılmıyor

```bash
# Sinyal skorunu kontrol et (minimum 60 olmalı)
# Risk limitlerine ulaşılmış olabilir
# Log dosyasına bakın
```

### Problem: Servis başlamıyor

```bash
# Logları kontrol et
sudo journalctl -u live-trading -n 50

# Python path doğru mu?
which python3

# Dosya yolu doğru mu?
ls -la /home/user/ClaudeCode/run_live_trading.py
```

## Gelişmiş Özellikler (Yakında)

- [ ] Telegram/E-posta bildirimleri
- [ ] Broker API entegrasyonu (Enpara, İş Yatırım, vb.)
- [ ] Machine learning tabanlı sinyal üretimi
- [ ] Backtesting entegrasyonu
- [ ] Web dashboard
- [ ] Mobile app
- [ ] Çoklu strateji desteği
- [ ] Portfolio optimization

## Destek ve İletişim

- **GitHub Issues**: Hata bildirimleri ve öneriler için
- **Dokümantasyon**: Bu README dosyası
- **Log Dosyaları**: Sorun giderme için logları inceleyin

## Lisans ve Sorumluluk Reddi

Bu yazılım "OLDUĞU GİBİ" sağlanmaktadır. Kullanımdan doğabilecek maddi/manevi zararlardan yazılım geliştiricisi sorumlu değildir. Gerçek para ile işlem yapmadan önce sistemi test modunda çalıştırmanız şiddetle tavsiye edilir.

---

**Son Güncelleme**: 2025-10-26
**Versiyon**: 1.0.0
