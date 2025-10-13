from src import db_setup, script
from flask import Flask, session, request, jsonify
import threading
import requests

app = Flask(__name__)
app.secret_key = 'Banane'

dbs = db_setup.Init()
usys = script.UserSystem()
tsys = script.WorkTimeSystem()

dbs.init_db()

def end_all_sessions():
    tsys.end_all_session("23:59")

@app.route('/')
def start_page():
    return(f"please apply client on /register/client")

@app.route('/register/client')
def register_client():
    pass

@app.route('/nfc/register/<string:nfc_tag>/<string:name>/<string:surname>')
def register_nfc(nfc_tag, name, surname):
    register = usys.register_nfc_tag(nfc_tag, name, surname)
    if register[0] == True:
        return f"NFC-Tag {nfc_tag} für {name} {surname} wurde angelegt!"
    else:
        return str(register[1]), 400

@app.route('/nfc/request', methods=['POST'])
def request_nfc():
    data = request.get_json()
    nfc_tag = data.get('nfc_tag', None)
    result = usys.check_request(nfc_tag)
    return jsonify({"exists": result[0], "pin_set": result[1]})

@app.route('/nfc/signin', methods=['POST'])
def signin_nfc():
    data = request.get_json()
    nfc_tag = data.get('nfc_tag', None)
    pin = data.get('pin', None)
    success, uid, name = usys.signin(nfc_tag, pin)
    return jsonify({"success": success, "user_id": uid, "name": name})

@app.route('/nfc/signup', methods=['POST'])
def signup_nfc():
    data = request.get_json()
    nfc_tag = data.get('nfc_tag', None)
    pin = data.get('pin', None)
    success = usys.signup(nfc_tag, pin)
    return jsonify({"success": success})
@app.route('/get/name/by/id/<uid>/')
def get_name_by_id(uid):
    name, surname = usys.get_name_by_id(uid)
    return jsonify({"name":name, "surname":surname})
@app.route('/worktimesystem/sessions', methods=['POST'])
def sessions():
    start_time = None
    end_time = None
    diff = None
    success = False
    action = None
    
    data = request.get_json(silent=True) or {}
    print(f"POST /worktimesystem/sessions payload={data}")
    user_id = data.get('user_id')

    if user_id in (None, "", "null"):
        return jsonify({"success": False, "action": None, "message": "user_id fehlt"}), 400
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "action": None, "message": "user_id muss int sein"}), 400

    session_check = tsys.check_status(user_id)
    session_id = session_check[1] if session_check[1] is not None else None
    print(session_check)
    print(session_id)
    print("step1")
    if session_check[0] is False:
        try:
            success, start_time = tsys.start_session(user_id)
            action = "started"
            end_time = None
            diff = None
        except Exception as e:
            print(e)
            success = False
            action = "failure by starting session"
            start_time = None
            end_time = None
            diff = None
    elif session_check[0] is True:
        try:
            success, start_time, end_time, diff = tsys.end_session(user_id, session_id)
            action = "stopped"
        except Exception as e:
            print(e)
            success = False
            action = "failure by stopping session"
            start_time = None
            end_time = None
            diff = None
    else:
        success = False
        action = None
        start_time = None
        end_time = None
        diff = None

    return jsonify({"success": success, "action": action, "start_time": start_time ,"end_time": end_time, "diff": diff})

if __name__ == '__main__':
    threading.Thread(target=end_all_sessions, daemon=True).start()
    app.run(host="0.0.0.0",port=4001, debug=True)