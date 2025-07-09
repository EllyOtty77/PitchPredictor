import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.parser import parse
import os
import time
import sqlite3
from dotenv import load_dotenv  

# Load environment variables
load_dotenv()   

# Import db path
DB_PATH = os.getenv('DB_PATH')

# Convert file path
def convert_filepath(file_path):
    """Convert Windows-style path to Unix-style path."""
    return file_path.replace('\\', '/')

# Get file creation time
def get_file_creation_time(file_path):
    """Return the file creation time formatted as 'YYYY-MM-DD HH:MM:SS'."""
    try:
        creation_time = os.path.getctime(file_path)
        return datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
    except FileNotFoundError:
        return "File not found"

# Safe conversion functions
def safe_int_conversion(text):
    """Safely convert text to integer."""
    try:
        return int(text)
    except ValueError:
        return None

def safe_float_conversion(text):
    """Safely convert text to float."""
    try:
        return float(text)
    except ValueError:
        return None

# Calculate goal difference
def gd_calc(goals_text):
    """Calculate goal difference from 'gf:ga' string."""
    gf, ga = map(int, goals_text.split(':'))
    return gf, ga, gf - ga



# Generate match dates
def get_adjusted_match_day():
    """Get the latest match day from DB, adjusted if match time is after 7AM."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('''
        SELECT "Home Team", "Away Team", "League", "Score", "Result", "Match Date"
        FROM footballresults
        ORDER BY "Match Date" DESC
    ''', conn)
    conn.close()

    df = df[:-1]  # Optional: skip last row
    df["Match Date"] = pd.to_datetime(df["Match Date"], format='mixed', errors='coerce')
    df = df.dropna(subset=["Match Date"])  # Clean up bad formats

    match_datetime = df.iloc[0]["Match Date"]
    return (
        match_datetime.date()
        if match_datetime.time() < pd.to_datetime("07:00").time()
        else (match_datetime + timedelta(days=1)).date()
    )

def generate_dates(date_input):
    """
    Generate a list of dates depending on the input:
    - '1' = Today (3 dates)
    - '2' = Adjusted match day from DB (4 dates)
    - Custom date (default 3 dates)
    """
    if date_input == '1':
        start_date = datetime.today().date()
        num_days = 3
    elif date_input == '2':
        start_date = get_adjusted_match_day()
        num_days = 4
    else:
        try:
            start_date = datetime.strptime(date_input, '%d-%m-%Y').date()
            num_days = 3
        except ValueError:
            raise ValueError("Invalid input. Use '1', '2', or a date in 'dd-mm-yyyy' format.")

    return [(start_date + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(num_days)]
    
# Parse datetime
def parse_date(date_str, time_str):
    """Parse date and time strings into a pandas datetime object."""
    try:
        date_obj = parse(date_str, dayfirst=True)
        datetime_str = f"{date_obj.strftime('%Y-%m-%d')} {time_str}"
        return pd.to_datetime(datetime_str, format="%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"Error parsing date: {e}")
        return None

# Clean goals from a text sheet
def clean_goals(sheet):
    """Parse goal entries from a text sheet."""
    goals = []
    for entry in sheet.split('\n'):
        if entry.strip():  # Skip empty lines
            player, minute = entry.rsplit(' ', 1)
            minute = int(minute.strip("'"))
            goals.append((player, minute))
    return goals

def scrape_data(dates):

    # Initialize an empty DataFrame to store all data
    all_data = pd.DataFrame()
    
    for date in dates:
        # Construct the URL
        url = f"https://www.soccereco.com/soccer-games?date={date}"
        # Send a GET request to the URL
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
    
        
        # List for storing temporary data
        home_teams = []
        away_teams = []
        scores = []
        result = []
        picks = []
        leagues = []
        home_odds = []
        draw_odds = []
        away_odds = []   
        home_form = []
        away_form = []
        match_dates = []
        match_times = []
        home1_5 = []
        away1_5 = []
        home2_5 = []
        away2_5 = []
        home3_5 = []
        away3_5 = []
        havg_scored = []
        h_avgconceded = []
        aavg_scored = []
        a_avgconceded = []
        home_power = []
        away_power = []
        home_btts = []
        away_btts = []
        home_rank = []
        away_rank = []
        home_pts = []
        away_pts = []
        home_gp = []
        away_gp = []
        home_w = []
        away_w = []
        home_d = []
        away_d = []
        home_l = []
        away_l = []
        home_gf = []
        home_ga = []
        home_gd = []
        away_gf = []
        away_ga = []
        away_gd = []
        
        # Extract information for each match item
        
        match_items = soup.find_all('a', {'class':'matchesbar-link'})
        
        for match_item in match_items:
            
            # Team names
            team_names = match_item.find_all('span', {'class':'teamname'})
            home_team = team_names[0]
            away_team = team_names[1]
                
            
            home_teams.append(home_team.text.strip())
            away_teams.append(away_team.text.strip())
            
            # Home team form   
            home = match_item.find('div', {'class':'home'})
            form_div = home.find('div', {'class': 'd-flex latest-matches'})
            if form_div:
                hform = form_div.text
            else:
                hform = 'None'
            home_form.append(hform)   
            
            #Away team form
            away = match_item.find('div', {'class':'away'})
            form_div = away.find('div', {'class': 'd-flex latest-matches'})
            if form_div:
                aform = form_div.text
            else:
                aform = 'None'
            
            away_form.append(aform)     
        
            # Picks
            pick = match_item.find('div', {'class': 'strong tipdisplay'})
            picks.append(pick.text)    
            
            # Match dates
            current_year = datetime.now().year
            date_text = match_item.find('span', {'data-frmt': '%d.%m'}).text.strip()
            datetime_str = f"{date_text}/{current_year}"
            datetime_obj = datetime.strptime(datetime_str, "%d.%m/%Y")
            formatted_datetime = datetime_obj.strftime("%d/%m/%Y")
            match_dates.append(formatted_datetime)
            
            # Match times
            time_text = match_item.find('span', {'data-frmt':'%H:%M'}).text.strip()
            if time_text:
                match_times.append(time_text)
            else:
                match_times.append(None)  
        
        
            # Extract stats for each match item
            link = match_item['href']
            url = link
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            
            # Extract score
            if soup:
                score = soup.find('div', {'class':'gamescoreon'})
                if score:
                    score = score.text
                else:
                    score = None
            else:
                score = None
                
            scores.append(score)
            
            if ' - ' in score:
                goals = list(map(int, score.split(' - ')))
        
                # Calculate the difference between the first and second goals
                difference = goals[0] - goals[1]
        
                # Determine the result based on the difference
                if difference == 0:
                    result.append('X')
                elif difference > 0:
                    result.append('1')
                else:
                    result.append('2')
            else:
                result.append('')   
            
            # Extract league
            league = soup.find('div', {'class':'leagueslink'}).text
            leagues.append(league)
        
            # Extract power rankings and team to score stats
            divs = soup.find_all('div', {'class': 'LeagueStandings mb-3 card'})
        
            power_div = divs[0]
            tr_items = power_div.find_all('tr')
            h_tr = tr_items[1]
            h_tds = h_tr.find_all('td')
            a_tr = tr_items[2]
            a_tds = a_tr.find_all('td')
        
            # Power rankings
            h_power = float(h_tds[-1].text.strip())
            a_power = float(a_tds[-1].text.strip())
        
            home_power.append(h_power)
            away_power.append(a_power)
        
            # Both teams to score
            h_btts = int(h_tds[-2].text.strip().replace('%', ''))
            a_btts = int(a_tds[-2].text.strip().replace('%', ''))
        
            home_btts.append(h_btts)
            away_btts.append(a_btts)
            
        
            # Match details
        
            # Odds
            odds = soup.find_all('div', {'class': 'oddgame text-center'})
            h_odd  = odds[0].text.strip()
            x_odd = odds[1].text.strip()
            a_odd = odds[2].text.strip()
        
            home_odds.append(h_odd)
            draw_odds.append(x_odd)
            away_odds.append(a_odd)
        
            # Game average stats
            game_stats = soup.find_all('div', {'class': 'card mb-4 detailscard'})
            game_div = game_stats[-1]
            trs = game_div.find_all('tr')
        
            for index, tr in enumerate(trs):
                
                # Over 1.5
                if index == 2:
                    tds = tr.find_all('td')
                    h1_5 = safe_int_conversion(tds[0].text.strip().replace('%', ''))
                    if h1_5 is None:
                        h1_5 = None
                        
                    a1_5 = safe_int_conversion(tds[1].text.strip().replace('%', ''))
                    if a1_5 is None:
                        a1_5 = None
                    
                    home1_5.append(h1_5)
                    away1_5.append(a1_5)
                        
                # Over 2.5    
                elif index == 4:
                    tds = tr.find_all('td')
                    h2_5 = safe_int_conversion(tds[0].text.strip().replace('%', ''))
                    if h2_5 is None:
                        h2_5 = None
                    
                    a2_5 = safe_int_conversion(tds[1].text.strip().replace('%', ''))
                    if a2_5 is None:
                        a2_5 = None
                    
                    home2_5.append(h2_5)
                    away2_5.append(a2_5)
                        
                # Over 3.5       
                elif index == 6:
                    tds = tr.find_all('td')
                    h3_5 = safe_int_conversion(tds[0].text.strip().replace('%', ''))
                    if h3_5 is None:
                        h3_5 = None
                        
                    a3_5 = safe_int_conversion(tds[1].text.strip().replace('%', ''))
                    if a3_5 is None:
                        a3_5 = None
                    
                    home3_5.append(h3_5)
                    away3_5.append(a3_5) 
                    
                # Average Scored        
                elif index == 8:
                    tds = tr.find_all('td')
                    h_avg = safe_float_conversion(tds[0].text.strip())
                    if h_avg is None:
                        h_avg = None
                        
                    a_avg = safe_float_conversion(tds[1].text.strip())
                    if a_avg is  None:
                        a_avg = None
        
                    havg_scored.append(h_avg)
                    aavg_scored.append(a_avg)
                    
                # Average Conceded
                elif index == 10:
                    tds = tr.find_all('td')
                    h_conceded = safe_float_conversion(tds[0].text.strip())
                    if h_conceded is None:
                        h_conceded = None
                        
                    a_conceded = safe_float_conversion(tds[1].text.strip())
                    if a_conceded is None:
                        a_conceded = None
                    
                    h_avgconceded.append(h_conceded)
                    a_avgconceded.append(a_conceded)    
                    
            # Extracting stats from the league standings
            table_divs = soup.find_all('div', {'class':'table-responsive'})
            table_div = table_divs[-1]
        
            # home team stats
            home_tr = table_div.find('tr', {'class':'home'})
        
            if home_tr:
                h_rank = int(home_tr.find('span', {'class':'rank-number'}).text.strip())
                
                home_stats = home_tr.find_all('div', {'class':'data-wrapper'})
                h_pt = int(home_stats[-1].text) 
                h_gdtext = home_stats[-2].text.strip()
                h_gf, h_ga, h_gd = gd_calc(h_gdtext)
                
                home_rank.append(h_rank)
                home_pts.append(h_pt)
                home_gd.append(h_gd)
            else:
                home_rank.append(None)
                home_pts.append(None)
                home_gd.append(None)
        
            # away team stats
            away_tr = table_div.find('tr', {'class':'away'})
            if away_tr:
                a_rank = int(away_tr.find('span', {'class':'rank-number'}).text.strip())
                
                away_stats = away_tr.find_all('div', {'class':'data-wrapper'})
                a_pt = int(away_stats[-1].text) if away_stats[-1].text.strip() else None
                a_gdtext = away_stats[-2].text.strip()
                a_gf, a_ga, a_gd = gd_calc(a_gdtext)
                
                away_rank.append(a_rank)
                away_pts.append(a_pt)
                away_gd.append(a_gd)
            else:
                away_rank.append(None)
                away_pts.append(None)
                away_gd.append(None)
            
        
        data = {
            'Home Team': home_teams,
            'Away Team': away_teams,
            'Match Dates': match_dates,
            'Match Time': match_times,
            'Score': scores,
            'Result': result,
            'League': leagues,
            'Home Position': home_rank,
            'Away Position': away_rank,
            'Home GD': home_gd,
            'Pick': picks,
            '1': home_odds,
            'X': draw_odds,
            '2': away_odds,
            'Home Form': home_form,
            'Away Form': away_form,
            'H1.5': home1_5,
            'A1.5': away1_5,
            'H2.5': home2_5,
            'A2.5': away2_5,
            'HomeBTTS': home_btts,
            'AwayBTTS': away_btts,
            'HomePower': home_power,
            'AwayPower': away_power,
            }
        
        day_df = pd.DataFrame(data)
        time.sleep(3)
        
        # Append to the all_data DataFrame
        all_data = pd.concat([all_data, day_df], ignore_index=True)
    
    # Drop duplicate rows & replace empty strings with NaN values
    all_data.drop_duplicates(inplace=True)
    all_data.replace('', np.nan, inplace=True)
    
    
    # Combine 'Match Date' and 'Match Time' columns into one column
    all_data['Match Date'] = all_data.apply(lambda row: parse_date(row['Match Dates'], row['Match Time']), axis=1) + pd.DateOffset(hours=2)
    
    # Drop 'Match Dates' and 'Match Time' columns
    all_data.drop(['Match Dates', 'Match Time'], axis=1, inplace=True)
    
    # Sort the DataFrame by 'Match Date' and reset the index
    all_data.sort_values('Match Date', inplace=True)
    all_data.reset_index(drop=True, inplace=True)
    
    return all_data

