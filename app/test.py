import os
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram sendMessage endpoint
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Payload message
payload = {
    "chat_id": CHAT_ID,
    "text": "🎉 Bot setup complete! I’m ready to send match predictions.",
    "parse_mode": "Markdown"
}

# Send the message
response = requests.post(url, data=payload)

# Confirm it worked
if response.status_code == 200:
    print("✅ Message sent successfully!")
else:
    print("❌ Error sending message:", response.text)
