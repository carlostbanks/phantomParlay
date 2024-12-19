import httpx
from typing import Dict
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class NFLClient:
    BASE_URL = 'https://api.balldontlie.io/nfl/v1/'
    API_KEY = os.getenv("NFL_API_KEY")  # Load API key from environment

    def __init__(self):
        if not self.API_KEY:
            raise ValueError("Missing NFL_API_KEY. Ensure it's set in the environment.")
        self.headers = {
            "Authorization": self.API_KEY
        }
        self.teams = None 

    async def get_teams(self):
        """Fetch and cache all teams."""
        if self.teams is not None:  # Return cached teams if available
            return self.teams

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/teams", headers=self.headers)
                if response.status_code == 200:
                    self.teams = response.json().get("data", [])  # Cache team data
                    return self.teams
        except Exception as e:
            print(f"Error getting teams: {e}")

        self.teams = []  # Ensure self.teams is set to an empty list if fetching fails
        return self.teams

    async def get_team_id(self, team_name: str) -> int:
        """Get team ID by matching the team name, location, or full name."""
        try:
            teams = await self.get_teams()  # Fetch teams
            if not teams:
                raise ValueError("Team list is empty. Unable to fetch team data.")

            # Check against all possible name fields
            for team in teams:
                if (
                    team_name.lower() == team["name"].lower() or
                    team_name.lower() == team["location"].lower() or
                    team_name.lower() in team["full_name"].lower()
                ):
                    return team["id"]

            raise ValueError(f"Team '{team_name}' not found.")
        except Exception as e:
            print(f"Error fetching team ID for {team_name}: {e}")
            raise

    async def get_h2h_last_season(self, team1_id: int, team2_id: int) -> Dict:
        """Get head-to-head games from the last season between two teams."""
        try:
            last_season = 2023  # Replace with logic to dynamically fetch the last completed season
            params = {
                "team_ids[]": [team1_id, team2_id],
                "seasons[]": last_season,
                "per_page": 100,  # To ensure we get all relevant games
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/games",
                    params=params,
                    headers=self.headers
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error fetching H2H games: {response.status_code} - {response.text}")
                    return {"data": []}
        except Exception as e:
            print(f"Error in get_h2h_last_season: {e}")
            return {"data": []}

    async def get_last_5_games(self, team_id: str) -> Dict:
        """Get team's last 5 games"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "team_ids[]": team_id,
                    "per_page": 5,
                    "seasons[]": 2024
                }
                
                response = await client.get(
                    f"{self.BASE_URL}/games",
                    params=params,
                    headers=self.headers
                )
                
                print(f"Games response status: {response.status_code}")
                print(f"Games response body: {response.text}")
                return response.json() if response.status_code == 200 else {"data": []}
        except Exception as e:
            print(f"Error getting games: {e}")
            return {"data": []}
