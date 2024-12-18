from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from typing import List
from ..models.bet import (
    ParlayAnalysisRequest, 
    ParlayAnalysisResponse, 
    BetAnalysis,
    ParlayBet  # Add this import
)
from ..services.analyzer import BetAnalyzer
from ..services.image_processor import ImageProcessor  # Add this
from ..database import Database

router = APIRouter()
analyzer = BetAnalyzer()

@router.post("/analyze-image")
async def analyze_bet_image(
    image: UploadFile = File(...),
    wallet_address: str = Form(...)
):
    try:
        print(f"Received image: {image.filename}, type: {image.content_type}")
        contents = await image.read()
        parsed_parlay = await ImageProcessor.process_bet_image(contents)
        
        # Convert to our request format
        request = ParlayAnalysisRequest(
            parlay=ParlayBet(**parsed_parlay),
            wallet_address=wallet_address
        )
        
        return await analyze_parlay(request)
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=ParlayAnalysisResponse)
async def analyze_parlay(request: ParlayAnalysisRequest):
    try:
        # Analyze each bet in the parlay
        individual_analyses = [
            analyzer.analyze_bet(bet) 
            for bet in request.parlay.individual_bets
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
            "total_odds": request.parlay.total_odds,
            "bets": [bet.dict() for bet in request.parlay.individual_bets],
            "overall_score": overall_score,
            "individual_analyses": [analysis.dict() for analysis in individual_analyses],
            "should_show_solana": show_solana
        })
        
        return response
    
    except Exception as e:
        print(f"Error in analyze_parlay: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))