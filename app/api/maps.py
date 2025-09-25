from fastapi import APIRouter, HTTPException, Query
from app.services.maps import MapsService

router = APIRouter(prefix="/maps", tags=["maps"])
maps_service = MapsService()

@router.get("/location-details")
async def get_location_details(location: str = Query(...)):
    try:
        details = await maps_service.get_location_details(location)
        return details
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/static-map")
async def get_static_map(
    latitude: float = Query(...),
    longitude: float = Query(...),
    zoom: int = Query(10, ge=1, le=20),
    size: str = Query("400x400"),
    map_type: str = Query("roadmap")
):
    try:
        map_url = maps_service.get_static_map_url(latitude, longitude, zoom, size, map_type)
        return {
            "map_url": map_url,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "zoom": zoom,
            "size": size,
            "map_type": map_type
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
