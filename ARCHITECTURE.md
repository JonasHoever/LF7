# System Architecture - I2C NFC Access Control

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RASPBERRY PI                                 │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Flask Web Server                          │  │
│  │                    (Port 5000)                               │  │
│  │                                                              │  │
│  │  Routes:                                                     │  │
│  │  - /           → Dashboard                                   │  │
│  │  - /login      → Login Page                                  │  │
│  │  - /register   → User Registration                           │  │
│  │  - /api/...    → REST API                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │                                           │
│                          │ HTTP Requests                             │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Backend Server (Port 5001)                      │  │
│  │                                                              │  │
│  │  - UserSystem: NFC + PIN Validation                         │  │
│  │  - WorkTimeSystem: Session Management                       │  │
│  │  - MariaDB Connection                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │                                           │
│                          │ SQL Queries                               │
│                          ↓                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    MariaDB Database                          │  │
│  │                                                              │  │
│  │  Tables:                                                     │  │
│  │  - users: id, name, surname, nfc_tag, pin                   │  │
│  │  - user_data: session_id, user_id, checkin_time, ...        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Serial Communication Thread                     │  │
│  │              (pyserial, 9600 baud)                           │  │
│  │                                                              │  │
│  │  Empfängt:  UID:12345678;PIN:1234                           │  │
│  │  Sendet:    ACCESS_GRANTED / ACCESS_DENIED                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────────┘
                            │
                            │ USB Serial (/dev/ttyACM0)
                            │ Baudrate: 9600
                            │
┌───────────────────────────┴──────────────────────────────────────────┐
│                      MASTER ARDUINO                                  │
│                      (I2C Master)                                    │
│                                                                      │
│  ┌────────────────────┐          ┌──────────────────────────────┐  │
│  │   LCD Display      │          │     4x4 Keypad               │  │
│  │   16x2 I2C         │          │                              │  │
│  │   Adresse: 0x27    │          │   1  2  3  A                 │  │
│  │                    │          │   4  5  6  B                 │  │
│  │  Anzeige:          │          │   7  8  9  C                 │  │
│  │  - Bereit          │          │   *  0  #  D                 │  │
│  │  - UID erkannt     │          │                              │  │
│  │  - PIN: ____       │          │  * = Backspace               │  │
│  │  - Willkommen!     │          │  # = Cancel                  │  │
│  └────────────────────┘          └──────────────────────────────┘  │
│           │                                    │                    │
│           │ I2C (SDA/SCL)                      │ Matrix Scan        │
│           │                                    │                    │
│  ┌────────┴────────────────────────────────────┴────────────────┐  │
│  │                 Microcontroller (Uno/Nano/Mega)              │  │
│  │                                                              │  │
│  │  State Machine:                                             │  │
│  │  1. IDLE             → Warte auf NFC von Slave              │  │
│  │  2. WAITING_FOR_PIN  → Lese Keypad                          │  │
│  │  3. VALIDATING       → Sende zu Pi, warte Antwort           │  │
│  │  4. ACCESS_GRANTED   → Sende OPEN an Slave                  │  │
│  │  5. ACCESS_DENIED    → Zeige Fehler                         │  │
│  │                                                              │  │
│  │  I2C Master:                                                │  │
│  │  - Fragt Slave alle 150ms nach UID                          │  │
│  │  - Sendet OPEN-Befehl bei Erfolg                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            │                                         │
│                            │ I2C Bus (SDA=A4, SCL=A5)                │
│                            │ Pull-Up: 4.7kΩ                          │
└────────────────────────────┴─────────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────────┐
│                      SLAVE ARDUINO                                   │
│                      (I2C Slave, Adresse 0x08)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              NFC Reader (MFRC522)                            │  │
│  │              SPI Interface (SS=10, RST=9)                    │  │
│  │              ⚠️  3.3V ONLY!                                   │  │
│  │                                                              │  │
│  │  Funktion:                                                   │  │
│  │  - Scannt 13.56MHz MIFARE Tags                              │  │
│  │  - Extrahiert UID (8-20 Hex-Zeichen)                        │  │
│  │  - Sendet "UID:xxxxx\n" via I2C                             │  │
│  │  - LED blinkt bei Scan                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            │                                         │
│                            │ SPI Bus                                 │
│                            │                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 Microcontroller (Uno/Nano/Mega)              │  │
│  │                                                              │  │
│  │  I2C Slave Callbacks:                                       │  │
│  │  - onRequest(): Sendet UID oder "NONE"                      │  │
│  │  - onReceive(): Empfängt "OPEN" Befehl                      │  │
│  │                                                              │  │
│  │  Status-LED (Pin 6):                                        │  │
│  │  - Blinkt 3x bei NFC-Scan                                   │  │
│  │  - Leuchtet während Motor läuft                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            │                                         │
│                            │ Digital Pins 2-5                        │
│                            │                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          28BYJ-48 Stepper Motor + ULN2003 Driver            │  │
│  │                                                              │  │
│  │  Spezifikationen:                                           │  │
│  │  - 2048 Schritte/Umdrehung                                  │  │
│  │  - 512 Schritte = 90° (Drehkreuz öffnen)                    │  │
│  │  - Speed: 10 RPM                                            │  │
│  │  - Externe 5V Versorgung empfohlen (min. 1A)                │  │
│  │                                                              │  │
│  │  Sequenz bei OPEN:                                          │  │
│  │  1. Drehe +512 Schritte (90° vor)                           │  │
│  │  2. Warte 1 Sekunde                                         │  │
│  │  3. Drehe -512 Schritte (90° zurück)                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘


KOMMUNIKATIONSABLAUF
══════════════════════════════════════════════════════════════════════

Schritt 1: NFC-Scan
─────────────────────
┌──────┐             ┌──────┐
│ User │──Tag──────→ │ Slave│
└──────┘             └──┬───┘
                        │ PICC_IsNewCardPresent()
                        │ PICC_ReadCardSerial()
                        │ UID = "4A3B2C1D"
                        │ newCardAvailable = true
                        └────────────────────────

Schritt 2: I2C UID-Transfer
────────────────────────────
┌────────┐  requestFrom(0x08)   ┌───────┐
│ Master │─────────────────────→│ Slave │
│        │←─────────────────────│       │
│        │   "UID:4A3B2C1D\n"   │       │
└────────┘                       └───────┘
   │
   │ LCD: "UID erkannt"
   │      "PIN: ____"
   └──────────────────────────

Schritt 3: PIN-Eingabe
──────────────────────
┌──────┐             ┌────────┐
│ User │──1─2─3─4──→ │ Master │
└──────┘             └───┬────┘
                         │ enteredPIN = "1234"
                         │ State = VALIDATING
                         └────────────────────

Schritt 4: Serial zu Raspberry Pi
──────────────────────────────────
┌────────┐  "UID:4A3B2C1D;PIN:1234\n"  ┌────────┐
│ Master │────────────────────────────→ │   Pi   │
│        │                              │        │
│        │                              │ Server │
│        │                              │ Query  │
│        │                              │ MariaDB│
│        │                              └───┬────┘
│        │                                  │
│        │  "ACCESS_GRANTED\n"              │
│        │←─────────────────────────────────┘
└────────┘

Schritt 5: I2C Motor-Befehl
────────────────────────────
┌────────┐  "OPEN"              ┌───────┐
│ Master │─────────────────────→│ Slave │
└────────┘                       └───┬───┘
                                     │ openDoorCommand = true
                                     │ LED ON
                                     │ step(+512)
                                     │ delay(1000)
                                     │ step(-512)
                                     │ LED OFF
                                     └────────────────────

Schritt 6: Fertig
─────────────────
┌────────┐              ┌──────┐
│ Master │──LCD─────────│ User │
│        │  "Willkommen!"│      │
└────────┘              └──────┘


FEHLERBEHANDLUNG
══════════════════════════════════════════════════════════════════════

Timeout Szenarien:
─────────────────

1. PIN-Timeout (30s)
   User gibt PIN nicht ein → Master: "Timeout!" → IDLE

2. Server-Timeout (10s)
   Pi antwortet nicht → Master: "Server Timeout!" → IDLE

3. I2C-Fehler
   Slave antwortet nicht → Master wartet, kein Crash

4. Serial-Fehler
   USB-Trennung → Pi reconnect-Logik aktiviert


Fehlerhafte PIN:
───────────────
┌────────┐                        ┌────────┐
│ Master │─UID:xxx;PIN:9999 ────→│   Pi   │
│        │                        │        │
│        │                        │ Server:│
│        │                        │ PIN != │
│        │                        │ DB     │
│        │                        └───┬────┘
│        │  "ACCESS_DENIED\n"         │
│        │←───────────────────────────┘
│        │
│  LCD:  │
│ "Zugang│
│ verweigert!"
│ "Falsche PIN"
└────────┘
