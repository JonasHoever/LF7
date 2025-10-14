# I2C NFC System - Verkabelungsanleitung

## System-Übersicht

```
[Raspberry Pi] <--USB-Serial--> [Master Arduino]
                                      |
                                    I2C Bus
                                      |
                                [Slave Arduino]
```

## Hardware-Komponenten

### Master Arduino (Uno/Nano/Mega)
- I2C LCD Display 16x2
- 4x4 Matrix Keypad
- USB zu Raspberry Pi
- Optional: Buzzer an Pin 11

### Slave Arduino (Uno/Nano/Mega)
- MFRC522 NFC Reader
- 28BYJ-48 Stepper Motor mit ULN2003 Driver
- LED an Pin 6
- I2C zu Master

---

## MASTER ARDUINO - Verkabelung

### I2C LCD Display (16x2)

| LCD Pin | Arduino Pin | Hinweis |
|---------|-------------|---------|
| VCC     | 5V          |         |
| GND     | GND         |         |
| SDA     | A4          | I2C Data (Uno/Nano) |
| SCL     | A5          | I2C Clock (Uno/Nano) |

**Mega 2560:**
- SDA → Pin 20
- SCL → Pin 21

**LCD I2C-Adresse:** 0x27 oder 0x3F (im Code anpassen falls nötig)

### 4x4 Matrix Keypad

| Keypad Pin | Arduino Pin | Bezeichnung |
|------------|-------------|-------------|
| Pin 1      | 9           | Row 0       |
| Pin 2      | 8           | Row 1       |
| Pin 3      | 7           | Row 2       |
| Pin 4      | 6           | Row 3       |
| Pin 5      | 5           | Col 0       |
| Pin 6      | 4           | Col 1       |
| Pin 7      | 3           | Col 2       |
| Pin 8      | 2           | Col 3       |

**Tastenlayout:**
```
1  2  3  A
4  5  6  B
7  8  9  C
*  0  #  D
```

- `*` = Backspace (letzte Ziffer löschen)
- `#` = Abbrechen
- `0-9` = PIN-Eingabe

### Optional: Buzzer

| Buzzer Pin | Arduino Pin |
|------------|-------------|
| +          | 11          |
| -          | GND         |

---

## SLAVE ARDUINO - Verkabelung

### MFRC522 NFC Reader (SPI)

| RC522 Pin | Arduino Pin | Hinweis |
|-----------|-------------|---------|
| SDA (SS)  | 10          | Slave Select |
| SCK       | 13          | SPI Clock |
| MOSI      | 11          | Master Out Slave In |
| MISO      | 12          | Master In Slave Out |
| IRQ       | -           | Nicht verbunden |
| GND       | GND         |         |
| RST       | 9           | Reset   |
| 3.3V      | 3.3V        | **WICHTIG: 3.3V NICHT 5V!** |

⚠️ **ACHTUNG:** RC522 ist **NUR 3.3V tolerant!** 5V zerstört das Modul!

**Mega 2560:**
- SS → 53
- SCK → 52
- MOSI → 51
- MISO → 50

### 28BYJ-48 Stepper Motor mit ULN2003

| ULN2003 Pin | Arduino Pin | Hinweis |
|-------------|-------------|---------|
| IN1         | 2           |         |
| IN2         | 3           |         |
| IN3         | 4           |         |
| IN4         | 5           |         |
| VCC         | 5V          | Externe Stromversorgung empfohlen! |
| GND         | GND         |         |

**Motor-Stecker:** Rot-Orange-Gelb-Rosa-Blau (Standard 28BYJ-48)

⚠️ **Stromversorgung:** Bei Verwendung des Motors über USB kann es zu Spannungseinbrüchen kommen. Verwende ein externes 5V-Netzteil (min. 1A) für den Arduino!

### Status-LED

| LED Pin | Arduino Pin | Hinweis |
|---------|-------------|---------|
| Anode (+) | 6         | via 220Ω Widerstand |
| Kathode (-) | GND     |         |

---

## I2C BUS - Verbindung zwischen Master und Slave

| Signal | Master Pin | Slave Pin | Hinweis |
|--------|------------|-----------|---------|
| SDA    | A4 (Uno/Nano) | A4 (Uno/Nano) | I2C Data |
| SCL    | A5 (Uno/Nano) | A5 (Uno/Nano) | I2C Clock |
| GND    | GND        | GND       | Gemeinsame Masse |

**Mega 2560:**
- SDA → Pin 20
- SCL → Pin 21

**Pull-Up Widerstände:** 
- 4.7kΩ zwischen SDA und 5V
- 4.7kΩ zwischen SCL und 5V
- (Oft bereits auf I2C-Modulen vorhanden!)

---

## Raspberry Pi - Verbindung zu Master

| Raspberry Pi | Master Arduino | Hinweis |
|--------------|----------------|---------|
| USB Port     | USB Port       | Standard USB-A zu USB-B Kabel |

**Serial Settings:**
- Baudrate: 9600
- Port: `/dev/ttyACM0` oder `/dev/ttyUSB0`

---

## Stromversorgung

### Option 1: Nur USB (Entwicklung)
- Raspberry Pi → Master Arduino via USB
- Slave Arduino über eigenes USB-Netzteil

### Option 2: Externe Versorgung (Produktion)
- Master Arduino: 7-12V DC Barrel Jack
- Slave Arduino: 7-12V DC Barrel Jack (min. 1A wegen Motor!)
- Raspberry Pi: 5V 3A USB-C

⚠️ **Wichtig:** Alle GND-Pins müssen gemeinsam verbunden sein!

---

## I2C Adressen

| Gerät | Adresse |
|-------|---------|
| Master Arduino | Keine (ist Master) |
| Slave Arduino | 0x08 |
| LCD Display | 0x27 oder 0x3F |

**Adresskonflikt vermeiden:** LCD und Slave müssen unterschiedliche Adressen haben!

### LCD-Adresse testen:
```bash
# Auf Raspberry Pi
sudo i2cdetect -y 1
```

Falls LCD nicht 0x27 ist, im Code ändern:
```cpp
LiquidCrystal_I2C lcd(0x3F, 16, 2);  // Adresse anpassen
```

---

## Verkabelungs-Checkliste

### Master Arduino
- [ ] I2C LCD (SDA=A4, SCL=A5)
- [ ] Keypad (Pins 2-9)
- [ ] I2C zu Slave (SDA, SCL, GND)
- [ ] USB zu Raspberry Pi
- [ ] Optional: Buzzer (Pin 11)

### Slave Arduino
- [ ] MFRC522 (SPI: SS=10, RST=9, 3.3V!)
- [ ] Stepper Motor (IN1-4 = Pins 2-5)
- [ ] LED (Pin 6)
- [ ] I2C zu Master (SDA, SCL, GND)
- [ ] Externe Stromversorgung (5V 1A+)

### Allgemein
- [ ] Alle GND verbunden
- [ ] I2C Pull-Up Widerstände (4.7kΩ)
- [ ] 3.3V für RC522 (NICHT 5V!)
- [ ] Externe 5V für Slave bei Motor-Betrieb

---

## Troubleshooting

### I2C funktioniert nicht
- Prüfe SDA/SCL Verbindungen
- Prüfe Pull-Up Widerstände (4.7kΩ)
- Prüfe Adresskonflikte (LCD != Slave)
- Kurze Kabel verwenden (< 30cm)

### NFC Reader erkennt keine Tags
- 3.3V Versorgung prüfen (NICHT 5V!)
- SPI-Pins korrekt?
- Tag-Abstand < 3cm
- RC522 Firmware: `mfrc522.PCD_DumpVersionToSerial()`

### Motor dreht nicht
- Externe Stromversorgung (min. 1A)
- Kabelreihenfolge prüfen
- `testMotor()` Funktion aufrufen

### Serial-Kommunikation Fehler
- Baudrate 9600 auf allen Geräten
- User in `dialout` Gruppe: `sudo usermod -a -G dialout $USER`
- Nur ein Programm darf Serial-Port öffnen

---

## Pinout-Übersicht

### Master Arduino UNO
```
Digital Pins:
2-5:   Keypad Spalten
6-9:   Keypad Zeilen
11:    Buzzer (optional)

Analog Pins:
A4:    I2C SDA
A5:    I2C SCL
```

### Slave Arduino UNO
```
Digital Pins:
2-5:   Stepper Motor (IN1-IN4)
6:     Status LED
9:     RC522 RST
10:    RC522 SS
11:    RC522 MOSI (SPI)
12:    RC522 MISO (SPI)
13:    RC522 SCK (SPI)

Analog Pins:
A4:    I2C SDA
A5:    I2C SCL
```

---

## Fertig!

Nach Verkabelung:
1. Master-Sketch auf Master-Arduino hochladen
2. Slave-Sketch auf Slave-Arduino hochladen
3. Serial Monitor öffnen (beide Arduinos, 9600 baud)
4. NFC-Tag scannen → UID wird an Master gesendet
5. PIN eingeben am Keypad
6. Raspberry Pi validiert
7. Motor dreht bei Erfolg

Viel Erfolg! 🚀
