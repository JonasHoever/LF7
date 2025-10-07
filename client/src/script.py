import requests
import serial

class UserSystemClient():
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
            return e, None

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
    
    def signin(self, nfc_tag):
        pin_bool = False
        while pin_bool == False:
            pin = input("Bitte geben Sie Ihre 4-stellige PIN ein: ")
            if len(pin) == 4 and pin.isdigit():
                print("Pin format korrekt!")
                pin_bool = True
                try:
                    res = self.fetch_signin(nfc_tag, pin)
                    if res[0] == True:
                        return res[0], res[1], res[2]
                    elif res[0] == False:
                        pin_bool == False
                    else:
                        raise Exception
                except Exception as e:
                    print(e)
                    return False, None, None
            else:
                print("Ungültiger Pin, bitte erneut eingeben!")
                pin_bool = False
                pin_confirmed = False
        
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
    
    def fetch_signin(self, nfc_tag, pin):
        response = requests.post(
            f"{self.server_url}/nfc/signin",
            json={"nfc_tag": nfc_tag, "pin": pin}
        )
        data = response.json()
        return data.get("success"), data.get("user_id"), data.get("name")

    
class Client_Short_Function():
    def __init__(self):
        self.USC = UserSystemClient()

    def request(self, nfc_tag):
        check_res, check_pin = self.USC.request(nfc_tag)
        if check_res == False:
            print(f"NFC-tag: {nfc_tag} nicht registriert!")
            print("Done!")
            return 
        elif check_res == True and check_pin == False:
            print(f"Pin für Tag: {nfc_tag} nicht gesetzt!")
            res = self.USC.singup(nfc_tag)
            print(res)
            print("Done!")
            return
        elif check_res == True and check_pin == True:
            print("Bitte Anmelden!")
            res = self.USC.signin(nfc_tag)
            print(res)
            print("Done!")
            return
        else:
            print("Fehler!")
            print(check_res)
            print("Done!")
            return