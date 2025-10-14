# NFC Worktime System - I2C Master-Slave mit Raspberry Pi

Ein **vollständig integriertes NFC-Zugangskontrollsystem** mit Arduino I2C-Bus, Keypad-PIN-Eingabe, Stepper-Motor-Drehkreuz und Raspberry Pi Backend.

## 🎯 System-Übersicht

```
┌─────────────┐  USB Serial  ┌──────────────┐  I2C Bus  ┌──────────────┐
│ Raspberry   │◄────────────►│   Master     │◄─────────►│    Slave     │
│     Pi      │              │   Arduino    │           │   Arduino    │
│             │              │              │           │              │
│ - Flask     │              │ - LCD 16x2   │           │ - RC522 NFC  │
│ - MariaDB   │              │ - 4x4 Keypad │           │ - Stepper    │
│ - Python    │              │ - Buzzer     │           │ - LED        │
└─────────────┘              └──────────────┘           └──────────────┘
```

## ✨ Features

- ✅ **I2C Master-Slave Kommunikation** zwischen zwei Arduinos
- ✅ **NFC-Authentifizierung** mit MFRC522 (13.56MHz MIFARE Tags)
- ✅ **PIN-Eingabe** über 4x4 Matrix Keypad
- ✅ **LCD Display** mit Echtzeit-Feedback (16x2 I2C)
- ✅ **Stepper Motor** Drehkreuz-Steuerung (28BYJ-48)
- ✅ **Raspberry Pi Backend** mit Flask + MariaDB
- ✅ **Arbeitszeiterfassung** automatisch beim Ein-/Auschecken
- ✅ **Web Interface** für Verwaltung und Monitoring
- ✅ **Buzzer Feedback** für akustische Bestätigung
- ✅ **Timeout-Handling** und Fehlerbehandlung

## 📦 Hardware-Komponenten

### Master Arduino (USB zu Raspberry Pi)
- Arduino Uno/Nano/Mega
- I2C LCD Display 16x2 (Adresse 0x27 oder 0x3F)
- 4x4 Matrix Keypad
- Buzzer (optional, Pin 11)
- USB-Kabel zu Raspberry Pi

### Slave Arduino (I2C zum Master)
- Arduino Uno/Nano/Mega
- MFRC522 NFC Reader (⚠️ **3.3V!**)
- 28BYJ-48 Stepper Motor + ULN2003 Driver
- Status-LED + 220Ω Widerstand
- Externe 5V Stromversorgung (min. 1A)

### I2C Bus
- 2x 4.7kΩ Pull-Up Widerstände (SDA, SCL)
- Kurze Kabel (< 30cm)
- Gemeinsame GND-Verbindung

### Raspberry Pi
- Raspberry Pi 3B+ / 4 / Zero 2 W
- microSD-Karte (min. 8GB)
- Netzteil 5V 3A

## 🚀 Quick Start

### Schnellinstallation (Alles in einem)
```bash
cd ~/projekt
./quick_setup.sh
```

### Manuelle Installation

#### 1. Raspberry Pi vorbereiten
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git mariadb-server -y
```

#### 2. Hardware verkabeln
**Siehe `WIRING_GUIDE.md` für detaillierte Verkabelung!**

**Wichtigste Punkte:**
- RC522 an **3.3V** (NICHT 5V!)
- I2C: SDA=A4, SCL=A5, GND gemeinsam
- Pull-Up Widerstände: 2x 4.7kΩ
- Stepper: Externe 5V Versorgung

#### 3. Arduino Sketches hochladen
```bash
# In Arduino IDE:
# 1. Öffne client/arduino_master_i2c.ino → Upload auf Master
# 2. Öffne client/arduino_slave_i2c.ino → Upload auf Slave
```

#### 4. System testen (ohne Raspberry Pi)
```bash
cd client
python3 test_i2c_system.py
# Scanne NFC → Gib PIN ein → Tippe 'ok' oder 'deny'
```

#### 5. Raspberry Pi Integration
```bash
# Server starten
cd server
./install_server.sh
mysql -u root -p < src/db_setup.sql
cp .env.example .env
nano .env  # DB_PASS eintragen
./start_server.sh

# Client starten (neues Terminal)
cd client
./install.sh
cp .env.example .env
nano .env  # SERVER_URL eintragen
./start.sh
```

#### 6. Browser öffnen
```
http://localhost:5000
```

## 📖 Dokumentation

| Datei | Beschreibung |
|-------|--------------|
| **COMPLETE.md** | ✅ Vollständige Projektübersicht |
| **QUICKSTART.md** | 🚀 Schnellstart-Anleitung |
| **WIRING_GUIDE.md** | 🔌 Detaillierte Verkabelung |
| **ARCHITECTURE.md** | 📐 System-Diagramme + Ablauf |
| **PINOUT.md** | 📍 Pin-Belegungen aller Komponenten |
| **README.md** | 📚 Diese Datei |

## 🎬 Systemablauf

1. **User** legt NFC-Tag auf Slave-Reader
2. **Slave** scannt UID, blinkt 3x mit LED
3. **I2C** Slave sendet `UID:xxxxx` an Master
4. **Master** zeigt auf LCD: "PIN eingeben: ____"
5. **User** gibt 4-stellige PIN am Keypad ein
6. **Master** sendet `UID:xxxxx;PIN:yyyy` an Raspberry Pi (Serial)
7. **Pi** validiert über MariaDB Server
8. **Pi** sendet `ACCESS_GRANTED` oder `ACCESS_DENIED` zurück
9. **Master** zeigt auf LCD: "Willkommen!" (bei Erfolg)
10. **Master** sendet `OPEN` via I2C an Slave
11. **Slave** dreht Motor 90° vor → 1s → 90° zurück
12. **System** bereit für nächsten Scan

## 🔧 Konfiguration

### Master Arduino
```cpp
// In arduino_master_i2c.ino:
#define SLAVE_ADDRESS 0x08           // I2C Slave-Adresse
#define PIN_LENGTH 4                 // PIN-Länge
#define PIN_TIMEOUT 30000            // 30s Timeout
LiquidCrystal_I2C lcd(0x27, 16, 2); // LCD-Adresse (ggf. 0x3F)
```

### Slave Arduino
```cpp
// In arduino_slave_i2c.ino:
#define SLAVE_ADDRESS 0x08           // I2C Adresse
#define DOOR_OPEN_STEPS 512          // 90° Drehung (2048 = 360°)
#define MOTOR_SPEED 10               // RPM
```

### Raspberry Pi Client
```bash
# client/.env
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SERVER_URL=http://localhost:5001
ARDUINO_BAUDRATE=9600
```

### Raspberry Pi Server
```bash
# server/.env
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
DB_HOST=localhost
DB_USER=root
DB_PASS=your_password
DB_NAME=pro1
```

## 🐛 Troubleshooting

### NFC wird nicht erkannt
```bash
# Prüfe RC522 Spannung (MUSS 3.3V sein!)
# Prüfe SPI-Pins (SS=10, RST=9, MOSI=11, MISO=12, SCK=13)
# Tag < 3cm vom Reader halten
```

### LCD zeigt nichts
```bash
# I2C-Adresse scannen
sudo i2cdetect -y 1
# Falls nicht 0x27, im Code ändern: lcd(0x3F, 16, 2)
```

### Motor dreht nicht
```bash
# Externe 5V Versorgung (min. 1A) anschließen
# Kabelreihenfolge prüfen: IN1=2, IN2=3, IN3=4, IN4=5
```

### Arduino nicht gefunden
```bash
# User zur dialout Gruppe hinzufügen
sudo usermod -a -G dialout $USER
# Neu einloggen
logout
```

### I2C funktioniert nicht
```bash
# Pull-Up Widerstände prüfen (4.7kΩ)
# SDA/SCL nicht vertauscht?
# GND gemeinsam verbunden?
# Kurze Kabel verwenden (< 30cm)
```

## 📡 Serial Protokoll

### Master → Raspberry Pi
```
MASTER_READY                    # Startup
NFC_DETECTED:4A3B2C1D          # NFC gescannt
UID:4A3B2C1D;PIN:1234          # PIN eingegeben
SENDING_OPEN_TO_SLAVE          # Motor-Befehl
SERVER_TIMEOUT                 # Keine Antwort
```

### Raspberry Pi → Master
```
ACCESS_GRANTED                 # Login erfolgreich
ACCESS_DENIED                  # Falsches Passwort/User
```

### Master → Slave (I2C)
```
(Request)                      # Fragt nach UID
OPEN                          # Motor aktivieren
```

### Slave → Master (I2C)
```
UID:4A3B2C1D\n                # NFC-Tag UID
NONE\n                        # Kein Tag vorhanden
```

## 🔒 Sicherheit

- **PIN-Verschlüsselung**: Argon2 Hash in Datenbank
- **UID-Verschlüsselung**: Fernet (AES) für URLs
- **SQL Injection**: Prepared Statements
- **Timeout-Protection**: 30s PIN, 10s Server
- **Login-Versuche**: Im Server limitieren (TODO)

## 🎓 Erweiterte Features

### Buzzer aktivieren
```cpp
// In Master setup():
pinMode(11, OUTPUT);

// Bei Erfolg/Fehler (bereits implementiert):
tone(11, 1000, 200);  // Erfolg: 1kHz
tone(11, 200, 500);   // Fehler: 200Hz
```

### Motor-Drehung anpassen
```cpp
// In Slave:
#define DOOR_OPEN_STEPS 1024  // 180° statt 90°
#define MOTOR_SPEED 15        // Schneller drehen
```

### PIN-Länge ändern
```cpp
// In Master:
#define PIN_LENGTH 6  // 6-stellige PIN
```

## 🎉 Credits

- **MFRC522 Library**: miguelbalboa/rfid
- **LiquidCrystal I2C**: johnrickman/LiquidCrystal_I2C
- **Keypad Library**: Chris--A/Keypad
- **Flask**: Pallets Projects
- **pyserial**: Python Serial Port Extension

## 📄 Lizenz

MIT License

## 🆘 Support

Bei Problemen:
1. Prüfe Verkabelung (`WIRING_GUIDE.md`)
2. Serial Monitor checken (9600 baud)
3. I2C-Scan durchführen: `sudo i2cdetect -y 1`
4. Test-Script ausführen: `python3 test_i2c_system.py`
5. GitHub Issue erstellen

---

### RC522 Verkabelung (Arduino Uno)

| RC522 | Arduino Uno | Hinweis |
|-------|-------------|---------|
| SDA   | Pin 10      | SS      |
| SCK   | Pin 13      | SCK     |
| MOSI  | Pin 11      | MOSI    |
| MISO  | Pin 12      | MISO    |
| GND   | GND         |         |
| RST   | Pin 9       | Reset   |
| 3.3V  | 3.3V        | **WICHTIG: 3.3V nicht 5V!** |

## Installation

### 1. Raspberry Pi OS vorbereiten

```bash
# System Update
sudo apt update && sudo apt upgrade -y

# Git installieren (falls nicht vorhanden)
sudo apt install git -y

# Repository klonen
cd ~
git clone <your-repo-url>
cd <project-folder>
```

### 2. MariaDB Server installieren

```bash
# MariaDB installieren
sudo apt install mariadb-server -y

# MariaDB Sicherheit einrichten
sudo mysql_secure_installation

# Root Passwort setzen und unsichere Defaults entfernen
```

### 3. Datenbank einrichten

```bash
cd server

# Datenbank Schema erstellen
mysql -u root -p < src/db_setup.sql
# Oder mit Python Script:
# python3 src/db_setup.py
```

### 4. Server installieren

```bash
cd server

# Dependencies installieren
./install_server.sh

# .env Konfiguration erstellen
cp .env.example .env
nano .env  # DB Passwort eintragen

# Server testen
./start_server.sh
```

Server läuft auf: `http://localhost:5001`

### 5. Client installieren

```bash
cd ../client

# Dependencies installieren
./install_client.sh

# .env Konfiguration erstellen
cp .env.example .env
nano .env  # SERVER_URL anpassen (z.B. http://192.168.1.100:5001)

# Arduino anschließen und User zur dialout Gruppe hinzufügen
sudo usermod -a -G dialout $USER
# Danach neu einloggen (logout/login oder reboot)

# Client testen
./start.sh
```

Client läuft auf: `http://localhost:5000`

## Arduino Setup

### 1. Arduino IDE installieren (optional, für Entwicklung)

```bash
# Arduino IDE 2.x
wget https://downloads.arduino.cc/arduino-ide/arduino-ide_2.x_Linux_64bit.AppImage
chmod +x arduino-ide_*.AppImage
```

### 2. Arduino Sketch hochladen

1. Arduino IDE öffnen
2. `client/arduino_nfc_scanner.ino` öffnen
3. Board auswählen: Tools > Board > Arduino Uno
4. Port auswählen: Tools > Port > /dev/ttyACM0
5. Upload (Strg+U)

### 3. Serial Port Rechte

```bash
# User zur dialout Gruppe hinzufügen
sudo usermod -a -G dialout $USER

# Neu einloggen damit Änderung wirksam wird
```

## Port Erkennung

Das System erkennt automatisch den Arduino Port:

- **macOS**: `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`
- **Linux/Raspberry Pi**: `/dev/ttyACM*`, `/dev/ttyUSB*`
- **Windows**: `COM*` (experimentell)

Unterstützte USB-Serial Chips:
- FTDI (FT232, FT2232)
- CH340/CH341
- CP210x
- Original Arduino

## Autostart (systemd)

### Server als Service

```bash
sudo nano /etc/systemd/system/nfc-server.service
```

```ini
[Unit]
Description=NFC Worktime Server
After=network.target mariadb.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/<project>/server
ExecStart=/home/pi/<project>/server/start_server.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nfc-server
sudo systemctl start nfc-server
```

### Client als Service

```bash
sudo nano /etc/systemd/system/nfc-client.service
```

```ini
[Unit]
Description=NFC Worktime Client
After=network.target nfc-server.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/<project>/client
ExecStart=/home/pi/<project>/client/start.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable nfc-client
sudo systemctl start nfc-client
```

### Service Status prüfen

```bash
# Server Status
sudo systemctl status nfc-server

# Client Status
sudo systemctl status nfc-client

# Logs anzeigen
sudo journalctl -u nfc-server -f
sudo journalctl -u nfc-client -f
```

## Verwendung

### 1. Neuen Benutzer registrieren

1. Browser öffnen: `http://<raspberry-pi-ip>:5000`
2. "Registrieren" klicken
3. NFC Tag scannen oder manuell eingeben
4. Name, Nachname, PIN eingeben
5. Registrierung abschließen

### 2. Arbeitszeit erfassen

1. NFC Tag am Reader scannen
2. PIN eingeben
3. System startet/stoppt automatisch die Arbeitszeit
4. Bestätigung wird angezeigt

### 3. Arbeitszeitdaten auslesen

```bash
# Datenbank abfragen
mysql -u root -p pro1

# Alle Sessions anzeigen
SELECT * FROM user_data;

# Heute's Sessions
SELECT u.name, u.surname, ud.checkin_time, ud.checkout_time, ud.session_duration 
FROM user_data ud 
JOIN users u ON ud.user_id = u.id 
WHERE DATE(ud.date) = CURDATE();
```

## Troubleshooting

### Arduino wird nicht erkannt

```bash
# Port Liste
ls -l /dev/tty*

# Dialout Gruppe prüfen
groups $USER

# Manuelle Port Angabe in .env
echo "ARDUINO_PORT=/dev/ttyACM0" >> client/.env
```

### Datenbank Verbindung fehlschlägt

```bash
# MariaDB Status
sudo systemctl status mariadb

# MariaDB starten
sudo systemctl start mariadb

# Verbindung testen
mysql -u root -p pro1 -e "SELECT 1"
```

### NFC Tags werden nicht gelesen

1. Verkabelung prüfen (3.3V nicht 5V!)
2. SPI Pins korrekt? (SS=10, RST=9 für Uno)
3. Tag am Reader halten (< 3cm Abstand)
4. Serial Monitor öffnen (9600 baud)
5. Debugging: `client/arduino_test.py` ausführen

### Port 5000/5001 bereits belegt

```bash
# Prozess finden
sudo lsof -i :5000
sudo lsof -i :5001

# Port in .env ändern
nano client/.env  # FLASK_PORT=8080
nano server/.env  # FLASK_PORT=8081
```

## Entwicklung

### Virtual Environment manuell aktivieren

```bash
# Client
cd client
source venv/bin/activate

# Server
cd server
source venv/bin/activate
```

### Dependencies aktualisieren

```bash
# In aktiviertem venv
pip install --upgrade -r requirements.txt
```

### Neue Dependencies hinzufügen

```bash
pip install <package>
pip freeze > requirements.txt
```

## Sicherheit

- **PIN Verschlüsselung**: Argon2 Hash
- **UID Verschlüsselung**: Fernet (AES)
- **HTTPS**: Für Produktion Reverse Proxy (nginx) verwenden
- **Firewall**: Nur benötigte Ports öffnen

```bash
# UFW Firewall (optional)
sudo ufw allow 5000/tcp  # Client
sudo ufw allow 5001/tcp  # Server (nur intern)
sudo ufw enable
```

## Lizenz

MIT License

## Support

Bei Problemen Issue auf GitHub erstellen oder Dokumentation prüfen.
