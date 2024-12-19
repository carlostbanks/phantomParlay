from typing import List, Dict
from ..models.bet import Bet, BetAnalysis
from ..services.nfl_client import NFLClient

class BetAnalyzer:
    def __init__(self):
        self.WEIGHTS = {
            'RECENT_FORM': 0.60,    # Last 5 games
            'HEAD_TO_HEAD': 0.40,   # Last season matchups
        }
        self.nfl_client = NFLClient()  # Create instance

    async def analyze_bet(self, bet: Bet) -> BetAnalysis:
        """Analyze a single bet to calculate confidence score and factors."""
        try:
            # Get team IDs using the updated get_team_id method
            team_id = await self.nfl_client.get_team_id(bet.team)
            opponent_id = await self.nfl_client.get_team_id(bet.opponent)

            # Fetch recent form and head-to-head data
            recent_games = await self.nfl_client.get_last_5_games(team_id)
            h2h_games = await self.nfl_client.get_h2h_last_season(team_id, opponent_id)

            # Calculate scores
            recent_form_score = self.calculate_win_percentage(recent_games, team_id)
            h2h_score = self.calculate_win_percentage(h2h_games, team_id)

            # Calculate weighted final score
            final_score = (
                recent_form_score * self.WEIGHTS['RECENT_FORM'] +
                h2h_score * self.WEIGHTS['HEAD_TO_HEAD']
            )

            # Generate analysis factors
            factors = self._generate_factors(recent_form_score, h2h_score, bet.opponent)

            return BetAnalysis(
                confidence_score=round(final_score),
                factors=factors,
                recommendation=self._get_recommendation(final_score)
            )

        except Exception as e:
            print(f"Error analyzing bet: {str(e)}")
            return self._basic_analysis(bet)


    def calculate_win_percentage(self, games: Dict, team_id: str) -> float:
        """Calculate win percentage for a given set of games and team ID."""
        if not games or "data" not in games:
            return 0.0

        wins = 0
        for game in games["data"]:
            if (
                (game["home_team"]["id"] == team_id and game["home_team_score"] > game["visitor_team_score"]) or
                (game["visitor_team"]["id"] == team_id and game["visitor_team_score"] > game["home_team_score"])
            ):
                wins += 1

        return (wins / len(games["data"])) * 100 if games["data"] else 0.0

    def _generate_factors(self, recent_form_score: float, h2h_score: float, opponent: str) -> List[str]:
        """Generate factors explaining the confidence score."""
        factors = []

        # Recent form factor
        recent_wins = int(recent_form_score * 5 / 100)  # Approximate wins out of 5
        factors.append(f"Won {recent_wins} of last 5 games")

        # Head-to-head factor
        if h2h_score > 50:
            factors.append(f"Won {int(h2h_score)}% vs {opponent} last season")
        elif h2h_score < 50:
            factors.append(f"Struggled vs {opponent} last season")

        return factors

    def _get_recommendation(self, score: float) -> str:
        """Provide a recommendation based on the confidence score."""
        if score >= 75:
            return "STRONG"
        elif score >= 50:
            return "POSSIBLE"
        return "SKIP"

    def _basic_analysis(self, bet: Bet) -> BetAnalysis:
        """Fallback analysis when API fails."""
        return BetAnalysis(
            confidence_score=50,
            factors=["Basic odds analysis only", "Unable to fetch detailed stats"],
            recommendation="POSSIBLE"
        )

    def calculate_overall_confidence(self, analyses: List[BetAnalysis]) -> int:
        """Calculate overall confidence score for a parlay based on individual analyses."""
        scores = [analysis.confidence_score for analysis in analyses]
        return round(sum(scores) / len(scores)) if scores else 0

    def should_suggest_solana(self, overall_score: int) -> bool:
        """Determine whether to suggest Solana purchase based on overall score."""
        return overall_score < 72
