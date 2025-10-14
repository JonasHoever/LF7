/*
 * SLAVE ARDUINO - I2C Slave mit NFC Reader und Stepper Motor
 * 
 * Hardware:
 * - MFRC522 NFC Reader (SPI: SS=10, RST=9)
 * - 28BYJ-48 Stepper Motor mit ULN2003 Driver
 * - LED an Pin 6 (Status-Lampe)
 * 
 * I2C Slave-Adresse: 0x08
 * 
 * Ablauf:
 * 1. Wartet auf NFC-Tag
 * 2. Sendet UID an Master via I2C (bei Anfrage)
 * 3. Wartet auf "OPEN" Befehl vom Master
 * 4. Dreht Stepper Motor (Drehkreuz öffnen)
 */

#include <Wire.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Stepper.h>

#define SLAVE_ADDRESS 0x08
#define SS_PIN 10
#define RST_PIN 9
#define LAMP_PIN 6

// 28BYJ-48 Stepper Motor: 2048 Schritte = 360°
#define STEPS_PER_REV 2048
#define DOOR_OPEN_STEPS 512   // 90° Drehung
#define MOTOR_SPEED 10        // RPM

// Stepper: IN1=2, IN3=4, IN2=3, IN4=5
Stepper myStepper(STEPS_PER_REV, 2, 4, 3, 5);
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Status-Variablen
String currentUID = "";
volatile bool newCardAvailable = false;
volatile bool openDoorCommand = false;
unsigned long lastCardTime = 0;
unsigned long cardCooldown = 2000;  // 2 Sekunden zwischen Scans

void setup() {
  Serial.begin(9600);
  
  // SPI für NFC Reader
  SPI.begin();
  mfrc522.PCD_Init();
  
  // I2C Slave
  Wire.begin(SLAVE_ADDRESS);
  Wire.onRequest(handleI2CRequest);
  Wire.onReceive(handleI2CReceive);
  
  // Stepper Motor
  myStepper.setSpeed(MOTOR_SPEED);
  
  // Status LED
  pinMode(LAMP_PIN, OUTPUT);
  digitalWrite(LAMP_PIN, LOW);
  
  Serial.println("=================================");
  Serial.println("SLAVE ARDUINO - NFC & Motor");
  Serial.println("=================================");
  Serial.println("I2C Adresse: 0x08");
  Serial.println("NFC Reader: AKTIV");
  Serial.println("Motor: BEREIT");
  Serial.println("=================================");
  
  // Test-Blink
  for (int i = 0; i < 3; i++) {
    digitalWrite(LAMP_PIN, HIGH);
    delay(200);
    digitalWrite(LAMP_PIN, LOW);
    delay(200);
  }
}

void loop() {
  // 1. NFC-Karten-Scan
  scanForNFCCard();
  
  // 2. Motor-Steuerung bei Befehl
  if (openDoorCommand) {
    executeDoorOpen();
    openDoorCommand = false;
  }
  
  delay(50);
}

void scanForNFCCard() {
  // Cooldown prüfen (verhindert Mehrfach-Scans)
  if (millis() - lastCardTime < cardCooldown) {
    return;
  }
  
  // Prüfe ob neue Karte vorhanden
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }
  
  // Lese Karten-UID
  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }
  
  // Extrahiere UID als Hex-String
  currentUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    byte b = mfrc522.uid.uidByte[i];
    if (b < 0x10) currentUID += "0";
    currentUID += String(b, HEX);
  }
  currentUID.toUpperCase();
  
  // Validierung: Mindestens 8 Zeichen
  if (currentUID.length() >= 8) {
    newCardAvailable = true;
    lastCardTime = millis();
    
    Serial.print("NFC-Karte erkannt: ");
    Serial.println(currentUID);
    
    // Visuelles Feedback
    blinkLED(3, 100);
  }
  
  // Karte deaktivieren
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void handleI2CRequest() {
  // Master fragt nach NFC-UID
  if (newCardAvailable) {
    String payload = "UID:" + currentUID + "\n";
    Wire.write(payload.c_str());
    
    Serial.print("I2C -> Master: ");
    Serial.println(payload);
    
    newCardAvailable = false;  // Nur einmal senden
  } else {
    Wire.write("NONE\n");
  }
}

void handleI2CReceive(int numBytes) {
  // Master sendet Befehl
  String command = "";
  
  while (Wire.available()) {
    char c = Wire.read();
    if (c >= 0x20 && c <= 0x7E) {  // Nur druckbare Zeichen
      command += c;
    }
  }
  
  command.trim();
  
  Serial.print("I2C <- Master: ");
  Serial.println(command);
  
  if (command == "OPEN") {
    openDoorCommand = true;
    Serial.println("OPEN-Befehl empfangen -> Motor aktiviert");
  }
}

void executeDoorOpen() {
  Serial.println("=================================");
  Serial.println("MOTOR: Drehkreuz öffnen");
  Serial.println("=================================");
  
  // LED an während Motor läuft
  digitalWrite(LAMP_PIN, HIGH);
  
  // Vorwärts drehen (Tür öffnen)
  Serial.println("Schritt 1: Öffnen (90° vor)");
  myStepper.step(DOOR_OPEN_STEPS);
  delay(1000);  // 1 Sekunde offen halten
  
  // Rückwärts drehen (Tür schließen)
  Serial.println("Schritt 2: Schließen (90° zurück)");
  myStepper.step(-DOOR_OPEN_STEPS);
  
  // LED aus
  digitalWrite(LAMP_PIN, LOW);
  
  Serial.println("Motor: Fertig");
  Serial.println("=================================");
  
  // Erfolgs-Blink
  blinkLED(2, 200);
}

void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LAMP_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LAMP_PIN, LOW);
    delay(delayMs);
  }
}

/*
 * DEBUGGING FUNKTIONEN
 */

void printNFCReaderDetails() {
  Serial.println("=================================");
  Serial.println("NFC Reader Info:");
  Serial.print("Firmware Version: 0x");
  byte v = mfrc522.PCD_ReadRegister(mfrc522.VersionReg);
  Serial.println(v, HEX);
  Serial.println("=================================");
}

void testMotor() {
  Serial.println("Motor Test: 360° Drehung");
  myStepper.step(STEPS_PER_REV);
  delay(1000);
  Serial.println("Motor Test: Fertig");
}
