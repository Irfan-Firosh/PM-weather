from app.db.models import WeatherRecord, Location
from sqlalchemy.orm import Session

def create_location(db: Session, location_data: dict):
    db_location = Location(**location_data)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_locations(db: Session):
    return db.query(Location).all()

def get_location(db: Session, location_id: int):
    return db.query(Location).filter(Location.id == location_id).first()

def get_location_by_name(db: Session, name: str):
    return db.query(Location).filter(Location.name == name).first()

def update_location(db: Session, location_id: int, location_data: dict):
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if db_location:
        for key, value in location_data.items():
            setattr(db_location, key, value)
        db.commit()
        db.refresh(db_location)
    return db_location

def delete_location(db: Session, location_id: int):
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if db_location:
        db.delete(db_location)
        db.commit()
    return db_location


def create_weather_record(db: Session, record_data: dict):
    db_record = WeatherRecord(**record_data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_weather_records(db: Session):
    return db.query(WeatherRecord).all()

def get_weather_records_by_location(db: Session, location_id: int):
    return db.query(WeatherRecord).filter(WeatherRecord.location_id == location_id).all()

def get_weather_record(db: Session, record_id: int):
    return db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()

def update_weather_record(db: Session, record_id: int, record_data: dict):
    db_record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if db_record:
        for key, value in record_data.items():
            setattr(db_record, key, value)
        db.commit()
        db.refresh(db_record)
    return db_record

def delete_weather_record(db: Session, record_id: int):
    db_record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if db_record:
        db.delete(db_record)
        db.commit()
    return db_record
    