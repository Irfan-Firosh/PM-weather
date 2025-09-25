import requests
import os
from dotenv import load_dotenv
load_dotenv()
from typing import Dict, List
from app.core.config import settings

class MapsService:
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyAu8DaAd-4P5iJzaVUIkNMr6nTCcgrcwgk")
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.static_maps_url = "https://maps.googleapis.com/maps/api/staticmap"
    
    def _validate_api_key(self) -> bool:
        return self.api_key and self.api_key != "your_google_maps_api_key_here"
    
    async def get_location_details(self, location: str) -> Dict:
        if not self._validate_api_key():
            raise Exception("Google Maps API key not configured. Please set GOOGLE_MAPS_API_KEY environment variable.")
        
        try:
            params = {
                "address": location,
                "key": self.api_key
            }
            
            response = requests.get(self.geocoding_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] != "OK" or not data.get("results"):
                raise ValueError(f"Location '{location}' not found in Google Maps")
            
            result = data["results"][0]
            return self._format_location_details(result)
            
        except requests.RequestException as e:
            if e.response and e.response.status_code == 403:
                raise Exception("Invalid Google Maps API key or quota exceeded")
            elif e.response and e.response.status_code == 429:
                raise Exception("Google Maps API rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"Google Maps API error: {str(e)}")
        except Exception as e:
            if "not found" in str(e).lower():
                raise e
            else:
                raise Exception(f"Location processing error: {str(e)}")
    
    def _format_location_details(self, result: Dict) -> Dict:       
        geometry = result.get("geometry", {})
        location = geometry.get("location", {})
        
        return {
            "formatted_address": result.get("formatted_address", ""),
            "place_id": result.get("place_id", ""),
            "coordinates": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng")
            },
            "location_type": geometry.get("location_type", ""),
            "types": result.get("types", [])
        }
    
    def get_static_map_url(self, latitude: float, longitude: float, zoom: int = 10, size: str = "400x400", map_type: str = "roadmap") -> str:
        if not self._validate_api_key():
            raise Exception("Google Maps API key not configured. Please set GOOGLE_MAPS_API_KEY environment variable.")
        
        params = {
            "center": f"{latitude},{longitude}",
            "zoom": zoom,
            "size": size,
            "maptype": map_type,
            "markers": f"color:red|{latitude},{longitude}",
            "key": self.api_key
        }
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.static_maps_url}?{param_string}"
