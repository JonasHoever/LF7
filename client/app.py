from src import script
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import serial
import threading
import time

app = Flask(__name__)

usys = script.UserSystemClient()
csfs = script.Client_Short_Function()  # Instanz erstellen, nicht Klasse

# Versuche Arduino zu verbinden - falls nicht verfügbar, läuft nur Web-UI
ser = None
try:
    ser = serial.Serial('/dev/cu.usbmodem1101', 9600, timeout=1)
    print("✅ Arduino erfolgreich verbunden auf /dev/cu.usbmodem1101")
except Exception as e:
    print(f"⚠️  Arduino nicht gefunden: {e}")
    print("💡 App läuft nur mit Web-UI (ohne Arduino NFC-Scanner)")
    print("🔌 Schließe Arduino an und starte neu für NFC-Scanner")

def is_valid_nfc_tag(tag):
    """Prüft ob der String eine gültige NFC-Tag-ID ist (nur Hex-Zeichen, 4-20 Zeichen)"""
    if not tag or len(tag) < 4 or len(tag) > 20:
        return False
    # Prüfe ob nur Hex-Zeichen (0-9, A-F)
    return all(c in '0123456789ABCDEF' for c in tag.upper())

def nfc_scan_loop():
    if ser is None:
        print("🚫 NFC-Scanner deaktiviert - Arduino nicht verbunden")
        return
    
    while True:
        try:
            if ser.in_waiting > 0:
                nfc_tag = ser.readline().decode('utf-8').strip()
                if nfc_tag and is_valid_nfc_tag(nfc_tag):
                    print(f"✅ Gültige NFC-Tag-ID empfangen: {nfc_tag}")
                    # Triggere die Route direkt
                    handle_nfc_request(nfc_tag)
                    time.sleep(1)
                elif nfc_tag:
                    print(f"⚠️  Ungültige Daten ignoriert: {nfc_tag}")
        except Exception as e:
            print(f"❌ Fehler beim NFC-Scan: {e}")
            time.sleep(5)  # Warte 5 Sekunden bei Fehler

def handle_nfc_request(nfc_tag):
    """Wird aufgerufen wenn NFC-Tag vom Arduino gescannt wird"""
    try:
        result = csfs.request(nfc_tag)
        print(f"Scan-Ergebnis für {nfc_tag}: {result}")
        # Speichere Ergebnis für Web-UI
        handle_web_nfc_request(nfc_tag)
        return result
    except Exception as e:
        print(f"Fehler bei NFC-Request: {e}")
        handle_web_nfc_request(nfc_tag)  # Speichere auch Fehler
        return None

# Globale Variable für letztes Scan-Ergebnis (für Web-UI Anzeige)
last_scan_result = None

def handle_web_nfc_request(nfc_tag):
    """Verarbeitet Arduino NFC-Scanner Daten für Web-UI Anzeige"""
    global last_scan_result
    try:
        result = csfs.request(nfc_tag)
        last_scan_result = {
            'success': True,
            'nfc_tag': nfc_tag,
            'exists': result[0] if result else False,
            'pin_set': result[1] if result else False,
            'message': f"Tag {nfc_tag} erfolgreich verarbeitet",
            'timestamp': time.strftime('%H:%M:%S')
        }
        return last_scan_result
    except Exception as e:
        last_scan_result = {
            'success': False,
            'nfc_tag': nfc_tag, 
            'error': str(e),
            'message': f"Fehler bei Tag {nfc_tag}: {str(e)}",
            'timestamp': time.strftime('%H:%M:%S')
        }
        return last_scan_result

def get_arduino_status():
    """Gibt Arduino Status für Template zurück"""
    if ser is None:
        return {
            'arduino_status': '❌ Nicht verbunden',
            'nfc_status': '🚫 Deaktiviert (nur Web-UI verfügbar)'
        }
    else:
        return {
            'arduino_status': '✅ /dev/cu.usbmodem1101',
            'nfc_status': '📡 Aktiv und bereit'
        }

@app.route('/')
def main():
    status = get_arduino_status()
    return render_template('index.html', result=last_scan_result, **status)

# Entferne die manuelle Web-UI Route - nur Arduino-Scanner erlaubt

@app.route('/nfc/request/<nfc_tag>')
def api_request(nfc_tag):
    """API Route - Original beibehalten"""
    result = csfs.request(nfc_tag)
    return jsonify({"nfc_tag": nfc_tag, "result": result})

@app.route('/api/last-scan')
def api_last_scan():
    """API Route um letztes Scan-Ergebnis abzurufen"""
    return jsonify(last_scan_result if last_scan_result else {"message": "Noch kein Tag gescannt"})

if __name__ == '__main__':
    # Starte NFC-Scanner nur wenn Arduino verbunden ist
    if ser is not None:
        threading.Thread(target=nfc_scan_loop, daemon=True).start()
        print("🚀 NFC-Scanner Thread gestartet")
    
    print("🌐 Web-UI startet auf http://localhost:80")
    app.run(debug=True, host="0.0.0.0", port=80)