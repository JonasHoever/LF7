/*
 * MASTER ARDUINO - I2C Master mit LCD, Keypad und Serial zu Raspberry Pi
 * 
 * Hardware:
 * - I2C LCD 16x2 (0x27 oder 0x3F)
 * - 4x4 Keypad (Matrix)
 * - Serial USB zu Raspberry Pi
 * 
 * Ablauf:
 * 1. Wartet auf NFC-UID vom Slave via I2C
 * 2. Zeigt UID auf LCD an
 * 3. Fordert PIN-Eingabe via Keypad
 * 4. Sendet "UID:xxxxx;PIN:yyyy" an Raspberry Pi via Serial
 * 5. Wartet auf Antwort "OK" oder "DENIED" vom Pi
 * 6. Sendet "OPEN" an Slave bei OK
 * 7. Dreht Motor beim Slave
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

#define SLAVE_ADDRESS 0x08
#define SERIAL_BAUD 9600
#define PIN_LENGTH 4
#define PIN_TIMEOUT 30000  // 30 Sekunden für PIN-Eingabe

LiquidCrystal_I2C lcd(0x27, 16, 2); // Falls nicht funktioniert: 0x3F versuchen

// Keypad-Konfiguration
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6};
byte colPins[COLS] = {5, 4, 3, 2};
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Status-Variablen
String currentUID = "";
String enteredPIN = "";
bool waitingForPIN = false;
bool waitingForServerResponse = false;
unsigned long pinStartTime = 0;
unsigned long serverRequestTime = 0;

enum State {
  IDLE,
  WAITING_FOR_PIN,
  VALIDATING_SERVER,
  ACCESS_GRANTED,
  ACCESS_DENIED
};

State currentState = IDLE;

void setup() {
  Serial.begin(SERIAL_BAUD);
  Wire.begin();  // Master-Modus
  
  // LCD initialisieren
  lcd.init();
  lcd.backlight();
  
  // Startup-Meldung
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System bereit");
  lcd.setCursor(0, 1);
  lcd.print("Bitte Karte...");
  
  Serial.println("MASTER_READY");
  delay(2000);
  showIdleScreen();
}

void loop() {
  switch (currentState) {
    case IDLE:
      handleIdleState();
      break;
      
    case WAITING_FOR_PIN:
      handlePinEntry();
      checkPinTimeout();
      break;
      
    case VALIDATING_SERVER:
      handleServerResponse();
      checkServerTimeout();
      break;
      
    case ACCESS_GRANTED:
      handleAccessGranted();
      break;
      
    case ACCESS_DENIED:
      handleAccessDenied();
      break;
  }
  
  delay(50);  // Reduziert CPU-Last
}

void handleIdleState() {
  // Frage Slave nach neuer NFC-Karte
  String slaveResponse = requestFromSlave();
  
  if (slaveResponse.startsWith("UID:")) {
    // Extrahiere UID (nur Hex-Zeichen)
    currentUID = extractUID(slaveResponse);
    
    if (currentUID.length() >= 8) {
      Serial.print("NFC_DETECTED:");
      Serial.println(currentUID);
      
      // Wechsle zu PIN-Eingabe
      currentState = WAITING_FOR_PIN;
      enteredPIN = "";
      pinStartTime = millis();
      showPinScreen();
    }
  }
}

void handlePinEntry() {
  char key = keypad.getKey();
  
  if (key) {
    if (key >= '0' && key <= '9') {
      // Ziffer eingegeben
      if (enteredPIN.length() < PIN_LENGTH) {
        enteredPIN += key;
        updatePinDisplay();
        
        // Bei 4 Ziffern: Sende an Server
        if (enteredPIN.length() == PIN_LENGTH) {
          sendToServer();
        }
      }
    } 
    else if (key == '*') {
      // Löschen (Backspace)
      if (enteredPIN.length() > 0) {
        enteredPIN.remove(enteredPIN.length() - 1);
        updatePinDisplay();
      }
    }
    else if (key == '#') {
      // Abbrechen
      cancelOperation();
    }
  }
}

void handleServerResponse() {
  if (Serial.available() > 0) {
    String response = Serial.readStringUntil('\n');
    response.trim();
    
    Serial.print("SERVER_RESPONSE:");
    Serial.println(response);
    
    if (response == "OK" || response == "ACCESS_GRANTED") {
      currentState = ACCESS_GRANTED;
    } 
    else if (response == "DENIED" || response == "ACCESS_DENIED" || response == "WRONG_PIN") {
      currentState = ACCESS_DENIED;
    }
  }
}

void handleAccessGranted() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Zugang gewaehrt");
  lcd.setCursor(0, 1);
  lcd.print("Willkommen!");
  
  // Sende OPEN an Slave
  Serial.println("SENDING_OPEN_TO_SLAVE");
  sendToSlave("OPEN");
  
  // Akustisches Feedback (optional: Buzzer an Pin)
  tone(11, 1000, 200);  // Falls Buzzer an Pin 11
  
  delay(3000);
  
  // Zurück zu IDLE
  showIdleScreen();
  currentState = IDLE;
  resetVariables();
}

void handleAccessDenied() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Zugang verweigert!");
  lcd.setCursor(0, 1);
  lcd.print("Falsche PIN");
  
  // Akustisches Feedback (Fehler-Ton)
  tone(11, 200, 500);
  
  delay(3000);
  
  // Zurück zu IDLE
  showIdleScreen();
  currentState = IDLE;
  resetVariables();
}

void sendToServer() {
  // Sende UID und PIN an Raspberry Pi
  Serial.print("UID:");
  Serial.print(currentUID);
  Serial.print(";PIN:");
  Serial.println(enteredPIN);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Pruefe...");
  lcd.setCursor(0, 1);
  lcd.print("Bitte warten");
  
  currentState = VALIDATING_SERVER;
  serverRequestTime = millis();
}

void sendToSlave(String command) {
  Wire.beginTransmission(SLAVE_ADDRESS);
  Wire.write(command.c_str());
  Wire.endTransmission();
}

String requestFromSlave() {
  String response = "";
  
  Wire.requestFrom(SLAVE_ADDRESS, 32);  // Bis zu 32 Bytes lesen
  
  while (Wire.available()) {
    char c = Wire.read();
    if (c == '\n' || c == '\r' || c == '\0') break;
    if (c >= 0x20 && c <= 0x7E) {  // Nur druckbare ASCII
      response += c;
    }
  }
  
  response.trim();
  return response;
}

String extractUID(String rawData) {
  // Extrahiere UID nach "UID:" bis zum nächsten Nicht-Hex-Zeichen
  String uid = "";
  int startIdx = rawData.indexOf("UID:");
  
  if (startIdx >= 0) {
    startIdx += 4;  // Nach "UID:"
    
    for (int i = startIdx; i < rawData.length(); i++) {
      char c = rawData[i];
      
      // Nur Hex-Zeichen (0-9, A-F, a-f)
      if ((c >= '0' && c <= '9') || (c >= 'A' && c <= 'F') || (c >= 'a' && c <= 'f')) {
        uid += (char)toupper(c);
      } else {
        break;  // Stoppe bei erstem Nicht-Hex
      }
    }
  }
  
  return uid;
}

void showIdleScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Bereit");
  lcd.setCursor(0, 1);
  lcd.print("Karte auflegen..");
}

void showPinScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("PIN eingeben:");
  lcd.setCursor(0, 1);
  lcd.print("____  *=Del #=C");
}

void updatePinDisplay() {
  lcd.setCursor(0, 1);
  
  // Zeige Sterne für eingegebene Ziffern
  for (int i = 0; i < PIN_LENGTH; i++) {
    if (i < enteredPIN.length()) {
      lcd.print('*');
    } else {
      lcd.print('_');
    }
  }
  
  lcd.print("  *=Del #=C");
}

void checkPinTimeout() {
  if (millis() - pinStartTime > PIN_TIMEOUT) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Timeout!");
    lcd.setCursor(0, 1);
    lcd.print("Abgebrochen");
    
    delay(2000);
    
    showIdleScreen();
    currentState = IDLE;
    resetVariables();
  }
}

void checkServerTimeout() {
  if (millis() - serverRequestTime > 10000) {  // 10 Sekunden Timeout
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Server Timeout!");
    lcd.setCursor(0, 1);
    lcd.print("Keine Antwort");
    
    Serial.println("SERVER_TIMEOUT");
    
    delay(3000);
    
    showIdleScreen();
    currentState = IDLE;
    resetVariables();
  }
}

void cancelOperation() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Abgebrochen");
  
  delay(1500);
  
  showIdleScreen();
  currentState = IDLE;
  resetVariables();
}

void resetVariables() {
  currentUID = "";
  enteredPIN = "";
  waitingForPIN = false;
  waitingForServerResponse = false;
}
