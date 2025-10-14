"""
I2C Test Script - Prüft Master-Slave Kommunikation
Simuliert Raspberry Pi Seite für Test ohne volle Flask App
"""

import serial
import serial.tools.list_ports
import time
import sys

def find_arduino_port():
    """Finde automatisch den Arduino Port"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        desc = f"{port.device} {port.description}".lower()
        if any(k in desc for k in ['usbmodem', 'usbserial', 'wchusbserial', 'ttyacm', 'ttyusb', 'arduino', 'ch340', 'cp210', 'com']):
            return port.device
    return None

def main():
    print("=" * 50)
    print("I2C MASTER-SLAVE TEST SCRIPT")
    print("=" * 50)
    print()
    
    # Finde Arduino
    print("🔍 Suche Master Arduino...")
    port = find_arduino_port()
    
    if not port:
        print("❌ Kein Arduino gefunden!")
        print("\n📋 Verfügbare Ports:")
        for p in serial.tools.list_ports.comports():
            print(f"   - {p.device}: {p.description}")
        sys.exit(1)
    
    print(f"✅ Arduino gefunden: {port}")
    
    # Öffne Serial-Verbindung
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Warte auf Arduino Reset
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print("✅ Serial-Verbindung hergestellt")
    except Exception as e:
        print(f"❌ Fehler beim Öffnen: {e}")
        sys.exit(1)
    
    print()
    print("=" * 50)
    print("TEST-MODUS AKTIV")
    print("=" * 50)
    print()
    print("Ablauf:")
    print("1. Lege NFC-Tag am Slave-Arduino auf")
    print("2. Master zeigt UID an und fordert PIN")
    print("3. Gib PIN am Keypad ein (4 Ziffern)")
    print("4. Dieses Script empfängt UID + PIN")
    print("5. Script sendet OK/DENIED zurück")
    print("6. Motor dreht bei OK")
    print()
    print("Befehle:")
    print("  'ok'     - Sende ACCESS_GRANTED")
    print("  'deny'   - Sende ACCESS_DENIED")
    print("  'quit'   - Beenden")
    print()
    print("-" * 50)
    print()
    
    test_mode = False
    current_uid = None
    
    try:
        while True:
            # Lese vom Arduino
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if not line:
                    continue
                
                print(f"\n📥 Arduino: {line}")
                
                # Parse Nachricht
                if line.startswith("MASTER_READY"):
                    print("✅ Master Arduino bereit!")
                    
                elif line.startswith("NFC_DETECTED:"):
                    uid = line.split(":")[1].strip()
                    current_uid = uid
                    print(f"🏷️  NFC-Tag erkannt: {uid}")
                    print("⏳ Warte auf PIN-Eingabe am Keypad...")
                    
                elif line.startswith("UID:") and ";PIN:" in line:
                    # UID und PIN empfangen
                    parts = line.split(";")
                    uid_part = parts[0]
                    pin_part = parts[1]
                    
                    uid = uid_part.split(":")[1].strip()
                    pin = pin_part.split(":")[1].strip()
                    
                    print()
                    print("=" * 50)
                    print("🔐 AUTHENTIFIZIERUNG")
                    print("=" * 50)
                    print(f"UID: {uid}")
                    print(f"PIN: {'*' * len(pin)} (Länge: {len(pin)})")
                    print()
                    
                    # Automatische Validierung (Test-Modus)
                    if test_mode:
                        print("🤖 Test-Modus: Automatisch OK")
                        ser.write(b"ACCESS_GRANTED\n")
                    else:
                        print("Manuelle Eingabe:")
                        print("  'ok'   - Zugang gewähren")
                        print("  'deny' - Zugang verweigern")
                        
                        while True:
                            cmd = input("\nBefehl: ").strip().lower()
                            
                            if cmd == 'ok':
                                print("✅ Sende ACCESS_GRANTED an Master")
                                ser.write(b"ACCESS_GRANTED\n")
                                break
                            elif cmd == 'deny':
                                print("❌ Sende ACCESS_DENIED an Master")
                                ser.write(b"ACCESS_DENIED\n")
                                break
                            elif cmd == 'quit':
                                print("👋 Beende...")
                                ser.close()
                                sys.exit(0)
                            else:
                                print("⚠️  Ungültiger Befehl!")
                    
                    print()
                    print("-" * 50)
                    
                elif line.startswith("SENDING_OPEN_TO_SLAVE"):
                    print("🚪 Master sendet OPEN-Befehl an Slave")
                    print("🔄 Motor sollte sich jetzt drehen...")
                    
                elif line.startswith("SERVER_TIMEOUT"):
                    print("⏱️  Timeout: Keine Antwort innerhalb 10 Sekunden")
                    
                else:
                    print(f"ℹ️  {line}")
            
            # Kommandozeilen-Eingabe (non-blocking würde besser sein)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Programm beendet (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial-Verbindung geschlossen")

if __name__ == "__main__":
    main()
