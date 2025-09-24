from app.db.models import WeatherRecord
from sqlalchemy.orm import Session

def create_weather_record(db: Session, record_data: dict):
    db_record = WeatherRecord(**record_data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_weather_records(db: Session):
    return db.query(WeatherRecord).all()

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
    