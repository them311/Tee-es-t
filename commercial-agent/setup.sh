#!/bin/bash
# Setup script for the Commercial Agent
# Run: chmod +x setup.sh && ./setup.sh

set -e

echo "============================================"
echo "  AGENT COMMERCIAL L-FDS — Configuration"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required. Install it first."
    exit 1
fi
echo "Python: $(python3 --version)"

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Fichier .env cree depuis .env.example"
fi

# Check each key
echo ""
echo "--- Verification des cles API ---"
echo ""

check_key() {
    local key_name=$1
    local key_prefix=$2
    local url=$3

    value=$(grep "^${key_name}=" .env | cut -d'=' -f2-)
    if [ -z "$value" ] || [ "$value" = "$key_prefix" ]; then
        echo "MISSING: $key_name"
        echo "  → Va sur: $url"
        echo "  → Puis colle la cle dans .env"
        echo ""
        return 1
    else
        echo "OK: $key_name"
        return 0
    fi
}

missing=0

check_key "ANTHROPIC_API_KEY" "sk-ant-..." "https://console.anthropic.com/settings/keys" || missing=$((missing+1))
check_key "HUBSPOT_API_KEY" "pat-..." "https://app-eu1.hubspot.com → Settings → Integrations → Private Apps" || missing=$((missing+1))
check_key "NOTION_API_KEY" "ntn_..." "https://www.notion.so/profile/integrations" || missing=$((missing+1))
check_key "GITHUB_TOKEN" "ghp_..." "https://github.com/settings/tokens" || missing=$((missing+1))

# Check Gmail credentials file
gmail_path=$(grep "^GMAIL_CREDENTIALS_PATH=" .env | cut -d'=' -f2-)
if [ ! -f "$gmail_path" ]; then
    echo "MISSING: Gmail credentials file ($gmail_path)"
    echo "  → Va sur: https://console.cloud.google.com → APIs → Credentials → OAuth 2.0"
    echo "  → Telecharge le JSON et place-le dans $gmail_path"
    echo ""
    missing=$((missing+1))
else
    echo "OK: Gmail credentials"
fi

echo ""

if [ $missing -gt 0 ]; then
    echo "============================================"
    echo "  $missing cle(s) manquante(s)"
    echo "  Complete le fichier .env puis relance:"
    echo "  ./setup.sh"
    echo "============================================"
    exit 1
fi

echo "============================================"
echo "  Toutes les cles sont configurees !"
echo "============================================"
echo ""

# Install dependencies
echo "Installation des dependances..."
pip install -r requirements.txt
echo ""

echo "============================================"
echo "  PRET ! Commandes disponibles :"
echo ""
echo "  Mode interactif :"
echo "    python main.py"
echo ""
echo "  Mode autonome :"
echo "    python autonomous.py morning    (routine du matin)"
echo "    python autonomous.py followup   (relances)"
echo "    python autonomous.py weekly_audit (audit hebdo)"
echo ""
echo "  Deployer sur un serveur :"
echo "    → Railway : railway up"
echo "    → Render  : git push (auto-deploy via render.yaml)"
echo "    → Docker  : docker build -t agent . && docker run agent"
echo "============================================"
