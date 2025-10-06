    def create_user(self, nfc_tag):
        pin_bool = False
        pin_confirmed = False
        while pin_bool == False or pin_confirmed == False:
            pin = input("Bitte erstellen Sie Ihre neue 4-stellige PIN: ")
            if len(pin) == 4 and pin.isdigit():
                print("Pin format korrekt!")
                pin_bool = True
                if input("Bitte 4-stellige Pin bestätigen: ") == pin:
                    pin_confirmed = True
                else:
                    print("PINs stimmen nicht überein, bitte komplett neue PIN eingeben!")
                    pin_bool = False
                    pin_confirmed = False
            else:
                print("Ungültiger Pin, bitte erneut eingeben!")
                pin_bool = False
                pin_confirmed = False
        hashed_pin = str(self.ph.hash(pin))
        self.sql.insert_query("insert into users (nfc_tag, pin) VALUES (%s, %s)", (nfc_tag, hashed_pin))
        print("User angelegt!")
        return
    
    def login_user(self, nfc_tag):
        try_counter = 0
        while try_counter <= 2:
            pin_bool = False
            pin = input("Bitte geben Sie Ihre 4-stellige PIN ein: ")
            while not pin_bool:
                if len(pin) == 4 and pin.isdigit():
                    pin_bool = True
                else:
                    print("Ungültiger Pin, bitte erneut eingeben!")
                    pin = input("Bitte geben Sie Ihre 4-stellige PIN ein: ")
            try:
                verify_pin = self.ph.verify(self.get_hashed_pin_by_nfc(nfc_tag), pin)
                print("Pin angenommen!")
                return
            except Exception:
                print("Pin abgelehnt!")
                try_counter += 1
        if try_counter > 2:
            print("zu viele Fehlversuche!")
            return
        

import requests
import time

license_key = "ABC123"

while True:
    response = requests.post(
        "http://localhost:5000/license/ping",
        json={"license": license_key}
    )
    print(response.json())
    time.sleep(5)  # alle 5 Sekunden ein Ping