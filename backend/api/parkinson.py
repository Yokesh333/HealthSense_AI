"""
backend/api/parkinson.py

FastAPI router for Parkinson's Disease ML Prediction endpoint.

Route: POST /api/parkinson/predict
"""

import logging
from fastapi import APIRouter, Request, HTTPException
from backend.models.parkinson_schemas import (
    ParkinsonPredictionRequest,
    ParkinsonPredictionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=ParkinsonPredictionResponse)
async def predict_parkinson(request: Request, data: ParkinsonPredictionRequest):
    try:
        predictor = request.app.state.parkinson_predictor
    except AttributeError:
        logger.error("parkinson/predict: ParkinsonPredictor is not loaded in app.state.")
        raise HTTPException(status_code=503, detail="Parkinson Predictor is not available.")

    if predictor is None:
        raise HTTPException(status_code=503, detail="Parkinson Predictor failed to initialize.")

    try:
        result = predictor.predict(data.model_dump())
        return result
    except Exception as e:
        logger.error("parkinson/predict failed — %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail=f"Parkinson prediction failed: {str(e)}")
