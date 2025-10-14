#!/bin/bash
echo "🚀 Installiere Client Dependencies..."

# Installiere Python-Pakete
pip3 install flask
pip3 install requests
pip3 install pyserial
pip3 install flask-socketio
pip install cryptography

echo "✅ Installation abgeschlossen!"
echo "💡 Starte den Client mit: ./start.sh"