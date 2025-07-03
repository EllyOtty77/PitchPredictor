import requests
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
print(response.json())
