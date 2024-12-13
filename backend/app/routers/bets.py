from fastapi import APIRouter, HTTPException
from typing import List
from ..models.bet import ParlayAnalysisRequest, ParlayAnalysisResponse, BetAnalysis
from ..services.analyzer import BetAnalyzer

router = APIRouter()
analyzer = BetAnalyzer()

@router.post("/analyze", response_model=ParlayAnalysisResponse)
async def analyze_parlay(request: ParlayAnalysisRequest):
    try:
        # Analyze each bet in the parlay
        individual_analyses = [
            analyzer.analyze_bet(bet) 
            for bet in request.bets
        ]
        
        # Calculate overall confidence
        overall_score = analyzer.calculate_overall_confidence(individual_analyses)
        
        # Determine if we should show Solana alternative
        show_solana = analyzer.should_suggest_solana(overall_score)
        
        return ParlayAnalysisResponse(
            overall_score=overall_score,
            individual_analyses=individual_analyses,
            should_show_solana=show_solana
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))