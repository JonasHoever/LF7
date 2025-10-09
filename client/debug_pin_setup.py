#!/usr/bin/env python3
"""
PIN-Setup Debug Test
"""
import requests
import json

def test_pin_setup():
    nfc_tag = "898AB101"
    
    print("1️⃣ Teste Tag-Status VOR PIN-Setup...")
    response = requests.post("http://192.180.160.5:4001/nfc/request", 
                           json={"nfc_tag": nfc_tag})
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Antwort: {response.json()}")
    
    print("\n2️⃣ Teste PIN-Setup...")
    response = requests.post("http://192.180.160.5:4001/nfc/signup", 
                           json={"nfc_tag": nfc_tag, "pin": "1234"})
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Antwort: {response.json()}")
    
    print("\n3️⃣ Teste Tag-Status NACH PIN-Setup...")
    response = requests.post("http://192.180.160.5:4001/nfc/request", 
                           json={"nfc_tag": nfc_tag})
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Antwort: {response.json()}")
    
    print("\n4️⃣ Teste Login mit PIN...")
    response = requests.post("http://192.180.160.5:4001/nfc/signin", 
                           json={"nfc_tag": nfc_tag, "pin": "1234"})
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Antwort: {response.json()}")

if __name__ == "__main__":
    test_pin_setup()