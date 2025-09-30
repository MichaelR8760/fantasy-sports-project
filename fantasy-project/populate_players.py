from database import insert_players
from player_lookup import load_player_lookup

# Load player lookup data and insert into database
players = load_player_lookup()
if players:
    insert_players(players)
else:
    print("No player data found. Run player_lookup.py first.")