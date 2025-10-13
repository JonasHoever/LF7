from src import script
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import requests
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime as dt
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

usys = script.UserSystemClient()
csfs = script.Client_Short_Function()  # Original für Terminal
csfs2 = script.Client_Short_Function2()  # Neue Web-UI Version

def find_arduino_port():
    """Finde automatisch den Arduino Port"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'usbmodem' in port.device or 'Arduino' in port.description:
            return port.device
    return None

# Versuche Arduino automatisch zu finden und zu verbinden
ser = None
try:
    # Finde automatisch den Arduino Port
    arduino_port = find_arduino_port()
    
    if arduino_port:
        print(f"🔍 Arduino gefunden auf: {arduino_port}")
        # Robuste Serial-Verbindung mit allen notwendigen Parametern
        ser = serial.Serial(
            port=arduino_port, 
            baudrate=9600, 
            timeout=1,
            writeTimeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        # Warte kurz bis Arduino bereit ist
        time.sleep(2)
        # Leere Input-Buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print(f"✅ Arduino erfolgreich verbunden auf {arduino_port}")
    else:
        print("❌ Kein Arduino-Port gefunden!")
        print("🔌 Verfügbare Ports:")
        for port in serial.tools.list_ports.comports():
            print(f"   - {port.device}: {port.description}")
        
except Exception as e:
    print(f"⚠️  Arduino-Verbindung fehlgeschlagen: {e}")
    print("💡 App läuft nur mit Web-UI (ohne Arduino NFC-Scanner)")
    print("🔌 Schließe Arduino an und starte neu für NFC-Scanner")

def is_valid_nfc_tag(tag):
    """Prüft ob der String eine gültige NFC-Tag-ID ist (nur Hex-Zeichen, 4-20 Zeichen)"""
    if not tag or len(tag) < 4 or len(tag) > 20:
        return False
    # Prüfe ob nur Hex-Zeichen (0-9, A-F)
    return all(c in '0123456789ABCDEF' for c in tag.upper())

def nfc_scanner_thread():
    """Läuft in separatem Thread und liest kontinuierlich vom Arduino"""
    global ser
    
    if not ser:
        print("🚫 Arduino nicht verfügbar - NFC-Scanner-Thread beendet")
        return
    
    print("🚀 NFC-Scanner Thread gestartet")
    
    while True:
        try:
            # Prüfe ob Serial-Verbindung noch aktiv ist
            if not ser or not ser.is_open:
                print("⚠️  Serial-Verbindung verloren - suche Arduino...")
                arduino_port = find_arduino_port()
                if arduino_port:
                    try:
                        ser = serial.Serial(
                            port=arduino_port, 
                            baudrate=9600, 
                            timeout=1,
                            writeTimeout=1,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS
                        )
                        time.sleep(2)
                        ser.reset_input_buffer()
                        ser.reset_output_buffer()
                        print(f"✅ Arduino wiederverbunden auf {arduino_port}")
                    except Exception as e:
                        print(f"❌ Wiederverbindung fehlgeschlagen: {e}")
                        time.sleep(5)
                        continue
                else:
                    print("❌ Arduino nicht gefunden - warte...")
                    time.sleep(5)
                    continue
                
            if ser.in_waiting > 0:
                # Lese eine Zeile vom Arduino
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                nfc_tag = line.strip()
                
                if nfc_tag and is_valid_nfc_tag(nfc_tag):
                    print(f"✅ Gültige NFC-Tag-ID empfangen: {nfc_tag}")
                    # Triggere die Route direkt
                    handle_nfc_request(nfc_tag)
                    time.sleep(1)
                elif nfc_tag:
                    print(f"⚠️  Ungültige Daten ignoriert: {nfc_tag}")
            
            time.sleep(0.1)  # Kurze Pause zwischen Reads
            
        except serial.SerialException as e:
            print(f"❌ Serial-Fehler: {e}")
            print("🔄 Versuche Arduino Wiederverbindung...")
            try:
                if ser and ser.is_open:
                    ser.close()
                time.sleep(3)
                
                # Versuche neuen Port zu finden
                new_port = find_arduino_port()
                if new_port:
                    ser = serial.Serial(
                        port=new_port, 
                        baudrate=9600, 
                        timeout=1,
                        writeTimeout=1,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS
                    )
                    time.sleep(2)
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    print(f"✅ Arduino wiederverbunden auf {new_port}")
                else:
                    print("❌ Arduino-Port nicht gefunden")
                    time.sleep(10)
                    
            except Exception as reconnect_error:
                print(f"❌ Wiederverbindung fehlgeschlagen: {reconnect_error}")
                time.sleep(10)  # Warte länger bei Wiederverbindungsfehlern
        except Exception as e:
            print(f"❌ Fehler beim NFC-Scan: {e}")
            time.sleep(2)  # Kürzere Pause, da das häufig vorkommt

def handle_nfc_request(nfc_tag):
    """Wird aufgerufen wenn NFC-Tag vom Arduino gescannt wird"""
    try:
        print(f"🔍 Prüfe NFC-Tag: {nfc_tag}")
        
        # NUR Web-UI verwenden - KEIN Terminal input()!
        web_result = handle_web_nfc_request(nfc_tag)
        print(f"🌐 Web-UI-Ergebnis für {nfc_tag}: {web_result}")
        
        return web_result
    except Exception as e:
        print(f"❌ Fehler bei NFC-Request: {e}")
        print(f"📍 Exception Details: {type(e).__name__}: {str(e)}")
        handle_web_nfc_request(nfc_tag)  # Speichere auch Fehler
        return None

# Globale Variable für letztes Scan-Ergebnis (für Web-UI Anzeige)
last_scan_result = None
last_scanned_tag = None

def handle_web_nfc_request(nfc_tag):
    """Verarbeitet Arduino NFC-Scanner Daten für Web-UI Anzeige"""
    global last_scan_result, last_scanned_tag
    try:
        print(f"🌐 Web-Request für Tag: {nfc_tag}")
        
        # Speichere den zuletzt gescannten Tag
        last_scanned_tag = nfc_tag
        
        # Sende WebSocket-Nachricht an alle verbundenen Clients
        try:
            socketio.emit('nfc_scanned', {
                'type': 'nfc_scanned',
                'tag_id': nfc_tag,
                'timestamp': time.strftime('%H:%M:%S')
            })
            print(f"📡 WebSocket-Nachricht gesendet für Tag: {nfc_tag}")
        except Exception as ws_error:
            print(f"⚠️  WebSocket-Fehler: {ws_error}")
        
        # DEBUG: Prüfe was csfs2.request() zurückgibt
        print(f"🔧 DEBUG: Rufe csfs2.request('{nfc_tag}') auf...")
        result = csfs2.request(nfc_tag)
        print(f"🔧 DEBUG: csfs2.request() Rückgabe-Typ: {type(result)}")
        print(f"🔧 DEBUG: csfs2.request() Rückgabe-Wert: {result}")
        
        # Erstelle korrektes Web-UI Format basierend auf dem was wir sehen
        if result is None:
            print("⚠️  csfs2.request() gab None zurück - verwende Fallback")
            # Fallback: Verwende csfs für korrekte Daten
            fallback_result = csfs.request(nfc_tag)
            print(f"🔄 Fallback csfs.request() Ergebnis: {fallback_result}")
            result = fallback_result
        
        # Sicherstelle dass result das richtige Format hat
        if result and not isinstance(result, dict):
            print(f"⚠️  Unerwartetes result Format: {result} (Type: {type(result)})")
            # Konvertiere zu Web-UI kompatiblem Format
            result = {
                'status': 'success',
                'message': str(result),
                'nfc_tag': nfc_tag,
                'action_needed': 'none'
            }
        
        print(f"📋 ✅ Final Web-Request Ergebnis: {result}")
        
        last_scan_result = {
            'nfc_tag': nfc_tag,
            'result': result,
            'timestamp': time.strftime('%H:%M:%S'),
            'status': 'success'
        }
        print(f"💾 ✅ GESPEICHERT in last_scan_result: {last_scan_result}")
        return result
    except Exception as e:
        print(f"💥 Exception in Web-Request: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"🔍 Full Traceback: {traceback.format_exc()}")
        
        error_result = {
            'status': 'error',
            'message': f"Fehler bei Tag {nfc_tag}: {str(e)}",
            'action_needed': 'none',
            'nfc_tag': nfc_tag
        }
        last_scan_result = {
            'nfc_tag': nfc_tag,
            'result': error_result,
            'timestamp': time.strftime('%H:%M:%S'),
            'status': 'error'
        }
        print(f"💾 ❌ FEHLER gespeichert in last_scan_result: {last_scan_result}")
        return error_result

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

@app.route('/register')
def register_page():
    status = get_arduino_status()
    return render_template('register.html', **status)

@app.route('/nfc/request/<nfc_tag>')
def api_request(nfc_tag):
    """API Route - Original beibehalten"""
    result = csfs.request(nfc_tag)
    return jsonify({"nfc_tag": nfc_tag, "result": result})

@app.route('/api/last-scan')
def api_last_scan():
    """API Route um letztes Scan-Ergebnis abzurufen"""
    print(f"🌐 API /api/last-scan aufgerufen")
    print(f"📊 last_scan_result: {last_scan_result}")
    response = last_scan_result if last_scan_result else {"message": "Noch kein Tag gescannt"}
    print(f"📤 API Antwort: {response}")
    return jsonify(response)

@app.route('/api/nfc/signup', methods=['POST'])
def api_nfc_signup():
    """API für PIN-Erstellung"""
    data = request.get_json()
    nfc_tag = data.get('nfc_tag')
    pin = data.get('pin')
    pin_confirm = data.get('pin_confirm')
    
    print(f"🔐 PIN-Setup für Tag: {nfc_tag}")
    print(f"📝 PIN: {pin} (Bestätigung: {pin_confirm})")
    
    result = csfs2.web_signup(nfc_tag, pin, pin_confirm)
    print(f"📤 PIN-Setup Ergebnis: {result}")
    
    return jsonify(result)

@app.route('/api/nfc/signin', methods=['POST'])
def api_nfc_signin():
    """API für Login"""
    data = request.get_json()
    nfc_tag = data.get('nfc_tag')
    pin = data.get('pin')
    
    result = csfs2.web_signin(nfc_tag, pin)
    return jsonify(result)

@app.route('/api/nfc/request', methods=['POST'])
def api_nfc_request():
    """API für NFC-Tag Status Prüfung"""
    data = request.get_json()
    nfc_tag = data.get('nfc_tag')
    
    if not nfc_tag:
        return jsonify({"exists": False, "pin_set": False})
    
    result = csfs2.web_request(nfc_tag)
    print(f"🔍 web_request result: {result}")
    
    # Konvertiere das strukturierte Ergebnis zu exists/pin_set Format
    if result["status"] == "not_registered":
        response = {"exists": False, "pin_set": False}
    elif result["status"] == "needs_pin_setup":
        response = {"exists": True, "pin_set": False}
    elif result["status"] == "needs_login":
        response = {"exists": True, "pin_set": True}
    else:
        response = {"exists": False, "pin_set": False}
    
    print(f"🔍 Tag-Status: exists={response['exists']}, pin_set={response['pin_set']}")
    return jsonify(response)

@app.route('/api/user-info', methods=['POST'])
def api_user_info():
    """API für Benutzerinformationen"""
    data = request.get_json()
    nfc_tag = data.get('nfc_tag')
    
    if not nfc_tag:
        return jsonify({"name": "Unknown", "surname": "User"})
    
    # Versuche Benutzerinformationen vom Server zu holen
    try:
        # Da der Server keine direkte User-Info Route hat, verwenden wir ein Mock
        # In einer echten Implementierung sollte der Server eine solche Route haben
        return jsonify({
            "name": "User",
            "surname": f"#{nfc_tag[-4:]}"  # Zeige letzten 4 Zeichen der Tag-ID
        })
    except Exception as e:
        return jsonify({"name": "Unknown", "surname": "User"})

@app.route('/api/nfc/last_scanned')
def api_nfc_last_scanned():
    """API Route um letzten gescannten NFC-Tag abzurufen"""
    global last_scanned_tag
    print(f"🌐 API /api/nfc/last_scanned aufgerufen")
    print(f"📊 last_scanned_tag: {last_scanned_tag}")
    
    if last_scanned_tag:
        response = {
            "success": True,
            "tag_id": last_scanned_tag,
            "timestamp": time.strftime('%H:%M:%S')
        }
    else:
        response = {
            "success": False,
            "message": "Noch kein Tag gescannt"
        }
    
    print(f"📤 API Antwort: {response}")
    return jsonify(response)

@app.route('/api/nfc/register', methods=['POST'])
def api_nfc_register():
    """API für NFC-Tag Registrierung"""
    data = request.get_json()
    nfc_tag = data.get('nfc_tag')
    name = data.get('name')
    surname = data.get('surname')
    
    print(f"🆕 Registrierungsanfrage: Tag={nfc_tag}, Name={name}, Surname={surname}")
    
    if not nfc_tag or not name or not surname:
        return jsonify({
            "success": False,
            "message": "NFC-Tag, Name und Nachname sind erforderlich!"
        })
    
    try:
        # Sende Anfrage an Server
        server_url = f"http://192.180.160.5:4001/nfc/register/{nfc_tag}/{name}/{surname}"
        print(f"📡 Sende an Server: {server_url}")
        
        response = requests.get(server_url)
        print(f"📨 Server Antwort: Status={response.status_code}, Text={response.text}")
        
        if response.status_code == 200:
            print(f"✅ Registrierung erfolgreich für Tag: {nfc_tag}")
            return jsonify({
                "success": True,
                "message": f"NFC-Tag {nfc_tag} für {name} {surname} wurde erfolgreich registriert!"
            })
        else:
            print(f"❌ Registrierung fehlgeschlagen: {response.status_code} - {response.text}")
            return jsonify({
                "success": False,
                "message": f"Fehler bei der Registrierung (Status {response.status_code}): {response.text}"
            })
    except Exception as e:
        print(f"💥 Exception bei Registrierung: {type(e).__name__}: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Verbindungsfehler: {str(e)}"
        })
    
@app.route("/welcome/<uid>/")
def welcome_site(uid):
    success, action, start_time, end_time, diff = usys.worktime_script(uid)
    name, surname = usys.get_name_by_id(uid)
    name_full = (name or "")+" "+(surname or "")
    if success == True and action == "started":
        return render_template('session_started.html', name_full=name_full, start_time=start_time)
    elif success == True and action == "stopped":
        return render_template('session_stopped.html', name_full=name_full, start_time=start_time, end_time=end_time, diff=diff)
    else:
        return render_template('welcome.html', uid=uid, success=success, action=action)

@app.route('/test/<name>/<int:alter>')
def user_profile(name, alter):
    """Beispiel-Route mit URL-Parametern"""
    status = get_arduino_status()
    return render_template('test.html', name=name, alter=alter, **status)

# WebSocket Event Handler
@socketio.on('connect')
def handle_connect():
    print('🔌 Client mit WebSocket verbunden')
    emit('status', {'message': 'Verbunden mit NFC-Scanner'})

@socketio.on('disconnect')
def handle_disconnect():
    print('🔌 Client von WebSocket getrennt')

if __name__ == '__main__':
    # Starte NFC-Scanner nur wenn Arduino verbunden ist
    if ser is not None:
        threading.Thread(target=nfc_scanner_thread, daemon=True).start()
        print("🚀 NFC-Scanner Thread gestartet")
    
    print("🌐 Web-UI startet auf http://localhost:5000")
    print("📡 WebSocket verfügbar auf ws://localhost:5000/ws")
    socketio.run(app, debug=True, host="0.0.0.0", port=80)