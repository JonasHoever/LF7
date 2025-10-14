# ✅ PROJEKT CHECKLISTE - I2C NFC System

## 📋 Hardware-Beschaffung

### Master Arduino
- [ ] Arduino Uno / Nano / Mega (1x)
- [ ] I2C LCD Display 16x2 (1x, Adresse 0x27 oder 0x3F)
- [ ] 4x4 Matrix Keypad (1x)
- [ ] Buzzer 5V (1x, optional)
- [ ] USB-Kabel Typ A zu B (1x)
- [ ] Breadboard + Jumper Wires

### Slave Arduino
- [ ] Arduino Uno / Nano / Mega (1x)
- [ ] MFRC522 NFC Reader Modul (1x, 13.56MHz)
- [ ] 28BYJ-48 Stepper Motor (1x)
- [ ] ULN2003 Motor Driver Board (1x)
- [ ] LED 5mm (1x, beliebige Farbe)
- [ ] 220Ω Widerstand (1x)
- [ ] Breadboard + Jumper Wires

### I2C Bus
- [ ] 4.7kΩ Widerstand (2x, Pull-Up)
- [ ] Jumper Wires

### Stromversorgung
- [ ] Raspberry Pi 3B+/4 (1x)
- [ ] USB-C Netzteil 5V 3A (1x, für Pi)
- [ ] DC Barrel Jack Netzteil 7-12V 1A+ (2x, für Arduinos)
- [ ] Oder: USB-Netzteile 5V 1A+ (für Entwicklung)

### Sonstiges
- [ ] NFC Tags MIFARE Classic / NTAG213 (min. 5x)
- [ ] microSD-Karte min. 8GB (1x, für Pi)
- [ ] Gehäuse (optional)
- [ ] Schrauben + Abstandshalter

---

## 🔧 Software-Setup

### Arduino IDE
- [ ] Arduino IDE 2.x installiert
- [ ] CH340/CP2102 USB-Treiber (falls Clone-Arduino)
- [ ] Libraries installiert:
  - [ ] MFRC522 (miguelbalboa/rfid)
  - [ ] LiquidCrystal_I2C
  - [ ] Keypad
  - [ ] Stepper (built-in)
  - [ ] Wire (built-in)
  - [ ] SPI (built-in)

### Raspberry Pi
- [ ] Raspberry Pi OS installiert
- [ ] SSH aktiviert (optional)
- [ ] Python 3.7+ vorhanden
- [ ] git installiert
- [ ] MariaDB Server installiert

---

## 🔌 Verkabelung

### Master Arduino
- [ ] LCD SDA → A4
- [ ] LCD SCL → A5
- [ ] LCD VCC → 5V
- [ ] LCD GND → GND
- [ ] Keypad Row 0 → D9
- [ ] Keypad Row 1 → D8
- [ ] Keypad Row 2 → D7
- [ ] Keypad Row 3 → D6
- [ ] Keypad Col 0 → D5
- [ ] Keypad Col 1 → D4
- [ ] Keypad Col 2 → D3
- [ ] Keypad Col 3 → D2
- [ ] Buzzer + → D11 (optional)
- [ ] Buzzer - → GND
- [ ] USB → Raspberry Pi

### Slave Arduino
- [ ] RC522 VCC → 3.3V ⚠️ WICHTIG!
- [ ] RC522 GND → GND
- [ ] RC522 RST → D9
- [ ] RC522 SS → D10
- [ ] RC522 MOSI → D11
- [ ] RC522 MISO → D12
- [ ] RC522 SCK → D13
- [ ] Stepper IN1 → D2
- [ ] Stepper IN2 → D3
- [ ] Stepper IN3 → D4
- [ ] Stepper IN4 → D5
- [ ] Stepper VCC → Externe 5V (min. 1A)
- [ ] Stepper GND → GND
- [ ] LED Anode → D6 (via 220Ω)
- [ ] LED Kathode → GND

### I2C Bus
- [ ] Master A4 (SDA) → Slave A4 (SDA)
- [ ] Master A5 (SCL) → Slave A5 (SCL)
- [ ] Master GND → Slave GND
- [ ] 4.7kΩ zwischen SDA und 5V
- [ ] 4.7kΩ zwischen SCL und 5V

### Stromversorgung
- [ ] Master: USB zu Pi oder 7-12V DC
- [ ] Slave: 7-12V DC (min. 1A wegen Motor)
- [ ] Raspberry Pi: 5V 3A USB-C
- [ ] Alle GND gemeinsam verbunden

---

## 💾 Software-Installation

### Arduino Sketches
- [ ] Master-Sketch kompiliert ohne Fehler
- [ ] Master-Sketch hochgeladen
- [ ] Serial Monitor Master zeigt "MASTER_READY"
- [ ] LCD zeigt "Bereit - Karte auflegen..."
- [ ] Keypad reagiert (Serial Monitor Test)
- [ ] Slave-Sketch kompiliert ohne Fehler
- [ ] Slave-Sketch hochgeladen
- [ ] Serial Monitor Slave zeigt Startup-Meldung
- [ ] LED blinkt 3x beim Slave-Start

### Raspberry Pi Server
- [ ] Repository geklont
- [ ] `server/install_server.sh` ausgeführt
- [ ] MariaDB läuft (`sudo systemctl status mariadb`)
- [ ] Datenbank erstellt (`src/db_setup.sql`)
- [ ] `server/.env` konfiguriert (DB_PASS)
- [ ] Server startet ohne Fehler
- [ ] Server erreichbar: `http://localhost:5001`

### Raspberry Pi Client
- [ ] `client/install.sh` ausgeführt
- [ ] User in dialout Gruppe (`groups $USER`)
- [ ] `client/.env` konfiguriert (SERVER_URL)
- [ ] Client startet ohne Fehler
- [ ] Client erreichbar: `http://localhost:5000`
- [ ] Arduino Port erkannt (`✅ Arduino gefunden`)

---

## 🧪 Funktions-Tests

### Einzelkomponenten-Tests

#### LCD Test
- [ ] LCD leuchtet auf
- [ ] Text lesbar
- [ ] Kontrast korrekt eingestellt
- [ ] I2C-Adresse korrekt (0x27 oder 0x3F)

#### Keypad Test
```bash
# Serial Monitor Master öffnen (9600 baud)
# Taste drücken → Zeichen erscheint im Monitor
```
- [ ] Alle Ziffern (0-9) funktionieren
- [ ] Stern (*) = Backspace funktioniert
- [ ] Raute (#) = Cancel funktioniert
- [ ] A, B, C, D werden erkannt

#### NFC Reader Test
```bash
# Serial Monitor Slave öffnen (9600 baud)
# NFC-Tag auflegen
```
- [ ] "Karte erkannt: ..." erscheint
- [ ] UID ist 8-20 Hex-Zeichen
- [ ] LED blinkt 3x bei Scan
- [ ] Mehrfach-Scans funktionieren

#### Stepper Motor Test
```cpp
// In Slave setup() hinzufügen:
testMotor();  // Testfunktion aufrufen
```
- [ ] Motor dreht sich 360°
- [ ] Drehrichtung korrekt
- [ ] Keine Schritte übersprungen
- [ ] Kein lautes Brummen

#### Buzzer Test
```cpp
// In Master setup() hinzufügen:
tone(11, 1000, 500);  // Testton
```
- [ ] Buzzer piept
- [ ] Ton hörbar
- [ ] Keine Störgeräusche

### Subsystem-Tests

#### I2C Kommunikation Test
```bash
# Raspberry Pi Terminal:
sudo i2cdetect -y 1
```
- [ ] LCD-Adresse sichtbar (27 oder 3F)
- [ ] Slave-Adresse sichtbar (08)
- [ ] Keine anderen Geräte (Konflikt!)

```bash
# Serial Monitor Master & Slave öffnen
# NFC-Tag scannen
```
- [ ] Slave: "Karte erkannt: ..."
- [ ] Slave: "I2C -> Master: UID:..."
- [ ] Master: "NFC erkannt: ..."
- [ ] Master LCD zeigt UID

#### Serial Kommunikation Test
```bash
cd client
python3 test_i2c_system.py
```
- [ ] Script findet Arduino automatisch
- [ ] NFC scannen → "NFC_DETECTED" erscheint
- [ ] PIN eingeben → "UID:xxx;PIN:yyy" empfangen
- [ ] 'ok' tippen → Master zeigt "Willkommen!"
- [ ] Motor dreht sich

### Vollsystem-Tests

#### End-to-End Test (ohne Server)
```bash
python3 test_i2c_system.py
```
1. [ ] NFC-Tag scannen
2. [ ] Master LCD zeigt UID
3. [ ] PIN eingeben (4 Ziffern)
4. [ ] Python empfängt UID+PIN
5. [ ] 'ok' tippen
6. [ ] Master LCD zeigt "Willkommen!"
7. [ ] Slave Motor dreht 90° vor/zurück

#### End-to-End Test (mit Server)
```bash
# Server starten (Terminal 1)
cd server && ./start_server.sh

# Client starten (Terminal 2)
cd client && ./start.sh
```
1. [ ] Neuen User registrieren (Browser)
2. [ ] NFC-Tag mit User verknüpfen
3. [ ] PIN setzen (4 Ziffern)
4. [ ] NFC-Tag am Slave scannen
5. [ ] Master fordert PIN an
6. [ ] Richtige PIN eingeben
7. [ ] Server validiert
8. [ ] Master zeigt "Willkommen!"
9. [ ] Motor öffnet Drehkreuz
10. [ ] Arbeitszeit-Session startet

#### Fehlerfall-Tests
- [ ] Falsche PIN → "Zugang verweigert"
- [ ] Unbekannte UID → "Zugang verweigert"
- [ ] PIN-Timeout → "Timeout!" nach 30s
- [ ] Server offline → "Server Timeout" nach 10s
- [ ] Cancel (#) → Zurück zu "Bereit"

---

## 📊 Performance-Tests

### Latenz-Messung
- [ ] NFC-Scan bis LCD-Anzeige: < 500ms
- [ ] PIN-Eingabe bis Server-Antwort: < 2s
- [ ] Motor-Aktivierung: < 1s
- [ ] Gesamt-Durchlaufzeit: < 5s

### Stabilität
- [ ] 10x hintereinander scannen → keine Fehler
- [ ] System 1h laufen lassen → keine Abstürze
- [ ] I2C-Bus stabil (keine Timeouts)
- [ ] Serial-Verbindung stabil (keine Disconnects)

---

## 🎨 Produktions-Vorbereitung

### Mechanischer Aufbau
- [ ] Arduinos in Gehäuse montiert
- [ ] LCD von außen sichtbar
- [ ] Keypad gut erreichbar
- [ ] NFC-Reader optimal positioniert
- [ ] Motor mechanisch befestigt
- [ ] Kabel ordentlich verlegt

### Elektrische Sicherheit
- [ ] Keine blanken Lötpunkte
- [ ] Kurzschlüsse ausgeschlossen
- [ ] Stromversorgung dimensioniert (min. 1A für Motor)
- [ ] Sicherungen vorhanden (optional)

### Software-Deployment
- [ ] Systemd Services erstellt
- [ ] Autostart aktiviert
- [ ] Logs konfiguriert
- [ ] Backup-Strategie definiert
- [ ] Update-Prozess dokumentiert

### Dokumentation
- [ ] Benutzerhandbuch erstellt
- [ ] Admin-Guide geschrieben
- [ ] Notfall-Kontakte hinterlegt
- [ ] Wartungsplan erstellt

---

## 🔐 Sicherheits-Checks

### Physische Sicherheit
- [ ] NFC-Reader manipulationssicher montiert
- [ ] Keypad gegen Vandalismus geschützt
- [ ] Arduinos in verschlossenem Gehäuse
- [ ] Kabel nicht zugänglich

### Netzwerk-Sicherheit
- [ ] Firewall konfiguriert
- [ ] Nur benötigte Ports offen
- [ ] HTTPS für Web-Interface (Production)
- [ ] SSH mit Key-Auth (Pi)

### Daten-Sicherheit
- [ ] Datenbank-Passwörter stark
- [ ] PINs als Hash gespeichert (Argon2)
- [ ] Regelmäßige Backups
- [ ] Log-Rotation aktiv

---

## 📝 Abnahme-Kriterien

### Funktionale Anforderungen
- [x] NFC-Tag wird erkannt
- [x] PIN kann eingegeben werden
- [x] Server validiert korrekt
- [x] Motor öffnet Drehkreuz
- [x] Arbeitszeit wird erfasst
- [x] Web-Interface funktioniert

### Non-Funktionale Anforderungen
- [ ] Antwortzeit < 5s
- [ ] Verfügbarkeit > 99%
- [ ] Keine Datenverluste
- [ ] Wartbar (Dokumentation vorhanden)

### Benutzer-Akzeptanz
- [ ] Bedienung intuitiv
- [ ] Fehler-Feedback klar
- [ ] Geschwindigkeit akzeptabel
- [ ] Design ansprechend

---

## 🎉 FERTIG!

Wenn alle Punkte abgehakt sind:
✅ **SYSTEM IST PRODUKTIONSBEREIT!**

Letzte Schritte:
1. [ ] Finale Tests durchführen
2. [ ] Schulung Benutzer
3. [ ] Übergabe Admin
4. [ ] Go-Live! 🚀

---

## 📞 Support-Kontakte

| Bereich | Kontakt | Verfügbarkeit |
|---------|---------|---------------|
| Hardware | ... | ... |
| Software | ... | ... |
| Notfall | ... | 24/7 |

---

**Erstellt:** [Datum]  
**Version:** 1.0  
**Status:** ✅ Vollständig
