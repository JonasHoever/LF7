# Arduino Pinout Diagrams

## MASTER ARDUINO UNO - Pinout

```
                    ┌─────────────────────────┐
                    │                         │
                    │   ARDUINO UNO (Master)  │
                    │                         │
     ┌──────────────┤ USB ◄── Raspberry Pi   │
     │              │                         │
     │              └─────────────────────────┘
     │
     │              ┌──────────────┬──────────────┐
     │              │ Digital Pins │  Analog Pins │
     │              ├──────────────┼──────────────┤
     │              │              │              │
     │              │   D0  (RX)   │   A0         │
     │              │   D1  (TX)   │   A1         │
Keypad Col 3 ───────┤   D2         │   A2         │
Keypad Col 2 ───────┤   D3         │   A3         │
Keypad Col 1 ───────┤   D4         │   A4  ◄────────── I2C SDA
Keypad Col 0 ───────┤   D5         │   A5  ◄────────── I2C SCL
Keypad Row 3 ───────┤   D6         │              │
Keypad Row 2 ───────┤   D7         │              │
Keypad Row 1 ───────┤   D8         │              │
Keypad Row 0 ───────┤   D9         │              │
     │              │   D10        │              │
Buzzer ─────────────┤   D11        │              │
     │              │   D12        │              │
     │              │   D13 (LED)  │              │
     │              │              │              │
     │              │   GND  ◄──────────── Common Ground
     │              │   5V         │              │
     │              │   3.3V       │              │
     │              └──────────────┴──────────────┘
     │                     │
     │                     │ I2C Bus
     │                     ↓
     │              I2C LCD 16x2
     │              ┌──────────────┐
     │              │ VCC ← 5V     │
     └──────────────│ GND ← GND    │
                    │ SDA ← A4     │
                    │ SCL ← A5     │
                    └──────────────┘
                    
                    
4x4 Matrix Keypad
┌─────────────────────────────┐
│                             │
│    1    2    3    A         │  Row 0 → D9
│    4    5    6    B         │  Row 1 → D8
│    7    8    9    C         │  Row 2 → D7
│    *    0    #    D         │  Row 3 → D6
│                             │
│    ↓    ↓    ↓    ↓         │
│   D5   D4   D3   D2         │
│  Col0 Col1 Col2 Col3        │
└─────────────────────────────┘
```

---

## SLAVE ARDUINO UNO - Pinout

```
                    ┌─────────────────────────┐
                    │                         │
                    │   ARDUINO UNO (Slave)   │
                    │   I2C Address: 0x08     │
                    │                         │
                    │                         │
                    └─────────────────────────┘
                    
              ┌──────────────┬──────────────┐
              │ Digital Pins │  Analog Pins │
              ├──────────────┼──────────────┤
              │              │              │
              │   D0  (RX)   │   A0         │
              │   D1  (TX)   │   A1         │
Stepper IN1 ──┤   D2         │   A2         │
Stepper IN2 ──┤   D3         │   A3         │
Stepper IN3 ──┤   D4         │   A4  ◄────────── I2C SDA
Stepper IN4 ──┤   D5         │   A5  ◄────────── I2C SCL
Status LED ───┤   D6         │              │
              │   D7         │              │
              │   D8         │              │
RC522 RST ────┤   D9         │              │
RC522 SS ─────┤   D10        │              │
RC522 MOSI ───┤   D11 (MOSI) │              │
RC522 MISO ───┤   D12 (MISO) │              │
RC522 SCK ────┤   D13 (SCK)  │              │
              │              │              │
              │   GND  ◄──────────── Common Ground
              │   5V   ───────────── Stepper Motor
              │   3.3V ───────────── RC522 VCC
              └──────────────┴──────────────┘
                    │
                    │ SPI Bus
                    ↓
            MFRC522 NFC Reader
            ┌──────────────────┐
            │ SDA (SS) ← D10   │
            │ SCK      ← D13   │
            │ MOSI     ← D11   │
            │ MISO     ← D12   │
            │ IRQ      (NC)    │
            │ GND      ← GND   │
            │ RST      ← D9    │
            │ 3.3V     ← 3.3V  │  ⚠️ WICHTIG: 3.3V!
            └──────────────────┘
            
            
28BYJ-48 Stepper Motor + ULN2003 Driver
┌────────────────────────────────────┐
│         ULN2003 Driver Board       │
│                                    │
│  IN1 ← D2                          │
│  IN2 ← D3                          │
│  IN3 ← D4                          │
│  IN4 ← D5                          │
│  VCC ← 5V (Extern!)                │
│  GND ← GND                         │
│                                    │
│  [5-Pin Connector to Motor]        │
└────────────────────────────────────┘
         │
         │ 5-Wire Cable
         ↓
┌────────────────────┐
│  28BYJ-48 Motor    │
│  (Rot-Orange-Gelb- │
│   Rosa-Blau)       │
└────────────────────┘


Status LED
┌─────────────┐
│   LED       │
│    │        │
│   (+) ← D6 (via 220Ω Resistor)
│   (-) ← GND │
└─────────────┘
```

---

## I2C BUS CONNECTION

```
┌─────────────────────┐           ┌─────────────────────┐
│   MASTER ARDUINO    │           │   SLAVE ARDUINO     │
│                     │           │                     │
│  A4 (SDA) ◄─────────┼───────────┼────────► A4 (SDA)  │
│                     │           │                     │
│  A5 (SCL) ◄─────────┼───────────┼────────► A5 (SCL)  │
│                     │           │                     │
│  GND      ◄─────────┼───────────┼────────► GND       │
│                     │           │                     │
│  5V       ─────┬────┘           └────┬──── 5V        │
└────────────────┼────────────────────┼────────────────┘
                 │                     │
                 │    Pull-Up          │
                 │    Resistors        │
                 ├─── 4.7kΩ ──────────┤ (to SDA)
                 └─── 4.7kΩ ──────────┘ (to SCL)


⚠️ Pull-Up Widerstände sind oft bereits auf I2C-Modulen vorhanden!
⚠️ Kurze Kabel verwenden (< 30cm für stabile Kommunikation)
```

---

## POWER SUPPLY DIAGRAM

### Development Setup (USB Power)
```
┌────────────┐
│ Raspberry  │
│    Pi      │
└──────┬─────┘
       │ USB Cable
       ↓
┌─────────────────┐
│ MASTER Arduino  │
│                 │
│ I2C ─────────┐  │
└──────────────┼──┘
               │
               │ I2C Bus (SDA, SCL, GND)
               │
┌──────────────┼──┐         ┌──────────────┐
│              │  │ USB     │  USB Power   │
│ SLAVE Arduino◄──┼─────────│  Adapter     │
│              │  │         │  (5V 1A+)    │
└──────────────┼──┘         └──────────────┘
               │
               └─── External Power für Stepper Motor
```

### Production Setup (External Power)
```
┌────────────┐
│ Raspberry  │  ← 5V 3A USB-C
│    Pi      │
└──────┬─────┘
       │ USB Cable
       ↓
┌─────────────────┐
│ MASTER Arduino  │  ← 7-12V DC Barrel Jack
│                 │
│ I2C ─────────┐  │
└──────────────┼──┘
               │
               │ I2C Bus (SDA, SCL, GND)
               │
┌──────────────┼──┐
│              │  │  ← 7-12V DC Barrel Jack (min. 1A)
│ SLAVE Arduino│  │
│              │  │
└──────────────┼──┘
               │
               └─── GND gemeinsam verbinden!
```

---

## SERIAL COMMUNICATION

```
┌─────────────────────────────────────────────────────┐
│              Raspberry Pi                           │
│                                                     │
│  Python Serial (pyserial)                           │
│  Port: /dev/ttyACM0                                 │
│  Baudrate: 9600                                     │
│                                                     │
│  Empfängt:                                          │
│    MASTER_READY                                     │
│    NFC_DETECTED:4A3B2C1D                           │
│    UID:4A3B2C1D;PIN:1234                           │
│    SENDING_OPEN_TO_SLAVE                            │
│    SERVER_TIMEOUT                                   │
│                                                     │
│  Sendet:                                            │
│    ACCESS_GRANTED                                   │
│    ACCESS_DENIED                                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ USB Serial
                   │ 9600 baud
                   │
┌──────────────────┴──────────────────────────────────┐
│              MASTER Arduino                         │
│                                                     │
│  Serial.begin(9600)                                 │
│  Serial.println("UID:xxx;PIN:yyy")                  │
│  response = Serial.readStringUntil('\n')            │
└─────────────────────────────────────────────────────┘
```

---

## COMPLETE SYSTEM WIRING

```
                    ┌──────────────────┐
                    │  Raspberry Pi    │
                    │                  │
                    │  - Flask Server  │
                    │  - MariaDB       │
                    │  - Serial Thread │
                    └────────┬─────────┘
                             │
                             │ USB Serial
                             │ 9600 baud
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            │      MASTER ARDUINO             │
            │      (I2C Master)               │
            │                                 │
            │  ┌──────────┐   ┌──────────┐   │
            │  │   LCD    │   │  Keypad  │   │
            │  │   I2C    │   │  Matrix  │   │
            │  │  0x27    │   │   4x4    │   │
            │  └──────────┘   └──────────┘   │
            │                                 │
            │  A4 (SDA) ──┐                   │
            │  A5 (SCL) ──┼───────┐           │
            │  GND ────────┼───────┼───────┐  │
            └─────────────┼───────┼───────┼──┘
                          │       │       │
                  ┌───────┼───────┼───────┼──────┐
                  │       │       │       │      │
                  │  Pull-Up      │       │      │
                  │  4.7kΩ        │       │      │
                  │       ↓       ↓       ↓      │
            ┌─────┴───────┴───────┴───────┴──────┴─┐
            │                                       │
            │      SLAVE ARDUINO                    │
            │      (I2C Slave 0x08)                 │
            │                                       │
            │  ┌──────────┐        ┌──────────┐    │
            │  │  RC522   │        │ Stepper  │    │
            │  │  NFC     │        │  Motor   │    │
            │  │  Reader  │        │ 28BYJ-48 │    │
            │  │ (3.3V!)  │        │  + LED   │    │
            │  └──────────┘        └──────────┘    │
            │                                       │
            └───────────────────────────────────────┘
```

---

## PIN SUMMARY TABLE

| Function         | Master Pin | Slave Pin | Notes                    |
|------------------|------------|-----------|--------------------------|
| I2C SDA          | A4         | A4        | + 4.7kΩ Pull-Up          |
| I2C SCL          | A5         | A5        | + 4.7kΩ Pull-Up          |
| Keypad Row 0     | 9          | -         |                          |
| Keypad Row 1     | 8          | -         |                          |
| Keypad Row 2     | 7          | -         |                          |
| Keypad Row 3     | 6          | -         |                          |
| Keypad Col 0     | 5          | -         |                          |
| Keypad Col 1     | 4          | -         |                          |
| Keypad Col 2     | 3          | -         |                          |
| Keypad Col 3     | 2          | -         |                          |
| Buzzer           | 11         | -         | Optional                 |
| RC522 SS         | -          | 10        |                          |
| RC522 RST        | -          | 9         |                          |
| RC522 MOSI       | -          | 11        | Hardware SPI             |
| RC522 MISO       | -          | 12        | Hardware SPI             |
| RC522 SCK        | -          | 13        | Hardware SPI             |
| RC522 VCC        | -          | 3.3V      | ⚠️ NOT 5V!               |
| Stepper IN1      | -          | 2         |                          |
| Stepper IN2      | -          | 3         |                          |
| Stepper IN3      | -          | 4         |                          |
| Stepper IN4      | -          | 5         |                          |
| Status LED       | -          | 6         | + 220Ω Resistor          |
| USB Serial       | Yes        | No        | To Raspberry Pi          |
| GND              | Common     | Common    | All GND connected        |

---

## TESTING CHECKLIST

### ✅ Before Power-On
- [ ] RC522 connected to 3.3V (NOT 5V!)
- [ ] All GND pins connected
- [ ] I2C Pull-Up resistors present (4.7kΩ)
- [ ] No short circuits (check with multimeter)
- [ ] Correct pin assignments

### ✅ Master Arduino Test
- [ ] LCD lights up and shows text
- [ ] Keypad responds (Serial Monitor shows key presses)
- [ ] I2C scan shows LCD address (0x27 or 0x3F)
- [ ] Serial communication at 9600 baud works

### ✅ Slave Arduino Test
- [ ] NFC reader detected (check Firmware version)
- [ ] LED blinks on startup
- [ ] Motor can be manually triggered
- [ ] I2C scan shows slave address (0x08)

### ✅ System Integration Test
- [ ] Scan NFC tag → Master shows UID
- [ ] Enter PIN → Master sends to Pi
- [ ] Pi responds → Master displays result
- [ ] OPEN command → Slave motor turns

---

## 🎉 READY TO GO!

Wenn alle Pins korrekt verbunden sind:
1. Upload Master-Sketch auf Master-Arduino
2. Upload Slave-Sketch auf Slave-Arduino
3. Starte Raspberry Pi Client
4. Scanne NFC-Tag
5. Gib PIN ein
6. Motor dreht! 🎊
