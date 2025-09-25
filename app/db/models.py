from sqlalchemy import Column, Integer, String, JSON, DateTime, Date, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    weather_records = relationship("WeatherRecord", back_populates="location")

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    weather_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    location = relationship("Location", back_populates="weather_records")
