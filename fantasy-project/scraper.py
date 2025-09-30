import requests
import sqlite3
from datetime import datetime
from player_lookup import load_player_lookup, find_player_by_name

def scrape_rotowire_api(slate_id=8602):
    """Scrape RotoWire data directly from their API"""
    
    # Load player lookup
    player_lookup = load_player_lookup()
    if not player_lookup:
        print("No player lookup data found. Run player_lookup.py first.")
        return [], []
    
    print("Fetching data from RotoWire API...")
    
    # Hit the API endpoint directly
    api_url = f"https://www.rotowire.com/daily/nfl/api/players.php?slateID={slate_id}"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"Found {len(data)} players in API response")
        
        matched_players = []
        unmatched_players = []
        
        for player_data in data:
            # Extract player info from JSON
            player_name = f"{player_data['firstName']} {player_data['lastName']}"
            position = player_data['rotoPos']
            team = player_data['team']['abbr']
            opponent = player_data['opponent']['team']
            salary = player_data['salary']
            projected_pts = player_data['pts']
            ownership = player_data['rostership']
            injury_status = player_data.get('injuryStatus', '')
            
            # Try to match player to lookup data
            matches = find_player_by_name(player_lookup, player_name, team)
            
            if matches:
                # Use the best match
                team_jersey, player_info, match_type = matches[0]
                matched_players.append({
                    'team_jersey': team_jersey,
                    'rotowire_name': player_name,
                    'lookup_name': player_info['name'],
                    'match_type': match_type,
                    'position': position,
                    'team': team,
                    'opponent': opponent,
                    'salary': salary,
                    'fpts': projected_pts,
                    'value': salary / float(projected_pts) if float(projected_pts) > 0 else 0,  # Calculate value
                    'roster_pct': ownership,
                    'injury_status': injury_status or ""
                })
            else:
                unmatched_players.append({
                    'name': player_name,
                    'team': team,
                    'position': position
                })
        
        print(f"Matched: {len(matched_players)} players")
        print(f"Unmatched: {len(unmatched_players)} players")
        
        if unmatched_players:
            print("Unmatched players:")
            for player in unmatched_players[:5]:  # Show first 5
                print(f"  {player['name']} ({player['team']} {player['position']})")
        
        # Store in database
        if matched_players:
            store_weekly_data(matched_players)
        
        return matched_players, unmatched_players
        
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}")
        return [], []
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return [], []

def store_weekly_data(players_data):
    """Store weekly data in database"""
    conn = sqlite3.connect("fantasy_data.db")
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    for player in players_data:
        cursor.execute('''
            INSERT INTO weekly_data 
            (date, team_jersey, salary, projected_fpts, value_score, ownership_pct, opponent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            today,
            player['team_jersey'],
            float(player['salary']),
            float(player['fpts']),
            float(player['value']),
            float(player['roster_pct']),
            player['opponent']
        ))
    
    conn.commit()
    conn.close()
    print(f"Stored {len(players_data)} players in database")

if __name__ == "__main__":
    matched, unmatched = scrape_rotowire_api()