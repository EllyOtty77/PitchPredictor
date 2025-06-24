import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve bot token from the environment variable
bot_token = os.getenv('BOT_TOKEN')

# Construct the Telegram API URL for getting updates
url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

# Make a GET request to the Telegram API
response = requests.get(url)

# Parse the response JSON into a Python dictionary
data = response.json()

# Print the chat IDs from the updates if there are any
if 'result' in data and len(data['result']) > 0:
    for update in data['result']:
        chat_id = update['message']['chat']['id']
        print(f"Chat ID: {chat_id}")
else:
    print("No updates found. Make sure you have sent a message to the bot.")
