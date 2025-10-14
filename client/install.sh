#!/bin/bash#!/bin/bash

# install.sh - Setup script für NFC Client auf Raspberry Pi OSecho "🚀 Installiere Client Dependencies..."

# Installiert Python venv und alle Dependencies

# Installiere Python-Pakete

set -e  # Exit bei Fehlerpip3 install flask

pip3 install requests

echo "==================================="pip3 install pyserial

echo "NFC Client Installation"pip3 install flask-socketio

echo "==================================="pip install cryptography



# Prüfe ob Python3 installiert istecho "✅ Installation abgeschlossen!"

if ! command -v python3 &> /dev/null; thenecho "💡 Starte den Client mit: ./start.sh"
    echo "❌ Python3 nicht gefunden!"
    echo "Installiere mit: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Prüfe Python Version (mindestens 3.7 erforderlich)
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python Version: $PYTHON_VERSION"

# Installiere System-Dependencies (falls nicht vorhanden)
echo ""
echo "Prüfe System-Dependencies..."
MISSING_PKGS=""

if ! dpkg -l | grep -q python3-venv; then
    MISSING_PKGS="$MISSING_PKGS python3-venv"
fi

if ! dpkg -l | grep -q python3-dev; then
    MISSING_PKGS="$MISSING_PKGS python3-dev"
fi

if ! dpkg -l | grep -q libmariadb-dev; then
    MISSING_PKGS="$MISSING_PKGS libmariadb-dev"
fi

if [ ! -z "$MISSING_PKGS" ]; then
    echo "⚠️  Fehlende Pakete:$MISSING_PKGS"
    echo "Installiere mit:"
    echo "  sudo apt update"
    echo "  sudo apt install -y$MISSING_PKGS"
    read -p "Jetzt installieren? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        sudo apt update
        sudo apt install -y $MISSING_PKGS
    else
        echo "⚠️  Installation fortgesetzt ohne System-Dependencies"
    fi
fi

# Erstelle venv falls nicht vorhanden
if [ ! -d "venv" ]; then
    echo ""
    echo "Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "✓ venv erstellt"
else
    echo "✓ venv bereits vorhanden"
fi

# Aktiviere venv
echo ""
echo "Aktiviere venv..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Update pip..."
pip install --upgrade pip

# Installiere Python Dependencies
echo ""
echo "Installiere Python Pakete..."
if [ -f "requirements.txt" ]; then
    echo "Verwende requirements.txt..."
    pip install -r requirements.txt
else
    echo "Installiere Standard-Pakete..."
    pip install flask flask-socketio eventlet pyserial cryptography requests python-dotenv
fi

echo ""
echo "==================================="
echo "✓ Installation erfolgreich!"
echo "==================================="
echo ""
echo "Nächste Schritte:"
echo "1. Konfiguriere .env Datei mit Server-URL"
echo "2. Schließe Arduino an (USB)"
echo "3. Starte mit: ./start.sh"
echo ""
echo "Zusätzliche Hinweise:"
echo "- Arduino Port: normalerweise /dev/ttyACM0 oder /dev/ttyUSB0"
echo "- User muss in 'dialout' Gruppe sein:"
echo "    sudo usermod -a -G dialout $USER"
echo "    (danach neu einloggen)"
echo ""
