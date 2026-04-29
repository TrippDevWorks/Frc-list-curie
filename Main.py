import requests
import time
import csv
import os

APIKEY = "your tba key"  # regenerate yours
EVENT = "event key here" # ex: 2026cur
YEAR = 2026 # set to ur season year ( for epa )
DELAY = 0.7 
save = True

HEADERKEY = {
    "X-TBA-Auth-Key": APIKEY
}

def get(url, headers=None, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[Retry {attempt+1}] {e}")
            time.sleep((attempt + 1) * 1.5)
    return None

def get_teams():
    url = f"https://www.thebluealliance.com/api/v3/event/{EVENT}/teams"
    response = get(url, headers=HEADERKEY)
    return response.json() if response else []

def get_epa(team_number):
    url = f"https://api.statbotics.io/v3/team_year/{team_number}/{YEAR}"
    response = get(url)
    if not response:
        return None
    data = response.json()
    return data.get("epa", {}).get("total_points", {}).get("mean")

def main():
    print(f"Getting teams for event key {EVENT}...")
    teams = get_teams()
    results = []

    for team in teams:
        team_number = team.get("team_number")
        nickname = team.get("nickname")
        city = team.get("city")
        state = team.get("state_prov")
        country = team.get("country")
        location = ", ".join(filter(None, [city, state, country]))
        print(f"Getting epa for {team_number}...")
        epa = get_epa(team_number)
        results.append({
            "team_number": team_number,
            "team_name": nickname,
            "location": location,
            "season_epa": epa
        })
        time.sleep(DELAY)
        
    results.sort(key=lambda x: (x["season_epa"] is None, x["season_epa"]), reverse=True)
    for team in results:
        print(team)

    if save and results:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, f"{EVENT}_Teams.csv")
    
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            print(f"\nSaved to {path}")
        except PermissionError:
            print("Could not save file due to permissions.")
            
if __name__ == "__main__":
    main()
