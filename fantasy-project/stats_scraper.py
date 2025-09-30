import requests
import sqlite3
import json
from datetime import datetime
from player_lookup import load_player_lookup

def fetch_player_stats(espn_player_id, week=3, season=2025):
    """Fetch player stats for Week 3"""
    try:
        url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/athletes/{espn_player_id}/gamelog"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Find stats for Week 3
        events = data.get('events', [])
        for event in events:
            week_num = event.get('week', {}).get('number')
            season_year = event.get('season', {}).get('year')
            
            if week_num == week and season_year == season:
                stats = event.get('statistics', [])
                return parse_stats(stats)
        
        return None
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            # Player doesn't have game log data - this is normal
            return None
        else:
            print(f"HTTP error for player {espn_player_id}: {e}")
            return None
    except Exception as e:
        print(f"Error fetching stats for player {espn_player_id}: {e}")
        return None

def parse_stats(stats_data):
    """Parse ESPN stats data - just raw numbers"""
    parsed_stats = {
        'passing_yards': 0,
        'passing_touchdowns': 0,
        'completions': 0,
        'passing_attempts': 0,
        'interceptions': 0,
        'rushing_attempts': 0,
        'rushing_yards': 0,
        'rushing_touchdowns': 0,
        'receptions': 0,
        'receiving_yards': 0,
        'receiving_touchdowns': 0,
        'receiving_targets': 0
    }
    
    for stat_group in stats_data:
        category = stat_group.get('name', '').lower()
        stats = stat_group.get('stats', [])
        
        for stat in stats:
            name = stat.get('name', '').lower()
            value = stat.get('value', 0)
            
            if 'passing' in category:
                if 'yards' in name:
                    parsed_stats['passing_yards'] = value
                elif 'touchdown' in name:
                    parsed_stats['passing_touchdowns'] = value
                elif 'completion' in name and 'percentage' not in name:
                    parsed_stats['completions'] = value
                elif 'attempt' in name:
                    parsed_stats['passing_attempts'] = value
                elif 'interception' in name:
                    parsed_stats['interceptions'] = value
                    
            elif 'rushing' in category:
                if 'yards' in name:
                    parsed_stats['rushing_yards'] = value
                elif 'touchdown' in name:
                    parsed_stats['rushing_touchdowns'] = value
                elif 'attempt' in name:
                    parsed_stats['rushing_attempts'] = value
                    
            elif 'receiving' in category:
                if 'yards' in name:
                    parsed_stats['receiving_yards'] = value
                elif 'touchdown' in name:
                    parsed_stats['receiving_touchdowns'] = value
                elif 'reception' in name and 'yard' not in name:
                    parsed_stats['receptions'] = value
                elif 'target' in name:
                    parsed_stats['receiving_targets'] = value
    
    return parsed_stats

import time

def scrape_week3_stats():
    """Scrape Week 3 stats for all players"""
    print("Fetching Week 3 stats...")
    
    player_lookup = load_player_lookup()
    if not player_lookup:
        print("No player lookup data found. Run player_lookup.py first.")
        return
    
    conn = sqlite3.connect("fantasy_data.db")
    cursor = conn.cursor()
    
    successful_fetches = 0
    failed_fetches = 0
    
    for team_jersey, player_info in player_lookup.items():
        espn_id = player_info.get('espn_id')
        if not espn_id:
            continue
            
        # Only fetch stats for skill position players
        position = player_info.get('position', '')
        if position not in ['QB', 'RB', 'WR', 'TE']:
            continue
        
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        try:
            stats = fetch_player_stats(espn_id, week=3)
            if stats:
                # Database insertion code here
                successful_fetches += 1
                print(f"✓ {player_info['name']}")
            else:
                failed_fetches += 1
                
        except Exception as e:
            print(f"✗ Failed: {player_info['name']} - {e}")
            failed_fetches += 1
            continue

    conn.commit()
    conn.close()
    
    print(f"Successfully fetched stats for {successful_fetches} players")
    print(f"Failed to fetch stats for {failed_fetches} players")

if __name__ == "__main__":
    scrape_week3_stats()