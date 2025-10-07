import requests
import serial

class Usersystem_client():
    def __init__(self):
        self.server_url = "http://192.180.160.5:4001"

    def request(self, nfc_tag):
        try:
            check_nfc = self.fetch_request(nfc_tag)
            print(check_nfc['exists'])
            print(check_nfc['pin_set'])
            return check_nfc['exists'], check_nfc['pin_set']
        except Exception as e:
            print(e)
            return None, None

    def singup(self, nfc_tag):
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
                    print("PINs stimmen nicht überein, bitte die neue PIN eingeben!")
                    pin_bool = False
                    pin_confirmed = False
            else:
                print("Ungültiger Pin, bitte erneut eingeben!")
                pin_bool = False
                pin_confirmed = False
        if pin_bool == True and pin_confirmed == True:
            try:
                result = self.fetch_signup(nfc_tag, pin)
                return result["success"]
            except Exception as e:
                print(e)
                return False
        
        print("User angelegt!")
        return True
    
    def fetch_signup(self, nfc_tag, pin):
        response = requests.post(
            f"{self.server_url}/nfc/signup",
            json={"nfc_tag": nfc_tag, "pin": pin}
        )
        return response.json()
    
    def fetch_request(self, nfc_tag):
        response = requests.post(
            f"{self.server_url}/nfc/request",
            json={"nfc_tag": nfc_tag}
        )
        return response.json()