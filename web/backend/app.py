from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/api/status")
def status():
    """Return a simple health snapshot."""
    return jsonify(status="ok", component="web-backend"), 200
