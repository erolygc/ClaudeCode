# 🚀 Quick Start Guide
## Trading System - 5 Dakikada Başlangıç

---

## 📦 Local Çalıştırma (Test)

### 1. Requirements

```bash
# Gerekli kütüphaneleri yükle
pip install pandas numpy ta-lib openpyxl
```

### 2. Test Verisi Oluştur

```bash
# Sample data generator (gerçek veri yerine)
python create_sample_data.py
```

**Output:**
```
📊 2,700 bar veri
📐 47,640 indikatör değeri
🎯 6 sinyal (BUY/SELL/HOLD)
```

### 3. Backtest Çalıştır

```bash
python backtest_all.py
```

---

## ☁️ Azure Deployment (Production)

### 1. Azure Login

```bash
az login
```

### 2. Email Ayarları

Gmail için App Password oluşturun:
1. Google Account → Security → 2-Step Verification (aktif et)
2. App passwords → Generate
3. "Mail" + "Other" seçin, "Trading System" yazın
4. 16 haneli şifreyi kaydet

### 3. Deploy!

```bash
# Tek komut!
./scripts/deploy_azure.sh

# Veya özel isimlerle
./scripts/deploy_azure.sh my-rg my-function-app westeurope
```

### 4. Environment Variables

Azure Portal'dan veya CLI ile:

```bash
az functionapp config appsettings set \
  --name your-function-app \
  --resource-group your-rg \
  --settings \
  SMTP_USERNAME="your-email@gmail.com" \
  SMTP_PASSWORD="your-16-digit-app-password" \
  TO_EMAILS="recipient@example.com" \
  FROM_EMAIL="your-email@gmail.com"
```

### 5. Test

```bash
# Health check
curl https://your-function-app.azurewebsites.net/api/health

# Logs izle
az functionapp log tail --name your-function-app --resource-group your-rg
```

**Beklenen sonuç:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-24T...",
  "service": "Trading System"
}
```

---

## ⏰ Otomatik Çalışma

Sistem **her iş günü (Pazartesi-Cuma) saat 18:00**'de otomatik çalışır.

**Ne yapar?**
1. 📊 BIST verilerini toplar
2. 📐 10+ teknik indikatörü hesaplar
3. 🎯 AL/SAT/BEKLE sinyalleri üretir
4. 📈 Backtest çalıştırır
5. 📧 Email raporu gönderir

**Schedule değiştirmek için:**
`azure_functions/function_app.py` → `@app.timer_trigger(schedule="...")`

```python
"0 0 18 * * 1-5"  # Pazartesi-Cuma 18:00 (varsayılan)
"0 0 15 * * 1-5"  # Türkiye saati için UTC-3 (15:00 UTC = 18:00 TR)
"0 0 9 * * 1-5"   # Sabah 09:00
"0 */30 * * * *"  # Her 30 dakikada
```

---

## 📧 Email Raporları

### Günlük Rapor Örnekleri

**Başarılı Execution:**
```
📊 Trading System Daily Report
✅ Pipeline Status: COMPLETED

📊 Phase 6: Data Collection
   2,700 Total Bars
   10/10 Success Rate

🎯 Phase 8: Signal Generation
   6 Total Signals
   🟢 1 BUY
   🔴 2 SELL
   🟡 3 HOLD

💪 Strong Signals:
   🟢 GARAN.IS (1h): BUY - 71.5/100
   🔴 EREGL.IS (1h): SELL - 31.5/100
```

**Hata Durumu:**
```
🚨 Trading System ERROR
❌ Pipeline failed at Phase 7
Error: Database connection timeout
```

---

## 💰 Maliyet

### Azure Free Tier ile Kullanım

| Resource | Monthly Cost |
|----------|--------------|
| Function App | ~$0 (1M execution free) |
| Storage | ~$0.50 |
| PostgreSQL* | ~$13 (optional) |
| **TOTAL** | **$0-15/month** |

*SQLite kullanırsanız sadece $0!

### Günlük 1 Execution

```
1 execution/day × 30 days = 30 executions/month
→ Tamamen ücretsiz! (1M limit içinde)
```

---

## 🔧 Troubleshooting

### "Module not found"
```bash
# requirements.txt'i kontrol edin
cd azure_functions
cat requirements.txt

# Yeniden deploy
func azure functionapp publish your-function-app --python
```

### "Email gönderilmiyor"
```bash
# SMTP settings kontrol
az functionapp config appsettings list --name your-function-app --resource-group your-rg | grep SMTP

# Gmail için: 2FA + App Password gerekli!
# Logs'da hatayı ara
az functionapp log tail --name your-function-app --resource-group your-rg | grep -i smtp
```

### "Timer çalışmıyor"
```bash
# Schedule kontrol (UTC timezone!)
# Türkiye UTC+3, yani 18:00 TR = 15:00 UTC

# Schedule değiştir:
schedule="0 0 15 * * 1-5"  # 18:00 Türkiye saati
```

---

## 📚 Daha Fazla Bilgi

- **Detaylı Deployment**: `docs/DEPLOYMENT_GUIDE.md`
- **Sistem Mimarisi**: `README.md`
- **Azure Functions Docs**: https://docs.microsoft.com/azure/azure-functions/

---

## ✅ Checklist

**Local Test:**
- [ ] Python 3.11 kurulu
- [ ] Packages yüklendi (pandas, numpy, ta-lib, openpyxl)
- [ ] `python create_sample_data.py` çalıştı
- [ ] `python backtest_all.py` çalıştı

**Azure Deployment:**
- [ ] Azure CLI kurulu ve login yapıldı
- [ ] Gmail App Password oluşturuldu
- [ ] `./scripts/deploy_azure.sh` başarılı
- [ ] Environment variables ayarlandı (SMTP)
- [ ] Health endpoint test edildi
- [ ] Email bildirimi alındı

---

## 🎉 Başarılı!

Sisteminiz çalışıyor! Her gün saat 18:00'de:
- ✅ Veriler toplanacak
- ✅ Sinyaller üretilecek
- ✅ Backtest çalışacak
- ✅ Email raporu gelecek

**Bir sonraki adım:** PostgreSQL migration veya Web Dashboard 🚀
