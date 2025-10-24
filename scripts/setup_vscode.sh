#!/bin/bash
#
# Visual Studio Code Quick Setup Script
# Trading System projesini VS Code'da açmak için
#

set -e

echo "======================================"
echo "Visual Studio Code Quick Setup"
echo "======================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Proje dizini
PROJECT_DIR="$HOME/trading-system"

# 1. Projeyi clone et (eğer yoksa)
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📦 Proje clone ediliyor...${NC}"
    git clone https://github.com/erolygc/ClaudeCode.git "$PROJECT_DIR"
    echo -e "${GREEN}✅ Clone tamamlandı!${NC}"
else
    echo -e "${YELLOW}📁 Proje zaten mevcut, güncelleniyor...${NC}"
    cd "$PROJECT_DIR"
    git fetch origin
    echo -e "${GREEN}✅ Güncelleme tamamlandı!${NC}"
fi

# 2. Branch'i checkout et
cd "$PROJECT_DIR"
echo ""
echo -e "${YELLOW}🌿 Branch checkout ediliyor...${NC}"
git checkout claude/financial-trading-system-011CURWtvGNU2QWu1qrZWB8D
echo -e "${GREEN}✅ Branch hazır!${NC}"

# 3. Virtual environment oluştur
echo ""
echo -e "${YELLOW}🐍 Virtual environment oluşturuluyor...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment oluşturuldu!${NC}"
else
    echo -e "${GREEN}✅ Virtual environment zaten mevcut!${NC}"
fi

# 4. Dependencies yükle
echo ""
echo -e "${YELLOW}📦 Dependencies yükleniyor...${NC}"
source venv/bin/activate

# Core dependencies
pip install --upgrade pip > /dev/null 2>&1
pip install pandas numpy ta-lib openpyxl > /dev/null 2>&1

# Azure Functions dependencies (optional)
if [ -f "azure_functions/requirements.txt" ]; then
    pip install -r azure_functions/requirements.txt > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Dependencies yüklendi!${NC}"

# 5. Environment template oluştur
echo ""
echo -e "${YELLOW}⚙️  Environment dosyası oluşturuluyor...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env dosyası oluşturuldu! Lütfen düzenleyin.${NC}"
else
    echo -e "${GREEN}✅ .env dosyası zaten mevcut!${NC}"
fi

# 6. VS Code workspace settings oluştur
echo ""
echo -e "${YELLOW}🔧 VS Code settings oluşturuluyor...${NC}"
mkdir -p .vscode

cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/.venv": true,
        "**/venv": true,
        "**/*.db": true,
        "**/*.db-journal": true
    },
    "files.associations": {
        "*.md": "markdown"
    }
}
EOF

cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Create Sample Data",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/create_sample_data.py",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Backtest",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/backtest_all.py",
            "console": "integratedTerminal"
        },
        {
            "name": "Azure Functions: Attach",
            "type": "python",
            "request": "attach",
            "port": 9091,
            "preLaunchTask": "func: host start"
        }
    ]
}
EOF

cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Data Collection",
            "type": "shell",
            "command": "${workspaceFolder}/venv/bin/python",
            "args": ["collect_all_data.py"],
            "problemMatcher": []
        },
        {
            "label": "Run Backtest",
            "type": "shell",
            "command": "${workspaceFolder}/venv/bin/python",
            "args": ["backtest_all.py"],
            "problemMatcher": []
        },
        {
            "label": "Create Sample Data",
            "type": "shell",
            "command": "${workspaceFolder}/venv/bin/python",
            "args": ["create_sample_data.py"],
            "problemMatcher": []
        }
    ]
}
EOF

echo -e "${GREEN}✅ VS Code settings oluşturuldu!${NC}"

# 7. VS Code'da aç
echo ""
echo -e "${YELLOW}🚀 VS Code açılıyor...${NC}"
code "$PROJECT_DIR"

echo ""
echo "======================================"
echo -e "${GREEN}✅ Kurulum Tamamlandı!${NC}"
echo "======================================"
echo ""
echo "Proje dizini: $PROJECT_DIR"
echo "Branch: claude/financial-trading-system-011CURWtvGNU2QWu1qrZWB8D"
echo ""
echo "Sonraki adımlar:"
echo "1. VS Code'da .env dosyasını düzenleyin (email settings)"
echo "2. Terminal'de: source venv/bin/activate"
echo "3. Test için: python create_sample_data.py"
echo ""
echo "Keyifli kodlamalar! 🎉"
