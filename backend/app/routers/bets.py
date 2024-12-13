# backend/app/routers/bets.py
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.bet import ParlayAnalysisRequest, ParlayAnalysisResponse, BetAnalysis
from ..services.analyzer import BetAnalyzer
from ..database import Database

router = APIRouter()
analyzer = BetAnalyzer()

@router.post("/analyze", response_model=ParlayAnalysisResponse)
async def analyze_parlay(request: ParlayAnalysisRequest):
    try:
        # Analyze bets
        individual_analyses = [
            analyzer.analyze_bet(bet) 
            for bet in request.bets
        ]
        
        overall_score = analyzer.calculate_overall_confidence(individual_analyses)
        show_solana = analyzer.should_suggest_solana(overall_score)
        
        # Create response
        response = ParlayAnalysisResponse(
            overall_score=overall_score,
            individual_analyses=individual_analyses,
            should_show_solana=show_solana
        )
        
        # Save to database
        await Database.save_analysis({
            "wallet_address": request.wallet_address,
            "bets": [bet.dict() for bet in request.bets],
            "overall_score": overall_score,
            "individual_analyses": [analysis.dict() for analysis in individual_analyses],
            "should_show_solana": show_solana
        })
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))