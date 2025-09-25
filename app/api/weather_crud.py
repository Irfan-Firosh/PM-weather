from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import json

from app.db.session import SessionLocal
from app.db import crud
from app.schemas.weather_crud import (
    WeatherRecordCreate, 
    WeatherRecordUpdate, 
    WeatherRecordResponse,
    WeatherRecordListResponse,
    WeatherDataRequest,
    WeatherDataResponse
)
from app.services.weather import WeatherService

router = APIRouter(prefix="/weather-data", tags=["weather-data"])
weather_service = WeatherService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", response_model=WeatherRecordResponse)
async def create_weather_record(
    request: WeatherDataRequest,
    db: Session = Depends(get_db)
):
    try:
        coordinates = await weather_service.get_coordinates_from_location(request.location)
        lat, lon = coordinates
        
        location_data = {
            "name": request.location,
            "latitude": str(lat),
            "longitude": str(lon)
        }
        
        existing_location = crud.get_location_by_name(db, request.location)
        if existing_location:
            location_id = existing_location.id
        else:
            location = crud.create_location(db, location_data)
            location_id = location.id
        
        weather_data = await weather_service.get_weather_summary(request.location)
        
        record_data = {
            "location_id": location_id,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "weather_data": weather_data
        }
        
        record = crud.create_weather_record(db, record_data)
        db_record = db.query(crud.WeatherRecord).filter(crud.WeatherRecord.id == record.id).first()
        
        return WeatherRecordResponse.from_orm(db_record)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[WeatherRecordListResponse])
async def get_all_weather_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    records = db.query(crud.WeatherRecord).offset(skip).limit(limit).all()
    return [WeatherRecordListResponse.from_orm(record) for record in records]

@router.get("/{record_id}", response_model=WeatherRecordResponse)
async def get_weather_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = crud.get_weather_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return WeatherRecordResponse.from_orm(record)

@router.get("/location/{location_id}", response_model=List[WeatherRecordListResponse])
async def get_weather_records_by_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    records = crud.get_weather_records_by_location(db, location_id)
    return [WeatherRecordListResponse.from_orm(record) for record in records]

@router.put("/{record_id}", response_model=WeatherRecordResponse)
async def update_weather_record(
    record_id: int,
    update_data: WeatherRecordUpdate,
    db: Session = Depends(get_db)
):
    existing_record = crud.get_weather_record(db, record_id)
    if not existing_record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    
    if update_dict.get('location'):
        try:
            coordinates = await weather_service.get_coordinates_from_location(update_dict['location'])
            lat, lon = coordinates
            
            location_data = {
                "name": update_dict['location'],
                "latitude": str(lat),
                "longitude": str(lon)
            }
            
            existing_location = crud.get_location_by_name(db, update_dict['location'])
            if existing_location:
                location_id = existing_location.id
            else:
                location = crud.create_location(db, location_data)
                location_id = location.id
            
            update_dict['location_id'] = location_id
            del update_dict['location']
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid location: {str(e)}")
    
    if update_dict.get('weather_data') is None and (update_dict.get('location_id') or update_dict.get('start_date') or update_dict.get('end_date')):
        try:
            location_name = existing_record.location.name
            if update_dict.get('location_id'):
                new_location = crud.get_location(db, update_dict['location_id'])
                if new_location:
                    location_name = new_location.name
            
            start_date = update_dict.get('start_date', existing_record.start_date)
            end_date = update_dict.get('end_date', existing_record.end_date)
            
            weather_data = await weather_service.get_weather_summary(location_name)
            update_dict['weather_data'] = weather_data
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch updated weather data: {str(e)}")
    
    updated_record = crud.update_weather_record(db, record_id, update_dict)
    if not updated_record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    
    return WeatherRecordResponse.from_orm(updated_record)

@router.delete("/{record_id}")
async def delete_weather_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    record = crud.delete_weather_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    return {"message": "Weather record deleted successfully", "deleted_id": record_id}

@router.get("/search/location", response_model=List[WeatherRecordListResponse])
async def search_weather_records_by_location_name(
    location_name: str = Query(..., description="Location name to search for"),
    db: Session = Depends(get_db)
):
    locations = db.query(crud.Location).filter(crud.Location.name.ilike(f"%{location_name}%")).all()
    if not locations:
        raise HTTPException(status_code=404, detail="No locations found matching the search criteria")
    
    all_records = []
    for location in locations:
        records = crud.get_weather_records_by_location(db, location.id)
        all_records.extend(records)
    
    return [WeatherRecordListResponse.from_orm(record) for record in all_records]

@router.get("/search/date-range", response_model=List[WeatherRecordListResponse])
async def search_weather_records_by_date_range(
    start_date: date = Query(..., description="Start date for search"),
    end_date: date = Query(..., description="End date for search"),
    db: Session = Depends(get_db)
):
    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    records = db.query(crud.WeatherRecord).filter(
        crud.WeatherRecord.start_date <= end_date,
        crud.WeatherRecord.end_date >= start_date
    ).all()
    
    return [WeatherRecordListResponse.from_orm(record) for record in records]
