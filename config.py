import os

# All secrets come from environment variables (set in Render).
# The git history of the private repo still contains the original values.
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = int(os.environ["CHAT_ID"])

# Telegram channel/group button link shown under each forwarded OTP
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/ys_personalgroup")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "ys_personalgroup")

# CR API (used only by the live forwarding loop, not the country sender).
API_URL = os.getenv("API_URL", "")
API_TOKEN = os.getenv("API_TOKEN", "")

# How many records to fetch from the API on each poll (max 200)
RECORDS = 100

# Poll interval in seconds
POLL_INTERVAL = 30

# File used to remember which OTPs were already forwarded (so we don't re-send on restart)
STATE_FILE = "state.json"
