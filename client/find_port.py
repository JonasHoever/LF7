#!/usr/bin/env python3
import serial.tools.list_ports

print("🔍 Suche nach Arduino-Ports...")
print("=" * 40)

ports = serial.tools.list_ports.comports()
arduino_ports = []

for port in ports:
    print(f"Port: {port.device}")
    print(f"  Beschreibung: {port.description}")
    print(f"  Hardware ID: {port.hwid}")
    
    # Prüfe ob es ein Arduino ist
    if any(keyword in port.description.lower() for keyword in ['arduino', 'usb', 'serial']):
        if 'usbmodem' in port.device:
            arduino_ports.append(port.device)
            print(f"  ✅ Arduino gefunden!")
    print("-" * 30)

print("\n🎯 Arduino-Ports gefunden:")
for port in arduino_ports:
    print(f"  📌 {port}")

if arduino_ports:
    print(f"\n💡 Verwende diesen Port in deiner app.py:")
    print(f"   ser = serial.Serial('{arduino_ports[0]}', 9600, timeout=1)")
else:
    print("\n❌ Kein Arduino gefunden. Stelle sicher, dass:")
    print("   - Arduino angeschlossen ist")
    print("   - Arduino-Treiber installiert sind")
    print("   - Arduino IDE den Arduino erkennt")