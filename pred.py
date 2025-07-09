import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database path
DB_PATH = os.getenv('DB_PATH')

# Function to generate predicitons
def generate_predictions():
    """Generates match predictions from Upcomingmatches and saves to Predictions table."""
    
    conn = sqlite3.connect(DB_PATH)
    query = '''
    SELECT "Home Team", "Away Team", "League",
    "HomePower", "AwayPower", "H1.5", "A1.5",
    "H2.5", "A2.5", "H3.5", "A3.5", "1", "2", 
    "HomeBTTS", "AwayBTTS", "HomeGP", 
    "Home Position", "Away Position", "Home GD",
    "Home Form", "Away Form", 
    ABS("HomePower" - "AwayPower") AS "Powerdiff","Match Date"
    FROM Upcomingmatches
    ORDER BY "Match Date" ASC
    '''
    
    df = pd.read_sql(query, conn)
    conn.close()

    # --- Over 1.5 Goals Prediction ---
    over_df = df[((df['H1.5'] > 90) | (df['A1.5'] > 90)) & (df['Powerdiff'] >= 30)].copy()
    over_df['Prediction'] = 'Over 1.5'
    over_df['Odd'] = 1.23

    # --- Home Team Win Prediction Based on Rank/Form ---
    pos_home = df[
        (df['Powerdiff'] > 50) &
        (df['Home Form'].str.count('W') > 4) &
        (df['Home Position'] <= 3)
    ].copy()

    home_df = df[
        (df['Powerdiff'] >= 80) &
        (df['Home Form'].str.count('W') >= 3) &
        (df['Away Form'].str.count('L') > 3)
    ].copy()

    win_df = pd.concat([home_df, pos_home], axis=0)
    win_df['Prediction'] = 'Home'
    win_df['Odd'] = win_df['1']

    # --- Combine Predictions ---
    pred_df = pd.concat([win_df, over_df], axis=0)
    pred_df = pred_df[['Home Team', 'Away Team', 'League', 'Prediction', 'Odd', 'Match Date']]
    pred_df.drop_duplicates(inplace=True)
    pred_df.sort_values(by='Match Date', inplace=True)
    pred_df.reset_index(drop=True, inplace=True)

    # Remove first row 
    pred_df = pred_df[1:]

    # --- Calculate Total Accumulator Odd ---
    total_odd = round(pred_df['Odd'].prod(), 2)
    
    # --- Save Predictions to DB ---
    conn = sqlite3.connect(DB_PATH)
    pred_df['Success'] = 0  # Add success column
    pred_df.to_sql('Predictions', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

    # --- Output ---
    print("\n📋 Match Predictions:")
    print(pred_df.head(3))

    print(f"\n Accumulator value: {total_odd}")
    print(f" Updated database with {len(pred_df)} matches")

    return pred_df, total_odd
    

# Function to automatically update prediction results
def update_prediction_results():
    conn = sqlite3.connect(DB_PATH)

    try:
        # Step 1: Get last updated prediction ID
        last_id_result = conn.execute("SELECT last_updated_id FROM PredictionUpdateLog ORDER BY id DESC LIMIT 1").fetchone()
        last_updated_id = last_id_result[0] if last_id_result else 0

        # Step 2: Get new predictions
        preds_sql = f"""
            SELECT *
            FROM Predictions
            WHERE id > {last_updated_id}
            ORDER BY id ASC
        """
        preds_df = pd.read_sql(preds_sql, conn)

        # Step 3: Load football results
        results_df = pd.read_sql("SELECT * FROM footballresults", conn)

        # Step 4: Process and compute total goals
        results_df["Total Goals"] = results_df["Score"].apply(
            lambda x: sum(map(int, x.split(" - "))) if isinstance(x, str) and " - " in x else None
        )

        # Step 5: Loop and evaluate prediction correctness
        updates = []
        for _, pred in preds_df.iterrows():
            home = pred["Home Team"]
            away = pred["Away Team"]
            match_date = pred["Match Date"]
            prediction = pred["Prediction"]
            pred_id = pred["id"]

            # Try match
            match = results_df[
                (results_df["Home Team"] == home) &
                (results_df["Away Team"] == away) &
                (results_df["Match Date"] == match_date)
            ]

            if not match.empty:
                total_goals = match["Total Goals"].values[0]
                actual_winner = match["Result"].iloc[0]

                success = 0
                if "Over" in prediction:
                    limit = float(prediction.split(" ")[1])
                    if total_goals > limit:
                        success = 1
                elif prediction == "Home" and actual_winner == "1":
                    success = 1
                elif prediction == "Away" and actual_winner == "2":
                    success = 1
                elif prediction == "Draw" and actual_winner == "X":
                    success = 1

                updates.append((success, pred_id))

        # Step 6: Update Database
        for success, pred_id in updates:
            conn.execute("UPDATE Predictions SET Success = ? WHERE id = ?", (success, pred_id))
            print(f"Updated prediction ID {pred_id} ➝ Success = {success}")

        conn.commit()
        print("✅ Prediction results updated.")
        
        # Step 7: Log the last updated ID
        if updates:
            last_updated_id = updates[-1][1]
            conn.execute("INSERT INTO PredictionUpdateLog (last_updated_id) VALUES (?)", (last_updated_id,))
            conn.commit()
            print(f"\n📘 Logged last updated ID: {last_updated_id}")
        else:
            print("🟡 No new predictions to update.")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        conn.close()
