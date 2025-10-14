# NFC Worktime System - Raspberry Pi OS Installation

Ein NFC-basiertes Arbeitszeiterfassungssystem mit Arduino RC522 Reader, Flask Web Interface und MariaDB Backend.

## System Architektur

- **Client**: Flask Web Interface + Arduino NFC Scanner
- **Server**: Flask REST API + MariaDB Datenbank
- **Arduino**: RC522 NFC Reader über USB Serial

## Hardware Anforderungen

- Raspberry Pi (3B+, 4 oder Zero 2 W empfohlen)
- Arduino Uno / Nano / Mega
- RC522 NFC Reader Modul (13.56MHz)
- NFC Tags (MIFARE Classic, NTAG213, etc.)

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
