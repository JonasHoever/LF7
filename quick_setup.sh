#!/bin/bash
# quick_setup.sh - Schnellinstallation für Raspberry Pi OS
# Installiert Server + Client in einem Durchgang

set -e

echo "========================================"
echo "NFC Worktime System - Schnellinstallation"
echo "========================================"
echo ""

# Frage nach Installation
echo "Dieses Script installiert:"
echo "1. MariaDB Server"
echo "2. NFC Backend Server"
echo "3. NFC Client mit Arduino Support"
echo ""
read -p "Fortfahren? (j/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Jj]$ ]]; then
    echo "Installation abgebrochen"
    exit 1
fi

# MariaDB installieren
echo ""
echo "=== Schritt 1/3: MariaDB Installation ==="
if command -v mysql &> /dev/null; then
    echo "✓ MariaDB bereits installiert"
else
    echo "Installiere MariaDB..."
    sudo apt update
    sudo apt install -y mariadb-server mariadb-client
    echo "✓ MariaDB installiert"
    
    echo ""
    echo "⚠️  WICHTIG: MariaDB Sicherheit einrichten"
    echo "Führe nach diesem Script aus:"
    echo "  sudo mysql_secure_installation"
fi

# Server installieren
echo ""
echo "=== Schritt 2/3: Server Installation ==="
cd server
./install_server.sh

echo ""
echo "Konfiguriere Server..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Bitte .env Datei bearbeiten:"
    echo "  nano server/.env"
    echo "  (DB_PASS eintragen)"
fi

# Client installieren
echo ""
echo "=== Schritt 3/3: Client Installation ==="
cd ../client
./install.sh

echo ""
echo "Konfiguriere Client..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Bitte .env Datei bearbeiten:"
    echo "  nano client/.env"
    echo "  (SERVER_URL eintragen)"
fi

# User zur dialout Gruppe hinzufügen
echo ""
echo "Füge User zur dialout Gruppe hinzu..."
sudo usermod -a -G dialout $USER
echo "✓ User hinzugefügt (neu einloggen erforderlich!)"

echo ""
echo "========================================"
echo "✓ Installation erfolgreich!"
echo "========================================"
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. MariaDB Sicherheit:"
echo "   sudo mysql_secure_installation"
echo ""
echo "2. Datenbank einrichten:"
echo "   cd server"
echo "   mysql -u root -p < src/db_setup.sql"
echo ""
echo "3. Konfiguration bearbeiten:"
echo "   nano server/.env  # DB_PASS"
echo "   nano client/.env  # SERVER_URL"
echo ""
echo "4. Arduino anschließen und neu einloggen:"
echo "   logout"
echo ""
echo "5. System starten:"
echo "   cd server && ./start_server.sh &"
echo "   cd client && ./start.sh"
echo ""
echo "6. Browser öffnen:"
echo "   http://localhost:5000"
echo ""
