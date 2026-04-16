from flask_cors import CORS
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Server is live"
