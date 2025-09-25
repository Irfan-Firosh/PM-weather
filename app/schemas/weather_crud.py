from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class WeatherRecordCreate(BaseModel):
    location: str
    start_date: date
    end_date: date
    
    
    @model_validator(mode='after')
    def end_date_must_be_after_start_date(self):
        if self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        return self

class WeatherRecordUpdate(BaseModel):
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    weather_data: Optional[Dict[str, Any]] = None
    
    @model_validator(mode='after')
    def end_date_must_be_after_start_date(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        return self

class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: Optional[str]
    longitude: Optional[str]
    
    class Config:
        from_attributes = True

class WeatherRecordResponse(BaseModel):
    id: int
    location_id: int
    start_date: date
    end_date: date
    weather_data: Optional[Dict[str, Any]]
    created_at: datetime
    location: LocationResponse
    
    class Config:
        from_attributes = True

class WeatherRecordListResponse(BaseModel):
    id: int
    location_id: int
    start_date: date
    end_date: date
    weather_data: Optional[Dict[str, Any]]
    created_at: datetime
    location: LocationResponse
    
    class Config:
        from_attributes = True

class WeatherDataRequest(BaseModel):
    location: str
    start_date: date
    end_date: date
    
    @field_validator('start_date')
    def start_date_must_be_future_or_today(cls, v):
        if v < date.today():
            raise ValueError('Start date cannot be in the past')
        return v
    
    @model_validator(mode='after')
    def end_date_must_be_after_start_date(self):
        if self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        return self

class WeatherDataResponse(BaseModel):
    location: str
    start_date: date
    end_date: date
    weather_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True
