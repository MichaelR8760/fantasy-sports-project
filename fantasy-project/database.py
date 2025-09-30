import sqlite3
import os

def create_database(db_path="fantasy_data.db"):
    """Create the database and tables"""
    try:
        print(f"Creating database at: {os.path.abspath(db_path)}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create players table (from ESPN lookup)
        print("Creating players table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                team_jersey TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT,
                team TEXT,
                jersey TEXT,
                espn_id TEXT,
                height TEXT,
                weight TEXT,
                age INTEGER
            )
        ''')
        
        # Create weekly_data table (from RotoWire scraping)
        print("Creating weekly_data table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                team_jersey TEXT NOT NULL,
                salary REAL,
                projected_fpts REAL,
                actual_fpts REAL,
                value_score REAL,
                ownership_pct REAL,
                opponent TEXT,
                FOREIGN KEY (team_jersey) REFERENCES players (team_jersey)
            )
        ''')
        
        # Create player_stats table (for actual weekly performance)
        print("Creating player_stats table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                week INTEGER,
                team_jersey TEXT NOT NULL,
                completions INTEGER DEFAULT 0,
                passing_attempts INTEGER DEFAULT 0,
                passing_yards INTEGER DEFAULT 0,
                passing_touchdowns INTEGER DEFAULT 0,
                interceptions INTEGER DEFAULT 0,
                rushing_attempts INTEGER DEFAULT 0,
                rushing_yards INTEGER DEFAULT 0,
                rushing_touchdowns INTEGER DEFAULT 0,
                receptions INTEGER DEFAULT 0,
                receiving_targets INTEGER DEFAULT 0,
                receiving_yards INTEGER DEFAULT 0,
                receiving_touchdowns INTEGER DEFAULT 0,
                FOREIGN KEY (team_jersey) REFERENCES players (team_jersey)
            )
        ''')
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables created: {[table[0] for table in tables]}")
        
        conn.commit()
        conn.close()
        print(f"Database successfully created: {db_path}")
        
    except Exception as e:
        print(f"Error creating database: {e}")

def insert_players(player_lookup, db_path="fantasy_data.db"):
    """Insert player data from lookup table"""
    conn = sqlite3.connect(db_path)
    
    data = []
    for key, player in player_lookup.items():
        data.append((
            key,  # team_jersey
            player['name'],
            player['position'],
            player['team'],
            player['jersey'],
            player['espn_id'],
            player['height'],
            player['weight'],
            player.get('age')
        ))
    
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR REPLACE INTO players 
        (team_jersey, name, position, team, jersey, espn_id, height, weight, age)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    
    conn.commit()
    conn.close()
    print(f"Inserted {len(data)} players into database")
        
if __name__ == "__main__":
    create_database()

    # Load and insert player data
    from player_lookup import load_player_lookup
    players = load_player_lookup()
    if players:
        insert_players(players)
    else:
        print("No player data found. Run player_lookup.py first.")

