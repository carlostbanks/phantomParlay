from pydantic import BaseModel
from typing import List, Dict

class Bet(BaseModel):
    team: str
    opponent: str
    bet_type: str
    odds: int
    details: Dict = {}

class ParlayBet(BaseModel):
    total_odds: int
    individual_bets: List[Bet]

class ParlayAnalysisRequest(BaseModel):
    parlay: ParlayBet
    wallet_address: str

class BetAnalysis(BaseModel):
    confidence_score: int
    factors: List[str]
    recommendation: str

class ParlayAnalysisResponse(BaseModel):
    overall_score: int
    individual_analyses: List[BetAnalysis]
    should_show_solana: bool