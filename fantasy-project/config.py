
# RotoWire URL for DraftKings lineup builder
ROTOWIRE_URL = "https://www.rotowire.com/daily/nfl/optimizer.php"

# CSV output settings
CSV_FILENAME = "rotowire_data_{date}.csv"
CSV_COLUMNS = [
    "Player",
    "Injury_Status", 
    "Position",
    "Team",
    "Opponent", 
    "Salary",
    "FPTS",
    "Value",
    "Roster_Percent"
]

ROTOWIRE_TO_ESPN_TEAM_IDS = {
    'ARI': 22,   # Cardinals
    'ATL': 1,    # Falcons
    'BAL': 33,   # Ravens
    'BUF': 2,    # Bills
    'CAR': 29,   # Panthers
    'CHI': 3,    # Bears
    'CIN': 4,    # Bengals
    'CLE': 5,    # Browns
    'DAL': 6,    # Cowboys
    'DEN': 7,    # Broncos
    'DET': 8,    # Lions
    'GB': 9,     # Packers
    'HOU': 34,   # Texans
    'IND': 11,   # Colts
    'JAX': 30,   # Jaguars
    'KC': 12,    # Chiefs
    'LAC': 24,   # Chargers
    'LAR': 14,   # Rams
    'LV': 13,    # Raiders
    'MIA': 15,   # Dolphins
    'MIN': 16,   # Vikings
    'NE': 17,    # Patriots
    'NO': 18,    # Saints
    'NYG': 19,   # Giants
    'NYJ': 20,   # Jets
    'PHI': 21,   # Eagles
    'PIT': 23,   # Steelers
    'SF': 25,    # 49ers
    'SEA': 26,   # Seahawks
    'TB': 27,    # Buccaneers
    'TEN': 10,   # Titans
    'WAS': 28    # Commanders
}