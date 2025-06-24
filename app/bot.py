# bot.py

import os
import sqlite3
import pandas as pd
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DB_PATH = os.getenv("DB_PATH", "soccermatches.db")  # fallback

def send_predictions():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = '''
            SELECT "Home Team", "Away Team", "League", "Odd", "Prediction", "Match Date"
            FROM Predictions
            ORDER BY "Match Date" ASC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            message = "⚠️ No match predictions found."
        else:
            df['Match Date'] = pd.to_datetime(df['Match Date'])
            df = df[df['Match Date'] > datetime.now()]
            if df.empty:
                message = "📭 No upcoming matches."
            else:
                acc_val = df['Odd'].prod()
                message = "🔥 *Today's Accumulator Picks*\n\n"
                for _, row in df.iterrows():
                    home = row["Home Team"]
                    away = row["Away Team"]
                    league = row["League"]
                    odd = row["Odd"]
                    prediction = row["Prediction"]
                    match_date = row["Match Date"].strftime("%A %d/%m %H:%M")

                    predicted_team = away if prediction.lower() == "away" else home if prediction.lower() == "home" else prediction
                    message += f"⚽ {home} vs {away} ({league})\n" \
                               f"🔮 Prediction: *{predicted_team}*\n" \
                               f"💸 Odd: {odd:.2f}\n" \
                               f"🗓️ {match_date}\n\n"
                message += f"🔥 *Accumulator Value:* {acc_val:.2f}"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        res = requests.post(url, data=payload)

        if res.status_code == 200:
            print("✅ Predictions sent to Telegram.")
        else:
            print("❌ Failed to send Telegram message:", res.text)
    except Exception as e:
        print("🚨 Error in send_predictions():", e)