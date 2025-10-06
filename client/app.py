from src import script
from flask import Flask, jsonify
import requests
import serial
import threading
import time

app = Flask(__name__)

usys = script.Usersystem_client()

# Passe den Port und die Baudrate an deinen Arduino an!
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

def nfc_scan_loop():
    while True:
        if ser.in_waiting > 0:
            nfc_tag = ser.readline().decode('utf-8').strip()
            if nfc_tag:
                result = usys.request(nfc_tag)
                print(f"Scan-Ergebnis: {result}")
                time.sleep(1)

@app.route('/')
def main():
    return "Client läuft!"

if __name__ == '__main__':
    threading.Thread(target=nfc_scan_loop, daemon=True).start()
    app.run(debug=True, host="0.0.0.0", port=80)