from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json

from app.db.session import SessionLocal
from app.db import crud
from app.services.export import ExportService

router = APIRouter(prefix="/export", tags=["export"])
export_service = ExportService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/weather-data")
async def export_weather_data(db: Session = Depends(get_db)):
    try:
        records = crud.get_weather_records(db)
        
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        
        records_data = []
        for record in records:
            record_dict = {
                "id": record.id,
                "location_id": record.location_id,
                "start_date": record.start_date.isoformat(),
                "end_date": record.end_date.isoformat(),
                "weather_data": record.weather_data,
                "created_at": record.created_at.isoformat(),
                "location": {
                    "id": record.location.id,
                    "name": record.location.name,
                    "latitude": record.location.latitude,
                    "longitude": record.location.longitude
                }
            }
            records_data.append(record_dict)
        
        export_data = export_service.export_weather_data(records_data)
        
        return json.loads(export_data.decode('utf-8'))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
