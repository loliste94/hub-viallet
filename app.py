"""
Hub Viallet — serveur web minimaliste.
Sert le dashboard HTML et expose /api/data (lecture) et /api/update (écriture).
"""
import json
import os
from flask import Flask, jsonify, send_from_directory, request, abort

app = Flask(__name__, static_folder="static")

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "hub_data.json")
API_TOKEN = os.environ.get("HUB_TOKEN", "changeme")


def load_data() -> dict:
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/data")
def get_data():
    return jsonify(load_data())


@app.route("/api/update", methods=["POST"])
def update_data():
    token = request.headers.get("X-Hub-Token", "")
    if token != API_TOKEN:
        abort(401)
    data = request.get_json(force=True)
    if not data:
        abort(400)
    save_data(data)
    return jsonify({"ok": True, "updated_at": data.get("updated_at", "")})


@app.route("/api/health")
def health():
    d = load_data()
    return jsonify({"ok": True, "updated_at": d.get("updated_at", "jamais")})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
