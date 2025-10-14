#!/bin/bash
# start.sh - Startet den NFC Client mit venv
# Lädt Arduino Port Erkennung und startet Flask Web Interface

set -e  # Exit bei Fehler

echo "==================================="
echo "Starte NFC Client"
echo "==================================="

# Prüfe ob venv existiert
if [ ! -d "venv" ]; then
    echo "❌ Virtual Environment nicht gefunden!"
    echo "Führe zuerst ./install.sh aus"
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

# Prüfe Arduino Verbindung
echo ""
echo "Suche Arduino..."
if ls /dev/ttyACM* 1> /dev/null 2>&1; then
    ARDUINO_PORT=$(ls /dev/ttyACM* | head -n 1)
    echo "✓ Arduino gefunden: $ARDUINO_PORT"
elif ls /dev/ttyUSB* 1> /dev/null 2>&1; then
    ARDUINO_PORT=$(ls /dev/ttyUSB* | head -n 1)
    echo "✓ Arduino gefunden: $ARDUINO_PORT"
else
    echo "⚠️  Arduino nicht gefunden!"
    echo "   Manueller Tag-Input wird verfügbar sein"
    echo "   Hinweis: User muss in 'dialout' Gruppe sein:"
    echo "   sudo usermod -a -G dialout $USER"
fi

# Port Konfiguration
PORT=${FLASK_PORT:-5000}
HOST=${FLASK_HOST:-0.0.0.0}

echo ""
echo "==================================="
echo "Client wird gestartet..."
echo "==================================="
echo "URL: http://$HOST:$PORT"
echo "Drücke Ctrl+C zum Beenden"
echo "==================================="
echo ""

# Starte Flask App
python3 app.py

# Cleanup beim Beenden
trap "echo ''; echo 'Client beendet'; deactivate" EXIT
