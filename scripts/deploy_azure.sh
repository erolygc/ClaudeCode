#!/bin/bash
#
# Azure Functions Deployment Script
# Usage: ./deploy_azure.sh [resource-group] [function-app-name] [region]
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
RESOURCE_GROUP="${1:-trading-system-rg}"
FUNCTION_APP_NAME="${2:-trading-system-func}"
REGION="${3:-eastus}"
STORAGE_ACCOUNT_NAME="${FUNCTION_APP_NAME}storage"
PYTHON_VERSION="3.11"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Azure Functions Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Function App: $FUNCTION_APP_NAME"
echo "Region: $REGION"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
echo -e "${YELLOW}Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure. Please run 'az login' first.${NC}"
    exit 1
fi

ACCOUNT_NAME=$(az account show --query name -o tsv)
echo -e "${GREEN}✅ Logged in as: $ACCOUNT_NAME${NC}"
echo ""

# Create resource group
echo -e "${YELLOW}📦 Creating resource group...${NC}"
if az group create --name "$RESOURCE_GROUP" --location "$REGION" &> /dev/null; then
    echo -e "${GREEN}✅ Resource group created/updated${NC}"
else
    echo -e "${RED}❌ Failed to create resource group${NC}"
    exit 1
fi

# Create storage account
echo -e "${YELLOW}💾 Creating storage account...${NC}"
STORAGE_ACCOUNT_NAME=$(echo $STORAGE_ACCOUNT_NAME | tr '[:upper:]' '[:lower:]' | tr -d '-')  # Storage account name restrictions
STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME:0:24}  # Max 24 chars

if az storage account create \
    --name "$STORAGE_ACCOUNT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$REGION" \
    --sku Standard_LRS &> /dev/null; then
    echo -e "${GREEN}✅ Storage account created/updated${NC}"
else
    echo -e "${RED}❌ Failed to create storage account${NC}"
    exit 1
fi

# Create Function App
echo -e "${YELLOW}⚡ Creating Function App...${NC}"
if az functionapp create \
    --resource-group "$RESOURCE_GROUP" \
    --consumption-plan-location "$REGION" \
    --runtime python \
    --runtime-version "$PYTHON_VERSION" \
    --functions-version 4 \
    --name "$FUNCTION_APP_NAME" \
    --storage-account "$STORAGE_ACCOUNT_NAME" \
    --os-type Linux &> /dev/null; then
    echo -e "${GREEN}✅ Function App created/updated${NC}"
else
    echo -e "${RED}❌ Failed to create Function App${NC}"
    exit 1
fi

# Configure App Settings
echo -e "${YELLOW}⚙️  Configuring App Settings...${NC}"

# Read settings from local.settings.json if exists
if [ -f "azure_functions/local.settings.json" ]; then
    echo -e "${YELLOW}   Using settings from local.settings.json${NC}"

    # Set each setting (excluding comments and system variables)
    az functionapp config appsettings set \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
        DATABASE_TYPE="sqlite" \
        SMTP_SERVER="${SMTP_SERVER:-smtp.gmail.com}" \
        SMTP_PORT="${SMTP_PORT:-587}" \
        ENABLE_NOTIFICATIONS="true" \
        &> /dev/null

    echo -e "${GREEN}✅ App settings configured${NC}"
else
    echo -e "${YELLOW}⚠️  local.settings.json not found, using defaults${NC}"
fi

# Deploy the function code
echo -e "${YELLOW}🚀 Deploying function code...${NC}"
cd azure_functions

if func azure functionapp publish "$FUNCTION_APP_NAME" --python; then
    echo -e "${GREEN}✅ Function code deployed successfully${NC}"
else
    echo -e "${RED}❌ Failed to deploy function code${NC}"
    exit 1
fi

cd ..

# Get Function App URL
FUNCTION_URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "defaultHostName" -o tsv)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Function App URL: https://$FUNCTION_URL"
echo "Health Check: https://$FUNCTION_URL/api/health"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure environment variables in Azure Portal"
echo "2. Set up email credentials (SMTP_USERNAME, SMTP_PASSWORD, TO_EMAILS)"
echo "3. Test the health endpoint"
echo "4. Monitor logs: az functionapp log tail --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo -e "${GREEN}Done!${NC}"
