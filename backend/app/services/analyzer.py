from typing import List, Dict
from ..models.bet import Bet, BetAnalysis

class BetAnalyzer:
    def analyze_bet(self, bet: Bet) -> BetAnalysis:
        # This is where we'll implement our confidence scoring algorithm
        score = self._calculate_confidence_score(bet)
        
        return BetAnalysis(
            confidence_score=score,
            factors=self._get_analysis_factors(bet),
            recommendation="PASS" if score < 50 else "POSSIBLE"
        )
    
    def _calculate_confidence_score(self, bet: Bet) -> int:
        # Mock scoring for now - we'll implement real logic later
        base_score = 50
        
        # Example factors we'll consider:
        # - Team's recent performance
        # - Head-to-head record
        # - Injuries
        # - Home/Away status
        # - Rest days
        
        return base_score
    
    def _get_analysis_factors(self, bet: Bet) -> List[str]:
        # Mock factors for now
        return [
            "Team's recent performance",
            "Key player status",
            "Head-to-head record"
        ]

    def calculate_overall_confidence(self, analyses: List[BetAnalysis]) -> int:
        # For parlays, we multiply probabilities
        # This naturally makes parlays riskier as more legs are added
        scores = [analysis.confidence_score for analysis in analyses]
        overall = 100
        for score in scores:
            overall *= (score/100)
        
        return round(overall)

    def should_suggest_solana(self, overall_score: int) -> bool:
        # If confidence is less than 72%, suggest Solana
        return overall_score < 72