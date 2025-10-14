#!/bin/bashsource venv/bin/activate

# start_server.sh - Startet den NFC Backend Server mit venvpython3 app.py
# Lädt Datenbank Konfiguration und startet Flask API

set -e  # Exit bei Fehler

echo "==================================="
echo "Starte NFC Backend Server"
echo "==================================="

# Prüfe ob venv existiert
if [ ! -d "venv" ]; then
    echo "❌ Virtual Environment nicht gefunden!"
    echo "Führe zuerst ./install_server.sh aus"
    exit 1
fi

# Aktiviere venv
echo "Aktiviere Virtual Environment..."
source venv/bin/activate

# Lade .env Datei falls vorhanden
if [ -f ".env" ]; then
    echo "Lade .env Konfiguration..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Prüfe MariaDB Verbindung
echo ""
echo "Prüfe Datenbank..."
if command -v mysql &> /dev/null; then
    if mysql -u${DB_USER:-root} -p${DB_PASS:-} -e "USE ${DB_NAME:-pro1}" 2>/dev/null; then
        echo "✓ Datenbank Verbindung OK"
    else
        echo "⚠️  Datenbank nicht erreichbar!"
        echo "   Stelle sicher dass MariaDB läuft:"
        echo "   sudo systemctl start mariadb"
    fi
else
    echo "⚠️  mysql client nicht gefunden"
fi

# Port Konfiguration
PORT=${FLASK_PORT:-5001}
HOST=${FLASK_HOST:-0.0.0.0}

echo ""
echo "==================================="
echo "Server wird gestartet..."
echo "==================================="
echo "URL: http://$HOST:$PORT"
echo "Drücke Ctrl+C zum Beenden"
echo "==================================="
echo ""

# Starte Flask App
python3 app.py

# Cleanup beim Beenden
trap "echo ''; echo 'Server beendet'; deactivate" EXIT
