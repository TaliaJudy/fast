from flask import Flask, request, Response, jsonify
import os
import time

app = Flask(__name__)

@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/download")
def download():
    """Send a stream of bytes for testing download speed"""
    size = int(request.args.get("size", 10 * 1024 * 1024))  # default 10MB
    chunk = int(request.args.get("chunk", 64 * 1024))       # default 64KB
    def generate():
        sent = 0
        buf = os.urandom(chunk)
        while sent < size:
            to_send = min(chunk, size - sent)
            yield buf[:to_send]
            sent += to_send
    return Response(generate(), mimetype="application/octet-stream")

@app.route("/upload", methods=["POST"])
def upload():
    """Receive data for testing upload speed"""
    data = request.get_data()
    size = len(data)
    return jsonify({"status": "ok", "size": size})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
