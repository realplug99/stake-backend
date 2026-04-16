from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "✅ Server is live"
    @app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response
