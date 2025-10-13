import requests
import serial

class UserSystemClient():
    def __init__(self):
        self.server_url = "http://192.180.160.5:4001"

    def request(self, nfc_tag):
        try:
            # Verwende die korrigierte fetch_request Funktion
            exists, pin_set = self.fetch_request(nfc_tag)
            print(f"🔍 Tag-Status: exists={exists}, pin_set={pin_set}")
            print(exists)
            print(pin_set)
            return exists, pin_set
        except Exception as e:
            print(f"❌ Fehler in request: {e}")
            return False, False

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
                try:
                    res = self.fetch_signin(nfc_tag, pin)
                    if res[0] == True:
                        return res[0], res[1], res[2]
                    else:
                        print("Falsche PIN, bitte erneut eingeben!")
                        pin_bool = False  # Schleife läuft weiter
                except Exception as e:
                    print(e)
                    return False, None, None
            else:
                print("Ungültiger Pin, bitte erneut eingeben!")
                pin_bool = False
        
        print("User angelegt!")
        return True

    def fetch_signup(self, nfc_tag, pin):
        """Erstellt PIN für Tag"""
        url = f"{self.server_url}/nfc/signup"
        data = {"nfc_tag": nfc_tag, "pin": pin}
        try:
            print(f"📡 PIN-Setup Request: {url} mit {data}")
            response = requests.post(url, json=data, timeout=10)  # Längeres Timeout
            print(f"📨 PIN-Setup Antwort: Status={response.status_code}, Body={response.text}")
            result = response.json()
            return result.get("success", False)
        except Exception as e:
            print(f"❌ Fehler bei PIN-Setup: {e}")
            return False
    
    def fetch_request(self, nfc_tag):
        """Prüft Tag-Status"""
        url = f"{self.server_url}/nfc/request"
        data = {"nfc_tag": nfc_tag}
        try:
            response = requests.post(url, json=data, timeout=10)  # Längeres Timeout
            if response.status_code == 200:
                result = response.json()
                return result.get("exists", False), result.get("pin_set", False)
        except Exception as e:
            print(f"❌ Fehler bei request: {e}")
        return False, False
    
    def fetch_signin(self, nfc_tag, pin):
        """Login mit PIN - KORRIGIERTE VERSION"""
        url = f"{self.server_url}/nfc/signin"
        data = {"nfc_tag": nfc_tag, "pin": pin}
        try:
            print(f"🔑 Login-Versuch: {url} mit Tag={nfc_tag}, PIN={pin}")
            response = requests.post(url, json=data, timeout=10)  # Längeres Timeout
            print(f"📨 Server-Antwort: Status={response.status_code}, Body={response.text}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                user_id = result.get("user_id", None)
                name = result.get("name", None)
                
                print(f"🔍 Login-Ergebnis: success={success}, user_id={user_id}, name={name}")
                return success, user_id, name
        except Exception as e:
            print(f"❌ Login-Fehler: {e}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()}")
        
        return False, None, None
    
    def worktime_script(self, uid):
        url = f"{self.server_url}/worktimesystem/sessions"

        try:
            uid_int = int(uid)
        except (TypeError, ValueError):
            print(f"❌ Ungültige UID übergeben: {uid!r}")
            return False, None

        data = {"user_id": uid_int}
        try:
            print(f"🕒 Stempel-Versuch für UID={uid_int}")
            response = requests.post(url, json=data, timeout=10)
            print(f"📨 Server-Antwort: Status={response.status_code}, Body={response.text}")

            if response.status_code != 200:
                return False, None

            # JSON sicher parsen
            if response.headers.get("Content-Type", "").startswith("application/json"):
                result = response.json()
            else:
                result = {}

            success = bool(result.get("success", False))
            action = result.get("action", None)
            start_time = result.get("start_time", None)
            end_time = result.get("end_time", None)
            diff = result.get("diff", None)
            print(f"🔍 Worktime-Ergebnis: success={success}, action={action}")
            return success, action, start_time, end_time, diff
        except Exception as e:
            print(f"❌ Worktime-Fehler: {e}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()}")
            return False, None
    
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

class Client_Short_Function2():
    def __init__(self):
        self.USC = UserSystemClient()

    def request(self, nfc_tag):
        # Web-UI kompatible Funktion die brauchbare Daten zurückgibt
        check_res, check_pin = self.USC.request(nfc_tag)
        if check_res == False:
            print(f"NFC-tag: {nfc_tag} nicht registriert!")
            print("Done!")
            return {
                'status': 'not_registered',
                'message': f'NFC-Tag {nfc_tag} ist nicht registriert. Bitte registrieren Sie sich zuerst.',
                'action_needed': 'register',
                'nfc_tag': nfc_tag
            }
        elif check_res == True and check_pin == False:
            print(f"Pin für Tag: {nfc_tag} nicht gesetzt!")
            print("Done!")
            return {
                'status': 'needs_pin_setup',
                'message': f'Willkommen! Bitte erstellen Sie eine 4-stellige PIN für Tag {nfc_tag}.',
                'action_needed': 'pin_setup',
                'nfc_tag': nfc_tag
            }
        elif check_res == True and check_pin == True:
            print("Tag ist vollständig eingerichtet!")
            return {
                'status': 'ready_for_login',
                'message': f'✅ Tag {nfc_tag} ist registriert und PIN ist gesetzt. Login möglich!',
                'action_needed': 'pin_login', 
                'nfc_tag': nfc_tag
            }
        else:
            print("Fehler!")
            print(check_res)
            print("Done!")
            return {
                'status': 'error',
                'message': f'Unbekannter Fehler bei Tag {nfc_tag}. Bitte versuchen Sie es erneut.',
                'action_needed': 'none',
                'nfc_tag': nfc_tag
            }
            return

    def web_request(self, nfc_tag):
        """Web-UI kompatible Version - gibt strukturierte Daten zurück"""
        try:
            check_res, check_pin = self.USC.request(nfc_tag)
            
            if check_res == False:
                return {
                    "status": "not_registered",
                    "message": f"NFC-Tag {nfc_tag} ist nicht registriert!",
                    "action_needed": "register",
                    "nfc_tag": nfc_tag
                }
            elif check_res == True and check_pin == False:
                return {
                    "status": "needs_pin_setup",
                    "message": f"PIN für Tag {nfc_tag} muss erstellt werden!",
                    "action_needed": "setup_pin",
                    "nfc_tag": nfc_tag
                }
            elif check_res == True and check_pin == True:
                return {
                    "status": "needs_login",
                    "message": f"Bitte melden Sie sich mit Ihrer PIN an!",
                    "action_needed": "login",
                    "nfc_tag": nfc_tag
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unbekannter Fehler: {check_res}",
                    "action_needed": "none",
                    "nfc_tag": nfc_tag
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fehler bei der Anfrage: {str(e)}",
                "action_needed": "none",
                "nfc_tag": nfc_tag
            }

    def web_signup(self, nfc_tag, pin, pin_confirm):
        """Web-UI PIN-Erstellung - KORRIGIERTE VERSION"""
        print(f"🔧 web_signup aufgerufen: Tag={nfc_tag}, PIN={pin}, Confirm={pin_confirm}")
        
        if len(pin) != 4 or not pin.isdigit():
            print("❌ PIN Format ungültig")
            return {
                "success": False,
                "message": "PIN muss genau 4 Ziffern haben!"
            }
        
        if pin != pin_confirm:
            print("❌ PIN Bestätigung stimmt nicht überein")
            return {
                "success": False,
                "message": "PINs stimmen nicht überein!"
            }
        
        try:
            print(f"📡 Rufe USC.fetch_signup({nfc_tag}, {pin}) auf...")
            success = self.USC.fetch_signup(nfc_tag, pin)
            print(f"✅ USC.fetch_signup Ergebnis: {success}")
            
            if success:
                return {
                    "success": True,
                    "message": "PIN erfolgreich erstellt!"
                }
            else:
                return {
                    "success": False,
                    "message": "Fehler beim Erstellen der PIN!"
                }
        except Exception as e:
            print(f"❌ Exception in web_signup: {e}")
            import traceback
            print(f"🔍 Full Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Fehler beim Erstellen der PIN: {str(e)}"
            }

    def web_signin(self, nfc_tag, pin):
        """Web-UI Login - KORRIGIERTE VERSION"""
        if len(pin) != 4 or not pin.isdigit():
            return {
                "success": False,
                "message": "PIN muss genau 4 Ziffern haben!"
            }
        
        try:
            print(f"🔑 Web-Login für Tag: {nfc_tag} mit PIN: {pin}")
            success, user_id, name = self.USC.fetch_signin(nfc_tag, pin)
            print(f"🔍 Login-Ergebnis: success={success}, user_id={user_id}, name={name}")
            
            if success:
                return {
                    "success": True,
                    "message": f"Willkommen, {name}!",
                    "user_id": user_id,
                    "name": name
                }
            else:
                return {
                    "success": False,
                    "message": "Falsche PIN oder Login-Fehler!"
                }
        except Exception as e:
            print(f"❌ Web-Login Fehler: {e}")
            return {
                "success": False,
                "message": f"Fehler beim Login: {str(e)}"
            }
        

