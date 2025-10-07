import serial

ser = serial.Serial('/dev/tty.usbmodem1201', 9600, timeout=1)

print("Warte auf NFC-Tag...")

while True:
    if ser.in_waiting > 0:
        nfc_tag = ser.readline().decode('utf-8').strip()
        if nfc_tag:
            print(f"NFC-Tag erkannt: {nfc_tag}")