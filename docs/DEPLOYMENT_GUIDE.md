# Azure Deployment Guide
## Trading System - FAZ 10

Bu dokümanda Azure'a deployment işleminin adım adım yapılışı anlatılmaktadır.

---

## 📋 Ön Gereksinimler

### 1. Gerekli Araçlar

```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Python 3.11
python --version  # 3.11 olmalı
```

### 2. Azure Hesabı

- Azure hesabınız olmalı ([Free Trial](https://azure.microsoft.com/free/))
- Subscription ID'nizi bilin
- Yeterli kotanız olmalı (Function App, Storage Account)

---

## 🚀 Deployment Adımları

### Adım 1: Azure'a Login

```bash
az login
```

Tarayıcı açılacak, Microsoft hesabınızla giriş yapın.

```bash
# Subscription'ı doğrulayın
az account show

# Farklı subscription kullanmak için
az account set --subscription "Subscription Name"
```

### Adım 2: Environment Ayarlarını Yapın

`azure_functions/local.settings.json` dosyasını oluşturun:

```bash
cp azure_functions/local.settings.json.template azure_functions/local.settings.json
```

**Gerekli ayarları doldurun:**

```json
{
  "Values": {
    "SMTP_USERNAME": "your-email@gmail.com",
    "SMTP_PASSWORD": "your-app-password",
    "TO_EMAILS": "recipient@example.com",
    "FROM_EMAIL": "your-email@gmail.com"
  }
}
```

**Gmail için App Password oluşturma:**
1. Google Account → Security
2. 2-Step Verification'ı aktif edin
3. App passwords → Generate new
4. "Mail" ve "Other" seçin, "Trading System" yazın
5. Oluşturulan 16 haneli şifreyi `SMTP_PASSWORD`'e yazın

### Adım 3: Deployment Scriptini Çalıştırın

```bash
cd /path/to/ClaudeCode

# Varsayılan ayarlarla
./scripts/deploy_azure.sh

# Veya özel ayarlarla
./scripts/deploy_azure.sh my-resource-group my-function-app eastus
```

**Script şunları yapacak:**
1. ✅ Resource Group oluşturur
2. ✅ Storage Account oluşturur
3. ✅ Function App oluşturur (Python 3.11, Linux)
4. ✅ App Settings'i configure eder
5. ✅ Function code'u deploy eder

### Adım 4: Environment Variables Ayarlayın

Azure Portal'dan veya CLI ile:

```bash
az functionapp config appsettings set \
  --name your-function-app-name \
  --resource-group your-resource-group \
  --settings \
  SMTP_USERNAME="your-email@gmail.com" \
  SMTP_PASSWORD="your-app-password" \
  TO_EMAILS="recipient1@example.com,recipient2@example.com" \
  FROM_EMAIL="your-email@gmail.com" \
  ENABLE_NOTIFICATIONS="true"
```

**Kritik ayarlar:**
- `SMTP_USERNAME`: Email gönderen adres
- `SMTP_PASSWORD`: App password (güvenli!)
- `TO_EMAILS`: Alıcılar (virgülle ayırın)
- `DATABASE_TYPE`: sqlite veya postgresql

### Adım 5: Test Edin

```bash
# Health check
curl https://your-function-app.azurewebsites.net/api/health

# Beklenen output:
{
  "status": "healthy",
  "timestamp": "2025-10-24T...",
  "service": "Trading System"
}
```

**Manuel trigger (test için):**
```bash
# Function key alın
FUNCTION_KEY=$(az functionapp keys list \
  --name your-function-app-name \
  --resource-group your-resource-group \
  --query "functionKeys.default" -o tsv)

# Manuel tetikle
curl -X POST "https://your-function-app.azurewebsites.net/api/manual-trigger?code=$FUNCTION_KEY"
```

### Adım 6: Monitoring ve Logs

```bash
# Real-time logs
az functionapp log tail \
  --name your-function-app-name \
  --resource-group your-resource-group

# Veya Azure Portal'dan
# Function App → Monitoring → Log Stream
```

---

## ⏰ Timer Schedule Ayarları

Function App varsayılan olarak **her iş günü saat 18:00**'de çalışır.

**Schedule formatı:**
```python
schedule="0 0 18 * * 1-5"  # Saniye Dakika Saat Gün Ay Hafta_Günü
```

**Örnekler:**
```python
"0 0 9 * * 1-5"    # Pazartesi-Cuma 09:00
"0 0 18 * * 1-5"   # Pazartesi-Cuma 18:00 (varsayılan)
"0 0 12 * * *"     # Her gün 12:00
"0 */30 * * * *"   # Her 30 dakikada bir
```

**Schedule değiştirmek için:**
`azure_functions/function_app.py` dosyasında `@app.timer_trigger` decorator'ını düzenleyin.

---

## 🗄️ PostgreSQL Migration (Opsiyonel)

SQLite yerine PostgreSQL kullanmak için:

### 1. PostgreSQL Database Oluşturun

```bash
# Azure PostgreSQL Flexible Server oluştur
az postgres flexible-server create \
  --resource-group your-resource-group \
  --name your-postgres-server \
  --location eastus \
  --admin-user adminuser \
  --admin-password 'YourSecurePassword123!' \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 14

# Database oluştur
az postgres flexible-server db create \
  --resource-group your-resource-group \
  --server-name your-postgres-server \
  --database-name tradingdb
```

### 2. Firewall Ayarları

```bash
# Azure services'e izin ver
az postgres flexible-server firewall-rule create \
  --resource-group your-resource-group \
  --name your-postgres-server \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### 3. Environment Variables

```bash
az functionapp config appsettings set \
  --name your-function-app-name \
  --resource-group your-resource-group \
  --settings \
  DATABASE_TYPE="postgresql" \
  POSTGRES_HOST="your-postgres-server.postgres.database.azure.com" \
  POSTGRES_DB="tradingdb" \
  POSTGRES_USER="adminuser" \
  POSTGRES_PASSWORD="YourSecurePassword123!" \
  POSTGRES_PORT="5432"
```

### 4. requirements.txt Güncelleyin

`azure_functions/requirements.txt` içinde uncomment edin:
```txt
psycopg2-binary>=2.9.9
```

### 5. Database Manager'ı Güncelleyin

`database/db_manager.py` dosyasında PostgreSQL desteği ekleyin (ileride implement edilecek).

---

## 🔐 Secrets Management (Best Practices)

### Azure Key Vault Kullanımı

```bash
# Key Vault oluştur
az keyvault create \
  --name your-keyvault-name \
  --resource-group your-resource-group \
  --location eastus

# Secret ekle
az keyvault secret set \
  --vault-name your-keyvault-name \
  --name "SmtpPassword" \
  --value "your-app-password"

# Function App'e erişim ver
az functionapp identity assign \
  --name your-function-app-name \
  --resource-group your-resource-group

# Key Vault policy ayarla
az keyvault set-policy \
  --name your-keyvault-name \
  --object-id <function-app-identity-object-id> \
  --secret-permissions get list
```

**App Settings'de kullanım:**
```bash
az functionapp config appsettings set \
  --name your-function-app-name \
  --resource-group your-resource-group \
  --settings \
  SMTP_PASSWORD="@Microsoft.KeyVault(SecretUri=https://your-keyvault-name.vault.azure.net/secrets/SmtpPassword/)"
```

---

## 📊 Monitoring ve Alerting

### Application Insights

```bash
# Application Insights oluştur
az monitor app-insights component create \
  --app your-app-insights-name \
  --location eastus \
  --resource-group your-resource-group \
  --application-type web

# Instrumentation key al
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app your-app-insights-name \
  --resource-group your-resource-group \
  --query "instrumentationKey" -o tsv)

# Function App'e bağla
az functionapp config appsettings set \
  --name your-function-app-name \
  --resource-group your-resource-group \
  --settings \
  APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"
```

**Metrics to Monitor:**
- Function execution count
- Function duration
- Error rate
- HTTP response codes

### Alerts Oluşturma

Azure Portal → Monitor → Alerts → New Alert Rule

**Önerilen alerts:**
1. Function execution failures > 3 in 5 minutes
2. Average duration > 5 minutes
3. HTTP 5xx errors > 5 in 10 minutes

---

## 🔄 CI/CD Pipeline (GitHub Actions)

`.github/workflows/deploy.yml` oluşturun:

```yaml
name: Deploy to Azure Functions

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd azure_functions
        pip install -r requirements.txt

    - name: Deploy to Azure Functions
      uses: Azure/functions-action@v1
      with:
        app-name: ${{ secrets.AZURE_FUNCTION_APP_NAME }}
        package: azure_functions
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

**Secrets ayarlayın:**
1. GitHub → Settings → Secrets and variables → Actions
2. New repository secret:
   - `AZURE_FUNCTION_APP_NAME`: your-function-app-name
   - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`: (Azure Portal'dan download edin)

---

## 🧪 Testing

### Local Testing

```bash
cd azure_functions

# Local settings oluştur
cp local.settings.json.template local.settings.json

# Settings'i doldurun
nano local.settings.json

# Start local Functions runtime
func start
```

**Test endpoints:**
- Health: `http://localhost:7071/api/health`
- Manual trigger: `http://localhost:7071/api/manual-trigger`

### Production Testing

```bash
# Health check
curl https://your-function-app.azurewebsites.net/api/health

# Watch logs
az functionapp log tail --name your-function-app --resource-group your-rg

# Check recent invocations
az monitor activity-log list \
  --resource-group your-resource-group \
  --offset 1h
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" hatası**
```bash
# requirements.txt'i kontrol edin
# Yeniden deploy edin
func azure functionapp publish your-function-app-name --python
```

**2. Timer trigger çalışmıyor**
```bash
# Schedule'ı kontrol edin
# Timezone: UTC kullanıyor (Türkiye: UTC+3)
# 18:00 TR = 15:00 UTC

# Schedule'ı düzeltin:
schedule="0 0 15 * * 1-5"  # Türkiye saati 18:00
```

**3. Email gönderilmiyor**
```bash
# SMTP credentials'ı kontrol edin
# Gmail: 2FA + App Password gerekli
# Logs'da SMTP hatalarını arayın

az functionapp log tail --name your-function-app --resource-group your-rg | grep -i smtp
```

**4. Database connection error**
```bash
# SQLite: DATABASE_PATH doğru mu?
# PostgreSQL: Firewall kuralları kontrol edin
# Connection string'i test edin
```

---

## 💰 Maliyet Optimizasyonu

### Consumption Plan (Varsayılan)

- **Ücretsiz Grant**: İlk 1M execution + 400K GB-s
- **Sonrası**: ~$0.20 per 1M executions
- **Günlük 1 execution**: Neredeyse bedava!

### Tahmini Maliyet

| Resource | Monthly Cost |
|----------|--------------|
| Function App (Consumption) | ~$0 (free tier) |
| Storage Account (LRS) | ~$0.50 |
| PostgreSQL (B1ms) | ~$13 |
| Application Insights | ~$2 (ilk 5GB free) |
| **TOTAL** | ~$15-20/month |

**Maliyet düşürme tips:**
- Consumption Plan kullanın (Dedicated yerine)
- Küçük database tier (B1ms yeterli)
- Application Insights sampling aktif edin
- Eski logs'ları temizleyin

---

## 📚 Ek Kaynaklar

- [Azure Functions Python Developer Guide](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Timer Trigger Documentation](https://docs.microsoft.com/azure/azure-functions/functions-bindings-timer)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)
- [PostgreSQL Flexible Server](https://docs.microsoft.com/azure/postgresql/flexible-server/)

---

## ✅ Deployment Checklist

- [ ] Azure CLI installed & logged in
- [ ] Resource group created
- [ ] Storage account created
- [ ] Function App created
- [ ] Environment variables configured
- [ ] Email credentials set (SMTP)
- [ ] Code deployed successfully
- [ ] Health endpoint tested
- [ ] Timer schedule verified
- [ ] Monitoring/alerts configured
- [ ] First execution successful
- [ ] Email notification received

---

Sorularınız için: [GitHub Issues](https://github.com/yourusername/ClaudeCode/issues)
