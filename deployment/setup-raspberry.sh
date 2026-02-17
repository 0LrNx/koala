#!/bin/bash
set -e

echo "🚀 Installation du bot Koala"
echo "=============================================="

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

INSTALL_DIR="$HOME/koala-bot"
SERVICE_NAME="koala-bot"

echo -e "${BLUE}📦 Installation des dépendances système...${NC}"
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

echo -e "${BLUE}📂 Clonage du repository...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo "Le dossier existe déjà, mise à jour..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo -e "${BLUE}🐍 Configuration de l'environnement virtuel Python...${NC}"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${BLUE}⚙️ Configuration du fichier .env...${NC}"
if [ ! -f .env ]; then
    echo "Création du fichier .env..."
    cat > .env << 'EOF'
ICS_URL="VOTRE_URL_ICS"
DISCORD_TOKEN="VOTRE_TOKEN"
DISCORD_CHANNEL_ID=123456789
MONITORING_CHANNEL_ID=123456789
PANDASCORE_ACCESS_TOKEN="VOTRE_TOKEN"
ROOTME_API_KEY="VOTRE_API_KEY"
EOF
    echo "⚠️  ATTENTION : Éditez le fichier .env avec vos vraies valeurs !"
    echo "   nano $INSTALL_DIR/.env"
fi

echo -e "${BLUE}📋 Configuration du service systemd...${NC}"
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Koala Discord Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin"
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}🔄 Activation du service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo -e "${GREEN}✅ Installation terminée !${NC}"
echo ""
echo "Prochaines étapes :"
echo "1. Éditez le fichier .env avec vos vraies valeurs :"
echo "   nano $INSTALL_DIR/.env"
echo ""
echo "2. Démarrez le bot :"
echo "   sudo systemctl start $SERVICE_NAME"
echo ""
echo "3. Vérifiez le status :"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "4. Voir les logs :"
echo "   sudo journalctl -u $SERVICE_NAME -f"
