import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8403980211:AAEe7sRuzrb_HlvS0DK-NOtI6KJ0nRGdBcM")
CHAT_ID = int(os.getenv("CHAT_ID", -1003226050176))

# Telegram channel/group button link shown under each forwarded OTP
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/ys_personalgroup")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "ys_personalgroup")

API_URL = os.getenv("API_URL", "http://147.135.212.197/crapi/had/viewstats")
API_TOKEN = os.getenv("API_TOKEN", "R1dXQjRSQnZXcohDiYFmgImOh0JBbVVVgpRRelWVZX9gk1BjeoSM")

# How many records to fetch from the API on each poll (max 200)
RECORDS = 100

# Poll interval in seconds
POLL_INTERVAL = 30

# File used to remember which OTPs were already forwarded (so we don't re-send on restart)
STATE_FILE = "state.json"
