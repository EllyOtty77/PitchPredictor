# Imports
import sqlite3
import pandas as pd
from eco import *
from pred import generate_predictions

# database path
DB_PATH = os.getenv('DB_PATH')

print('1. Fetch matches\n2. Update results')
date_input = input('Input your choice: ')
dates = generate_dates(date_input)
print("Generating match data for:", ", ".join(f"'{d}'" for d in dates))

# Fetch data
soccer_data = scrape_data(dates)
df = soccer_data.copy()

#  Process Depending on Input
if date_input == '1':
    df.drop(columns=['Score', 'Result'], inplace=True, errors='ignore')
    for col in ['1', 'X', '2']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.sort_values(by='Match Date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("\n📋 Upcoming Matches Preview:")
    print(df[['Home Team', 'Away Team', 'Match Date']].head(3))
    
    confirm = input("\nSave these upcoming matches to the database? (y/n): ").strip().lower()
    if confirm == 'y':
        with sqlite3.connect(DB_PATH) as conn:
            df.to_sql('Upcomingmatches', conn, if_exists='replace', index=False)
        print("✅ Upcoming matches saved to database.")
        # Trigger predictions after save
        generate_predictions()
    else:
        print("❌ Operation cancelled. No changes made.")

elif date_input == '2':
    df.drop(columns=['Pick', 'X'], inplace=True, errors='ignore')
    df.dropna(subset=['Score', 'Result'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("\n📋 Results Preview:")
    print(df[['Home Team', 'Away Team', 'Match Date']].tail(3))

    confirm = input("\nSave these results to the database? (y/n): ").strip().lower()
    if confirm == 'y':
        with sqlite3.connect(DB_PATH) as conn:
            df.to_sql('footballresults', conn, if_exists='append', index=False)
        print("✅ Match results saved to database.")
        
    else:
        print("❌ Operation cancelled. No changes made.")

else:
    print("⚠️ Invalid input. Please select option '1' or '2'.")
