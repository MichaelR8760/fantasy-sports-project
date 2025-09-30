import requests

# Test with a known superstar player ID
test_url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/athletes/3139477/gamelog"  # Patrick Mahomes
response = requests.get(test_url)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("API works!")
    data = response.json()
    print(f"Keys: {list(data.keys())}")
else:
    print(f"Error: {response.text}")