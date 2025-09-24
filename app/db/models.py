from sqlalchemy import Column, Integer, String, JSON, DateTime, Date, func
from app.db.base import Base

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    weather_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())