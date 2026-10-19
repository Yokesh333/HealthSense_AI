from fastapi import APIRouter, Request, HTTPException
from backend.models.adni_schemas import ADNIPredictionRequest, ADNIPredictionResponse

router = APIRouter()

@router.post("/predict", response_model=ADNIPredictionResponse)
async def predict_adni(request: Request, data: ADNIPredictionRequest):
    try:
        predictor = request.app.state.adni_predictor
    except AttributeError:
        raise HTTPException(status_code=500, detail="ADNI Predictor is not loaded in application state.")
        
    try:
        # Pass data as dict
        prediction_result = predictor.predict(data.model_dump())
        return prediction_result
    except Exception as e:
        # Don't expose internal stack traces, just the error message
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")
