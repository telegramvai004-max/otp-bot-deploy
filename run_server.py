import os
import threading

from flask import Flask, jsonify

import country_bot

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(ok=True, status="running")


def start_bot():
    country_bot.main()


PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=PORT)