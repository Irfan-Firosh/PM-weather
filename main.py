from app.db.session import engine
from app.db.base import Base
from fastapi import FastAPI
from app.api.weather import router as weather_router
from app.api.weather_crud import router as weather_crud_router
from app.api.export import router as export_router
from app.api.maps import router as maps_router
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather API", 
    description="Weather API with CRUD operations, export functionality, and Google Maps integration", 
    version="1.0.0"
)
app.include_router(weather_router)
app.include_router(weather_crud_router)
app.include_router(export_router)
app.include_router(maps_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)