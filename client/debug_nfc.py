#!/usr/bin/env python3
"""
Debug-Script für NFC-Tag Registrierung und Status-Prüfung
"""

import requests
import json

# Server-Konfiguration
SERVER_URL = "http://192.180.160.5:4001"

def test_server_connection():
    """Teste Verbindung zum Server"""
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        print(f"✅ Server erreichbar: {response.status_code}")
        print(f"📄 Antwort: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Server nicht erreichbar: {e}")
        return False

def test_registration(nfc_tag, name, surname):
    """Teste NFC-Tag Registrierung"""
    try:
        url = f"{SERVER_URL}/nfc/register/{nfc_tag}/{name}/{surname}"
        print(f"📡 Teste Registrierung: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📨 Status: {response.status_code}")
        print(f"📄 Antwort: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"💥 Fehler bei Registrierung: {e}")
        return False

def test_nfc_request(nfc_tag):
    """Teste NFC-Tag Status-Prüfung"""
    try:
        url = f"{SERVER_URL}/nfc/request"
        data = {"nfc_tag": nfc_tag}
        
        print(f"📡 Teste NFC-Request: {url}")
        print(f"📦 Daten: {data}")
        
        response = requests.post(url, json=data, timeout=10)
        print(f"📨 Status: {response.status_code}")
        print(f"📄 Antwort: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Parsed Result: {result}")
            print(f"   - exists: {result.get('exists')}")
            print(f"   - pin_set: {result.get('pin_set')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"💥 Fehler bei NFC-Request: {e}")
        return False

def main():
    print("🔧 NFC-System Debug")
    print("=" * 50)
    
    # 1. Server-Verbindung testen
    print("\n1️⃣ Teste Server-Verbindung...")
    if not test_server_connection():
        print("❌ Server nicht erreichbar - Abbruch")
        return
    
    # 2. Test-Tag für Debug
    test_tag = "898AB101"  # Dein gescannter Tag
    test_name = "Test"
    test_surname = "User"
    
    print(f"\n2️⃣ Teste Tag-Status VOR Registrierung...")
    test_nfc_request(test_tag)
    
    print(f"\n3️⃣ Teste Registrierung...")
    if test_registration(test_tag, test_name, test_surname):
        print("✅ Registrierung erfolgreich")
    else:
        print("❌ Registrierung fehlgeschlagen")
    
    print(f"\n4️⃣ Teste Tag-Status NACH Registrierung...")
    test_nfc_request(test_tag)
    
    print("\n" + "=" * 50)
    print("🏁 Debug abgeschlossen")

if __name__ == "__main__":
    main()