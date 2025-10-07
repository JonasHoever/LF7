import mysql.connector as mysql
from src.db_config import get_connection
from argon2 import PasswordHasher
import serial
from datetime import date, datetime

class Sql():
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def query(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()
    
    def insert_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.conn.commit()
        return self.cursor.fetchall()
    
    def query_to_list(self, query):
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [list(row) for row in rows]
    
class UserSystem():
    def __init__(self):
        self.sql = Sql()
        self.ph = PasswordHasher()

    def register_nfc_tag(self, nfc_tag, name, surname):
        try:
            res = self.sql.insert_query("INSERT INTO users (nfc_tag, name, surname) VALUES (%s,%s,%s)",(nfc_tag,name,surname))
            print(res)
            return True
        except Exception as e:
            print(e)
            return False, e

    def check_pin_by_nfc(self, nfc_tag):
        result = self.sql.query("SELECT pin FROM users WHERE nfc_tag = %s", (nfc_tag,))
        if result and result[0][0] is not None:
            return True
        return False

    def get_user_id_by_nfc(self, nfc_tag):
        uid = self.sql.query("SELECT id from users where nfc_tag = %s",(nfc_tag,))
        return uid

    def get_hashed_pin_by_nfc(self, nfc_tag):
        result = self.sql.query("SELECT pin FROM users WHERE nfc_tag = %s", (nfc_tag,))
        if result:
            return result[0][0]
        return None

    def check_request(self, nfc_tag):
        query = "SELECT id FROM users WHERE nfc_tag = %s LIMIT 1"
        result = self.sql.query(query, (nfc_tag,))
        result2 = self.check_pin_by_nfc(nfc_tag)
        return bool(result, result2)
            
    def signup(self, nfc_tag, pin):
        try:
            hashed_pin = self.ph.hash(str(pin))
            self.sql.insert_query("insert into users (nfc_tag, pin) VALUES (%s, %s)", (nfc_tag, hashed_pin))
            print(f"User für {nfc_tag} angelegt!")
            return True
        except Exception as e:
            print(f"Fehler beim anlegen einer users für {nfc_tag}!")
            print(e)
            return False
    
    def signin(self, nfc_tag, pin):
        try:
            self.ph.verify(self.get_hashed_pin_by_nfc(nfc_tag), pin)
            print(f"Pin für {nfc_tag} angenommen!")
            uid_result = self.get_user_id_by_nfc(nfc_tag)
            uid = uid_result[0][0] if uid_result else None
            return True, uid
        except Exception as e:
            print(e)
            print(f"Pin für {nfc_tag} abgelehnt!")
            return False, None
            
class WorkTimeSystem():
    def __init__(self):
        self.sql = Sql()

    def check_status(self, uid):
        date_today = date.today()
        try:
            sessions_today = self.sql.query("SELECT session_id, status FROM user_data WHERE date = %s AND status = 1 ORDER BY checkin_time DESC",(date_today,))
            if not sessions_today:
                raise Exception("Keine aktive Session gefunden!")
            else:
                latest_session = sessions_today[0][0]
                return True, latest_session
        except Exception as e:
            print(e)
            return False, None
        
    def start_session(self, uid):
        current_timestamp = datetime.now()
        sql_current_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.sql.insert_query("insert into user_data (user_id, checkin_time) VALUES (%s, %s)",(uid,sql_current_timestamp))
            return True
        except Exception as e:
            print(e)
            return False
        
    def end_session(self, uid, session_id):
        current_timestamp = datetime.now()
        sql_current_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.sql.insert_query("UPDATE user_data SET checkout_time = %s, status = 0 WHERE user_id = %s AND session_id = %s",(sql_current_timestamp, uid, session_id))
            return True
        except Exception as e:
            print(e)
            return False

    def end_all_session(self, target_time_str):
        while True:
            now = datetime.now().strftime("%H:%M")
            if now == target_time_str:
                try:
                    self.sql.insert_query("UPDATE user_data SET status = 0 where status = 1")
                except Exception as e:
                    print(e)
                    return False

class LicenseSystem():
    def __init__(self):
        pass

    