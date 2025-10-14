#!/bin/bash
# install_server.sh - Setup script für NFC Server auf Raspberry Pi OS
# Installiert Python venv und alle Dependencies

set -e  # Exit bei Fehler

echo "==================================="
echo "NFC Server Installation"
echo "==================================="

# Prüfe ob Python3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden!"
    echo "Installiere mit: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Prüfe Python Version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python Version: $PYTHON_VERSION"

# Installiere System-Dependencies
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

if ! dpkg -l | grep -q mariadb-client; then
    MISSING_PKGS="$MISSING_PKGS mariadb-client"
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

# Erstelle venv
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
    pip install flask flask-socketio eventlet mysql-connector-python argon2-cffi python-dotenv
fi

echo ""
echo "==================================="
echo "✓ Installation erfolgreich!"
echo "==================================="
echo ""
echo "Nächste Schritte:"
echo "1. MariaDB installieren: sudo apt install mariadb-server"
echo "2. Datenbank einrichten: python3 src/db_setup.py"
echo "3. .env Datei konfigurieren"
echo "4. Starte mit: ./start_server.sh"
echo ""
