from PIL import Image
import pytesseract
import io
from typing import List, Dict
from base64 import b64encode

class ImageProcessor:
    @staticmethod
    async def process_bet_image(image_bytes: bytes) -> List[Dict]:
        try:
            # Convert bytes to image using PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Extract text from image using pytesseract
            text = pytesseract.image_to_string(image)
            print("Extracted text from image:", text)  # Debug print
            
            # Parse the text into bets
            bets = ImageProcessor._parse_bet_text(text)
            return bets
            
        except Exception as e:
            print(f"Error in process_bet_image: {str(e)}")
            raise e

    @staticmethod
    def _parse_bet_text(text: str) -> List[Dict]:
        lines = text.split('\n')
        bets = []
        matchups = []
        odds_list = []
        picked_teams = []
        total_parlay_odds = None
        
        # First collect the teams that were picked (marked with ©)
        for line in lines:
            if '©' in line:
                team = line.replace('©', '').strip()
                picked_teams.append(team)
        
        # Then collect matchups and their corresponding odds
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            print(f"Processing line: {line}")
            
            # Collect matchup lines
            if '@' in line and 'Payout' not in line:
                matchups.append(line)
                
            # Collect odds
            if (line.startswith('+') or line.startswith('-')):
                try:
                    odds = int(''.join(filter(lambda x: x.isdigit() or x in '+-', line)))
                    if total_parlay_odds is None:
                        total_parlay_odds = odds  # Store total parlay odds
                        print(f"Total parlay odds: {odds}")
                        continue
                    odds_list.append(odds)
                except ValueError:
                    continue

        print(f"Found picked teams: {picked_teams}")
        print(f"Found matchups: {matchups}")
        print(f"Found individual odds: {odds_list}")
        print(f"Total parlay odds: {total_parlay_odds}")

        # Now pair them up
        parlay_info = {
            "total_odds": total_parlay_odds,
            "individual_bets": []
        }

        for i, matchup in enumerate(matchups):
            if i < len(odds_list):
                away, home = matchup.split('@')
                away = away.strip()
                home = home.strip()
                
                picked_team = picked_teams[i]
                is_home_pick = picked_team == home
                
                parlay_info["individual_bets"].append({
                    "team": picked_team,
                    "opponent": away if is_home_pick else home,
                    "bet_type": "moneyline",
                    "odds": odds_list[i],
                    "details": {}
                })

        print("Final parsed parlay:", parlay_info)
        return parlay_info