#!/usr/bin/env python3
"""
Arduino Test Script - Prüft Serial-Verbindung
"""
import serial
import time

def test_arduino():
    try:
        # Verbinde mit Arduino
        ser = serial.Serial('/dev/cu.usbmodem1101', 9600, timeout=2)
        print("✅ Arduino verbunden auf /dev/cu.usbmodem1101")
        
        # Warte bis Arduino bereit ist
        print("⏳ Warte 3 Sekunden bis Arduino bereit ist...")
        time.sleep(3)
        
        # Leere Buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print("👂 Höre 10 Sekunden auf Arduino-Nachrichten...")
        print("📱 Jetzt NFC-Tag an Arduino halten!")
        print("-" * 50)
        
        start_time = time.time()
        while (time.time() - start_time) < 10:
            if ser.in_waiting > 0:
                try:
                    raw_data = ser.readline()
                    data = raw_data.decode('utf-8', errors='ignore').strip()
                    print(f"📡 RAW: {raw_data}")
                    print(f"📝 DECODED: '{data}'")
                    print("-" * 30)
                except Exception as decode_error:
                    print(f"❌ Decode-Fehler: {decode_error}")
            time.sleep(0.1)
        
        print("🏁 Test beendet")
        ser.close()
        
    except Exception as e:
        print(f"❌ Arduino Test fehlgeschlagen: {e}")
        print(f"🔍 Exception Details: {type(e).__name__}")

if __name__ == "__main__":
    test_arduino()