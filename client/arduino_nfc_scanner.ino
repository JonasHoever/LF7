#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  
  // Warte bis Serial bereit ist
  while (!Serial) {
    delay(10);
  }
  
  // Keine Debug-Nachrichten an Serial senden!
  // Python soll nur reine Tag-IDs empfangen
}

void loop() {
  // Scanne kontinuierlich nach NFC-Tags
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    
    // UID als HEX-String zusammenbauen (ohne Leerzeichen)
    String tagID = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      if (mfrc522.uid.uidByte[i] < 0x10) {
        tagID += "0";  // Führende Null für einstellige Hex-Werte
      }
      tagID += String(mfrc522.uid.uidByte[i], HEX);
    }
    
    // Tag-ID in Großbuchstaben umwandeln
    tagID.toUpperCase();
    
    // NUR die Tag-ID senden - keine anderen Nachrichten!
    Serial.println(tagID);
    
    // Verhindere mehrfaches Lesen desselben Tags
    delay(2000);
    
    // Warte bis Tag weggenommen wird
    while (mfrc522.PICC_IsNewCardPresent()) {
      delay(100);
    }
    
    // Keine Debug-Nachrichten - Python soll nur Tag-IDs bekommen
  }
  
  delay(100); // Kleine Pause zwischen Scans
}