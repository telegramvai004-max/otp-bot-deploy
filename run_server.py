import os
import threading
import time

import requests
from flask import Flask, jsonify

import country_bot

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(ok=True, status="running")


def start_bot():
    country_bot.main()


PUBLIC_URL = os.environ.get("PUBLIC_URL", "")


def self_ping():
    """Ping the public URL every 4 min so Render free tier never sleeps."""
    if not PUBLIC_URL:
        return
    while True:
        try:
            requests.get(PUBLIC_URL, timeout=15)
        except Exception:
            pass
        time.sleep(240)


PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)