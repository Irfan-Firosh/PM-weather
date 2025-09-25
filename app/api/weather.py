from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List, Dict
from app.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])
weather_service = WeatherService()

@router.get("/current")
async def get_current_weather(
    location: str = Query(..., description="Location (city, zip code, coordinates, or landmark)")
):
    try:
        weather_data = await weather_service.get_current_weather(location)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/forecast")
async def get_5day_forecast(
    location: str = Query(..., description="Location (city, zip code, coordinates, or landmark)")
):
    try:
        forecast_data = await weather_service.get_5day_forecast(location)
        return {"forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary")
async def get_weather_summary(
    location: str = Query(..., description="Location (city, zip code, coordinates, or landmark)")
):
    try:
        summary_data = await weather_service.get_weather_summary(location)
        return summary_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/validate")
async def validate_location(
    location: str = Query(..., description="Location to validate")
):
    try:
        validation_result = weather_service.validate_location_input(location)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))