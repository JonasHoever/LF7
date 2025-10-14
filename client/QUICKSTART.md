# I2C NFC System - Quick Start Guide

## Setup-Schritte

### 1. Hardware verkabeln
Siehe `WIRING_GUIDE.md` für detaillierte Verkabelung!

**Wichtigste Punkte:**
- ✅ RC522 an **3.3V** (NICHT 5V!)
- ✅ I2C: SDA=A4, SCL=A5, GND gemeinsam
- ✅ Stepper Motor: Externe 5V Versorgung empfohlen

### 2. Arduino-Sketches hochladen

#### Master Arduino (USB zu Raspberry Pi)
```bash
# Arduino IDE öffnen
# Datei: arduino_master_i2c.ino öffnen
# Board: Arduino Uno/Nano/Mega
# Port: /dev/ttyACM0 (oder was angezeigt wird)
# Upload (Strg+U)
```

#### Slave Arduino (I2C zum Master)
```bash
# Arduino IDE öffnen
# Datei: arduino_slave_i2c.ino öffnen
# Board: Arduino Uno/Nano/Mega
# Port: /dev/ttyACM1 (oder was angezeigt wird)
# Upload (Strg+U)
```

### 3. Test ohne Raspberry Pi

**Test-Script verwenden:**
```bash
cd client
python3 test_i2c_system.py
```

**Ablauf:**
1. Script findet Master Arduino automatisch
2. NFC-Tag am Slave scannen
3. UID wird an Master gesendet
4. PIN am Keypad eingeben (4 Ziffern)
5. Script empfängt `UID:xxxxx;PIN:yyyy`
6. Eingabe `ok` → Motor dreht
7. Eingabe `deny` → Zugang verweigert

### 4. Raspberry Pi Integration

**Server starten:**
```bash
cd server
./start_server.sh
```

**Client starten:**
```bash
cd client
./start.sh
```

**Oder manuell:**
```bash
cd client
source venv/bin/activate
python3 app.py
```

### 5. System testen

1. **Browser öffnen:** `http://localhost:5000`
2. **NFC-Tag scannen** am Slave
3. **PIN eingeben** am Keypad (Master)
4. **Raspberry Pi validiert** über Server
5. **Motor dreht** bei erfolgreicher Validierung

## Systemablauf

```
1. [Slave]  NFC-Tag scannen
              ↓
2. [I2C]    UID → Master senden
              ↓
3. [Master] LCD zeigt UID
              ↓
4. [User]   PIN am Keypad eingeben
              ↓
5. [Master] Serial → UID:xxx;PIN:yyy → Raspberry Pi
              ↓
6. [Pi]     Server-Validierung (MariaDB)
              ↓
7. [Pi]     Serial → OK/DENIED → Master
              ↓
8. [Master] I2C → OPEN → Slave (bei OK)
              ↓
9. [Slave]  Motor dreht 90° vor/zurück
```

## Debugging

### Serial Monitor öffnen

**Master Arduino:**
```bash
# Arduino IDE: Tools > Serial Monitor
# Baudrate: 9600
# Zeigt: NFC_DETECTED, UID:xxx;PIN:yyy, etc.
```

**Slave Arduino:**
```bash
# Arduino IDE: Tools > Serial Monitor  
# Baudrate: 9600
# Zeigt: Karte erkannt, I2C -> Master, OPEN-Befehl
```

### I2C Scan (LCD-Adresse finden)

```bash
# Auf Raspberry Pi
sudo apt install i2c-tools
sudo i2cdetect -y 1
```

Ausgabe zeigt alle I2C-Geräte:
- `27` oder `3F` = LCD Display
- `08` = Slave Arduino

### Häufige Probleme

**NFC wird nicht erkannt:**
- RC522 an 3.3V? (NICHT 5V!)
- SPI-Pins korrekt?
- Tag < 3cm vom Reader?

**LCD zeigt nichts:**
- I2C-Adresse korrekt? (0x27 oder 0x3F)
- SDA/SCL vertauscht?
- Kontrast-Potentiometer am LCD drehen

**Motor dreht nicht:**
- Externe 5V Versorgung (min. 1A)?
- Kabel-Reihenfolge: IN1=2, IN2=3, IN3=4, IN4=5?
- `testMotor()` im Sketch aufrufen

**Master empfängt keine UID:**
- I2C GND verbunden?
- Pull-Up Widerstände (4.7kΩ)?
- Slave-Adresse = 0x08?

**Raspberry Pi empfängt nichts:**
- User in dialout Gruppe? `groups $USER`
- Richtiger Port? `ls -l /dev/ttyACM*`
- Serial Monitor geschlossen?

## Pinbelegung Schnellreferenz

### Master Arduino
```
A4     → I2C SDA
A5     → I2C SCL
2-5    → Keypad Spalten
6-9    → Keypad Zeilen
11     → Buzzer (optional)
USB    → Raspberry Pi
```

### Slave Arduino
```
A4     → I2C SDA
A5     → I2C SCL
10     → RC522 SS
9      → RC522 RST
11-13  → RC522 SPI
2-5    → Stepper IN1-4
6      → Status LED
```

## Erweiterte Konfiguration

### PIN-Timeout ändern
```cpp
// In arduino_master_i2c.ino
#define PIN_TIMEOUT 30000  // 30 Sekunden
```

### Motor-Drehung anpassen
```cpp
// In arduino_slave_i2c.ino
#define DOOR_OPEN_STEPS 512   // 90° (2048 = 360°)
#define MOTOR_SPEED 10        // RPM
```

### LCD-Adresse ändern
```cpp
// In arduino_master_i2c.ino
LiquidCrystal_I2C lcd(0x3F, 16, 2);  // Falls nicht 0x27
```

### Buzzer aktivieren
```cpp
// Master Setup:
pinMode(11, OUTPUT);

// Bei ACCESS_GRANTED:
tone(11, 1000, 200);  // 1kHz, 200ms

// Bei ACCESS_DENIED:
tone(11, 200, 500);   // 200Hz, 500ms
```

## Produktions-Tipps

1. **Robuste Stromversorgung**
   - Master: 7-12V DC
   - Slave: 12V 1A DC (wegen Motor)
   - Gemeinsame GND

2. **Kurze I2C-Kabel**
   - < 30cm für stabile Kommunikation
   - Twisted Pair verwenden

3. **Pull-Up Widerstände**
   - 4.7kΩ zwischen SDA/SCL und 5V
   - Reduziert I2C-Fehler

4. **Mechanischer Schutz**
   - Keypad in Gehäuse einbauen
   - LCD mit Schutzglas
   - RC522 vor Wasser schützen

5. **Zugangskontrolle**
   - PIN-Komplexität erhöhen
   - Login-Versuche limitieren (im Server)
   - Timeout nach 3 Fehlversuchen

## Support & Logs

### Python-Logs ansehen
```bash
cd client
./start.sh 2>&1 | tee client.log
```

### Arduino Serial-Logs speichern
```bash
screen /dev/ttyACM0 9600 | tee arduino.log
# Beenden: Ctrl+A dann K
```

### Systemd-Logs (bei Autostart)
```bash
sudo journalctl -u nfc-client -f
```

Viel Erfolg! 🚀
