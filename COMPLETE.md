# 🎉 I2C NFC SYSTEM - KOMPLETT!

## ✅ Was wurde erstellt?

### 1️⃣ **Arduino Sketches**

#### Master Arduino (`arduino_master_i2c.ino`)
- ✅ I2C Master-Modus
- ✅ LCD Display 16x2 (I2C)
- ✅ 4x4 Matrix Keypad
- ✅ State Machine mit 5 Zuständen
- ✅ Serial-Kommunikation zu Raspberry Pi (9600 baud)
- ✅ PIN-Eingabe mit Timeout (30s)
- ✅ Server-Response Timeout (10s)
- ✅ Buzzer-Support (Pin 11)
- ✅ Sendet: `UID:xxxxx;PIN:yyyy` an Pi
- ✅ Empfängt: `ACCESS_GRANTED` / `ACCESS_DENIED`
- ✅ Sendet: `OPEN` an Slave bei Erfolg

#### Slave Arduino (`arduino_slave_i2c.ino`)
- ✅ I2C Slave-Modus (Adresse 0x08)
- ✅ MFRC522 NFC Reader (SPI)
- ✅ 28BYJ-48 Stepper Motor
- ✅ Status-LED (Pin 6)
- ✅ Scannt NFC-Tags (13.56MHz)
- ✅ Sendet UID via I2C an Master
- ✅ Empfängt OPEN-Befehl
- ✅ Dreht Motor 90° vor/zurück
- ✅ Cooldown-Logik (2s zwischen Scans)

### 2️⃣ **Python Integration**

#### Client App (`client/app.py`)
- ✅ Serial-Thread für Master-Arduino
- ✅ Parst `UID:xxx;PIN:yyy` Nachrichten
- ✅ Neue Funktion: `validate_nfc_and_pin(uid, pin)`
- ✅ Server-API Validierung
- ✅ WorkTime-System Integration
- ✅ Sendet `ACCESS_GRANTED` / `ACCESS_DENIED` zurück
- ✅ WebSocket-Events für Live-Updates
- ✅ Raspberry Pi OS Port-Erkennung

### 3️⃣ **Installation & Scripts**

#### Raspberry Pi Setup
- ✅ `install.sh` - Client venv + Dependencies
- ✅ `start.sh` - Client starten mit Auto-Port-Detection
- ✅ `install_server.sh` - Server venv + Dependencies
- ✅ `start_server.sh` - Server starten mit DB-Check
- ✅ `quick_setup.sh` - One-Click Installation
- ✅ `requirements.txt` - Python Packages
- ✅ `.env.example` - Konfigurationsvorlagen

### 4️⃣ **Dokumentation**

- ✅ `WIRING_GUIDE.md` - Komplette Verkabelungsanleitung
- ✅ `QUICKSTART.md` - Schnellstart-Guide
- ✅ `ARCHITECTURE.md` - System-Diagramme + Ablauf
- ✅ `README.md` - Haupt-Dokumentation
- ✅ `test_i2c_system.py` - Standalone Test-Script

---

## 🚀 Wie starte ich?

### Methode 1: Vollständiges System

```bash
# 1. Raspberry Pi vorbereiten
cd ~/projekt
./quick_setup.sh

# 2. Datenbank einrichten
cd server
mysql -u root -p < src/db_setup.sql

# 3. Konfiguration
nano server/.env  # DB_PASS eintragen
nano client/.env  # SERVER_URL eintragen

# 4. Starten
cd server && ./start_server.sh &
cd client && ./start.sh
```

### Methode 2: Nur Arduino Test (ohne Pi)

```bash
# 1. Beide Arduino-Sketches hochladen
# 2. Test-Script starten
cd client
python3 test_i2c_system.py

# 3. NFC scannen, PIN eingeben
# 4. Im Terminal: 'ok' oder 'deny' eingeben
```

---

## 🔌 Hardware-Checkliste

### Master Arduino
- [ ] LCD 16x2 I2C (SDA=A4, SCL=A5)
- [ ] 4x4 Keypad (Pins 2-9)
- [ ] USB zu Raspberry Pi
- [ ] I2C zu Slave (SDA, SCL, GND)
- [ ] Optional: Buzzer (Pin 11)

### Slave Arduino
- [ ] MFRC522 (3.3V!, SPI: SS=10, RST=9)
- [ ] Stepper 28BYJ-48 (Pins 2-5)
- [ ] LED + 220Ω (Pin 6)
- [ ] I2C zu Master (SDA, SCL, GND)
- [ ] Externe 5V 1A Versorgung

### I2C Bus
- [ ] Pull-Up Widerstände (2x 4.7kΩ)
- [ ] SDA Master ↔ SDA Slave
- [ ] SCL Master ↔ SCL Slave
- [ ] GND gemeinsam

---

## 📡 Kommunikationsprotokoll

### Master → Raspberry Pi (Serial)
```
MASTER_READY                    # Startup
NFC_DETECTED:4A3B2C1D          # NFC gescannt
UID:4A3B2C1D;PIN:1234          # PIN eingegeben
SENDING_OPEN_TO_SLAVE          # Motor-Befehl gesendet
SERVER_TIMEOUT                 # Keine Antwort
```

### Raspberry Pi → Master (Serial)
```
ACCESS_GRANTED                 # Login OK
ACCESS_DENIED                  # Login Fehler
OK                             # Alternative OK
DENIED                         # Alternative Deny
```

### Master → Slave (I2C)
```
(Request)                      # Master fragt nach UID
OPEN                          # Motor aktivieren
```

### Slave → Master (I2C)
```
UID:4A3B2C1D\n                # NFC-Tag UID
NONE\n                        # Kein Tag vorhanden
```

---

## 🎯 Systemablauf (Schritt für Schritt)

1. **User:** Legt NFC-Tag auf Slave-Reader
2. **Slave:** Scannt UID, LED blinkt 3x
3. **I2C:** Slave sendet `UID:xxx` an Master
4. **Master:** LCD zeigt "PIN eingeben: ____"
5. **User:** Gibt 4-stellige PIN am Keypad ein
6. **Master:** Sendet `UID:xxx;PIN:yyyy` an Raspberry Pi
7. **Pi:** Validiert via MariaDB Server
8. **Pi:** Sendet `ACCESS_GRANTED` oder `ACCESS_DENIED`
9. **Master:** Bei GRANTED → LCD "Willkommen!", Buzzer 1kHz
10. **Master:** Sendet `OPEN` via I2C an Slave
11. **Slave:** LED an, Motor dreht 90° vor → 1s warten → 90° zurück
12. **Slave:** LED aus, bereit für nächsten Scan

---

## 🐛 Debugging

### Serial Monitor checken

**Master:**
```bash
# Arduino IDE → Serial Monitor → 9600 baud
# Zeigt: MASTER_READY, NFC_DETECTED, UID:xxx;PIN:yyy
```

**Slave:**
```bash
# Arduino IDE → Serial Monitor → 9600 baud
# Zeigt: Karte erkannt, I2C -> Master, OPEN-Befehl
```

### I2C Scan
```bash
sudo i2cdetect -y 1
# Sollte zeigen:
#   08 = Slave Arduino
#   27 = LCD Display (oder 3F)
```

### Python Debug
```bash
cd client
python3 app.py
# Zeigt: 📥 Arduino: ..., 🔐 Validierung, ✅/❌ Ergebnis
```

---

## ⚠️ Wichtige Hinweise

### 🔴 KRITISCH: RC522 Spannung
```
⚡ NUR 3.3V für RC522!
❌ 5V ZERSTÖRT das Modul!
✅ 3.3V Pin vom Arduino verwenden
```

### 🟡 Stromversorgung
```
⚠️ Stepper Motor braucht min. 1A
🔌 Externe 5V Versorgung empfohlen
⚡ Nicht über USB betreiben (Spannungseinbrüche)
```

### 🟢 I2C Best Practices
```
✅ Pull-Up Widerstände: 4.7kΩ
✅ Kurze Kabel: < 30cm
✅ Keine Adresskonflikte
✅ GND gemeinsam verbinden
```

---

## 📊 Pinbelegung Übersicht

```
MASTER ARDUINO UNO
═══════════════════
A4      → I2C SDA
A5      → I2C SCL
2-5     → Keypad Spalten
6-9     → Keypad Zeilen
11      → Buzzer (optional)
USB     → Raspberry Pi

SLAVE ARDUINO UNO
══════════════════
A4      → I2C SDA
A5      → I2C SCL
2       → Stepper IN1
3       → Stepper IN2
4       → Stepper IN3
5       → Stepper IN4
6       → Status LED
9       → RC522 RST
10      → RC522 SS (SDA)
11      → RC522 MOSI
12      → RC522 MISO
13      → RC522 SCK
3.3V    → RC522 VCC
```

---

## 🎓 Erweiterte Features

### Buzzer-Feedback aktivieren
```cpp
// In arduino_master_i2c.ino setup():
pinMode(11, OUTPUT);

// Bereits implementiert:
tone(11, 1000, 200);  // Erfolg
tone(11, 200, 500);   // Fehler
```

### LCD-Adresse ändern
```cpp
// Falls LCD nicht auf 0x27:
LiquidCrystal_I2C lcd(0x3F, 16, 2);
```

### Motor-Drehung anpassen
```cpp
// In arduino_slave_i2c.ino:
#define DOOR_OPEN_STEPS 1024  // 180° statt 90°
#define MOTOR_SPEED 15        // Schneller
```

### PIN-Timeout ändern
```cpp
// In arduino_master_i2c.ino:
#define PIN_TIMEOUT 60000  // 60 Sekunden
```

---

## 🎉 FERTIG!

Das komplette System ist einsatzbereit:

✅ Master-Slave I2C Kommunikation  
✅ NFC-Scanner mit UID-Extraktion  
✅ PIN-Eingabe via Keypad  
✅ Raspberry Pi Validierung  
✅ Stepper Motor Ansteuerung  
✅ LCD Feedback + Buzzer  
✅ WebSocket Live-Updates  
✅ Worktime-System Integration  
✅ Automatische Port-Erkennung  
✅ Fehlerbehandlung + Timeouts  
✅ Vollständige Dokumentation  

**Viel Erfolg beim Aufbau! 🚀**

---

## 📞 Support

Bei Problemen:
1. `WIRING_GUIDE.md` → Verkabelung prüfen
2. `QUICKSTART.md` → Troubleshooting-Sektion
3. `test_i2c_system.py` → Standalone-Test
4. Serial Monitor → Debug-Ausgaben checken
5. `i2cdetect -y 1` → I2C-Geräte scannen

**GitHub Issues:** Für Bugs und Feature-Requests
