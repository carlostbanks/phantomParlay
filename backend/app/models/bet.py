from pydantic import BaseModel
from typing import List

class Bet(BaseModel):
    team: str
    bet_type: str  # ML, spread, over/under
    odds: float
    details: dict  # Additional details like spread value, etc.

class ParlayAnalysisRequest(BaseModel):
    bets: List[Bet]
    wallet_address: str

class BetAnalysis(BaseModel):
    confidence_score: int
    factors: List[str]
    recommendation: str

class ParlayAnalysisResponse(BaseModel):
    overall_score: int
    individual_analyses: List[BetAnalysis]
    should_show_solana: bool  # True if overall confidence is low