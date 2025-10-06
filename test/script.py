import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

while True:
    if ser.in_waiting > 0:
        nr = ser.read(1)
        print("Folgender char wurde empfangen: ", int.from_bytes(nr, "big"))