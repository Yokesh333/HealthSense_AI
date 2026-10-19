import json
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/questionnaire", tags=["Questionnaire"])

QUESTIONNAIRE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "questionnaire"

@router.get("/{type_}")
async def get_questionnaire(type_: str) -> Dict[str, Any]:
    """
    Fetch a versioned questionnaire.
    Valid types: 'alzheimers', 'parkinsons', 'both'.
    'both' returns a combination of both questionnaires.
    """
    if type_ not in ("alzheimers", "parkinsons", "both"):
        raise HTTPException(status_code=400, detail="Invalid questionnaire type")
        
    def _load_json(filename: str) -> Dict[str, Any]:
        filepath = QUESTIONNAIRE_DIR / filename
        if not filepath.exists():
            raise HTTPException(status_code=404, detail=f"Questionnaire {filename} not found")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
            
    if type_ == "alzheimers":
        return _load_json("alzheimers_questions.json")
        
    elif type_ == "parkinsons":
        return _load_json("parkinsons_questions.json")
        
    elif type_ == "both":
        alz = _load_json("alzheimers_questions.json")
        pd = _load_json("parkinsons_questions.json")
        
        return {
            "questionnaire_id": "BOTH_SCREENING",
            "version": f"ALZ-{alz['version']}_PD-{pd['version']}",
            "alzheimers_questions": alz["questions"],
            "parkinsons_questions": pd["questions"],
            "total_questions": len(alz["questions"]) + len(pd["questions"])
        }
