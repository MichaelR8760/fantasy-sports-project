import requests
import json
import time
from config import ROTOWIRE_TO_ESPN_TEAM_IDS

def build_player_lookup():
    """
    Fetch all NFL player data from ESPN API and create lookup table
    Returns dictionary with team_jersey as key and player info as value
    """
    player_lookup = {}
    failed_teams = []
    
    print("Fetching player data from ESPN API...")
    
    for team_abbrev, espn_team_id in ROTOWIRE_TO_ESPN_TEAM_IDS.items():
        try:
            print(f"Fetching {team_abbrev} roster...")
            
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{espn_team_id}/roster"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract player data - ESPN groups by position
            for position_group in data.get('athletes', []):
                # The actual players are in the 'items' array
                for athlete in position_group.get('items', []):
                    name = athlete.get('displayName', '')
                    jersey = athlete.get('jersey', None)
                    
                    # Skip if no jersey number
                    if not jersey:
                        continue
                    
                    # Get position from the athlete's individual data
                    athlete_position = athlete.get('position', {})
                    if isinstance(athlete_position, dict):
                        position_name = athlete_position.get('abbreviation', 'UNKNOWN')
                    else:
                        position_name = str(athlete_position)
                    
                    # Create unique key: TEAM_JERSEY
                    key = f"{team_abbrev}_{jersey}"
                    
                    player_lookup[key] = {
                        'name': name,
                        'position': position_name,
                        'team': team_abbrev,
                        'jersey': str(jersey),
                        'espn_id': athlete.get('id', ''),
                        'height': athlete.get('displayHeight', ''),
                        'weight': athlete.get('displayWeight', ''),
                        'age': athlete.get('age', '')
                    }
            
            # Small delay to be respectful to ESPN's servers
            time.sleep(0.1)
            
        except requests.RequestException as e:
            print(f"Failed to fetch {team_abbrev}: {e}")
            failed_teams.append(team_abbrev)
            continue
        except Exception as e:
            print(f"Error processing {team_abbrev}: {e}")
            failed_teams.append(team_abbrev)
            continue
    
    print(f"\nFetched data for {len(ROTOWIRE_TO_ESPN_TEAM_IDS) - len(failed_teams)}/32 teams")
    print(f"Total players in lookup: {len(player_lookup)}")
    
    if failed_teams:
        print(f"Failed teams: {', '.join(failed_teams)}")
    
    return player_lookup

def save_player_lookup(player_data, filename="player_lookup.json"):
    """Save player lookup data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(player_data, f, indent=2)
    print(f"Player lookup saved to {filename}")

def load_player_lookup(filename="player_lookup.json"):
    """Load player lookup data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{filename} not found. Run build_player_lookup() first.")
        return {}

def find_player_by_name(player_lookup, name, team=None):
    """
    Find player by name (fuzzy matching)
    Returns list of potential matches
    """
    matches = []
    name_lower = name.lower()
    
    for key, player in player_lookup.items():
        player_name_lower = player['name'].lower()
        
        # Exact match
        if name_lower == player_name_lower:
            matches.append((key, player, 'exact'))
        # Contains match
        elif name_lower in player_name_lower or player_name_lower in name_lower:
            # If team specified, prioritize team matches
            if team and player['team'] == team:
                matches.append((key, player, 'partial_team'))
            else:
                matches.append((key, player, 'partial'))
    
    # Sort by match quality
    match_order = {'exact': 0, 'partial_team': 1, 'partial': 2}
    matches.sort(key=lambda x: match_order.get(x[2], 3))
    
    return matches

if __name__ == "__main__":
    # Build and save player lookup
    players = build_player_lookup()
    save_player_lookup(players)
    
    # Test lookup
    print("\nSample players:")
    count = 0
    for key, player in players.items():
        if count < 5:
            print(f"{key}: {player['name']} - {player['position']}")
            count += 1
        else:
            break