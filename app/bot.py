import os
import sqlite3
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DB_PATH = os.getenv('DB_PATH')

def fetch_predictions():
    try:
        # Connect and load predictions
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT "Home Team", "Away Team", "League", "Odd", "Prediction", "Match Date"
            FROM Predictions
            ORDER BY "Match Date" ASC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return "⚠️ No matches found.", 0

        # Convert Match Date and filter for future matches
        df['Match Date'] = pd.to_datetime(df['Match Date'])
        df = df[df['Match Date'] > datetime.now()]

        if df.empty:
            return "📭 No upcoming matches.", 0

        # Calculate accumulator value
        acc_val = df['Odd'].prod()

        # Build message
        message = "🔥 *Today's Accumulator Picks*\n\n"
        for _, row in df.iterrows():
            home = row["Home Team"]
            away = row["Away Team"]
            league = row["League"]
            odd = row["Odd"]
            prediction = row["Prediction"]
            date = row["Match Date"].strftime("%A %d/%m %H:%M")

            predicted_team = (
                away if prediction.lower() == "away"
                else home if prediction.lower() == "home"
                else prediction
            )

            message += f"⚽ {home} vs {away} ({league})\n" \
                       f"🔮 Prediction: *{predicted_team}*\n" \
                       f"💸 Odd: {odd:.2f}\n" \
                       f"🗓️ {date}\n\n"

        message += f"🔥 *Accumulator Value:* {acc_val:.2f}"

        return message, acc_val
    except Exception as e:
        return f"❌ Error fetching predictions: {e}", 0

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, data=payload)
    return res.status_code == 200

# Main logic
if __name__ == "__main__":
    msg, acc_val = fetch_predictions()
    success = send_to_telegram(msg)

    if success:
        print("✅ Predictions sent to Telegram.")
    else:
        print("❌ Failed to send message.")
