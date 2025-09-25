import requests
import os
from typing import Dict, List, Tuple
from datetime import datetime

class WeatherService:
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "your_api_key_here")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0"
    
    def _is_zip_code(self, location: str) -> bool:
        clean_location = location.replace(" ", "").replace("-", "")
        return clean_location.isdigit() and len(clean_location) >= 4
    
    def _is_coordinate_string(self, location: str) -> bool:
        try:
            clean_location = location.replace(" ", "")
            if "," in clean_location:
                parts = clean_location.split(",")
                if len(parts) == 2:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, IndexError):
            pass
        return False
    
    def _parse_coordinates(self, location: str) -> Tuple[float, float]:
        clean_location = location.replace(" ", "")
        parts = clean_location.split(",")
        return float(parts[0]), float(parts[1])
    
    async def get_coordinates_from_location(self, location: str) -> Tuple[float, float]:
        try:
            if self._is_coordinate_string(location):
                return self._parse_coordinates(location)
            
            if self._is_zip_code(location):
                url = f"{self.geocoding_url}/zip"
                params = {
                    "zip": f"{location},US",
                    "appid": self.api_key
                }
            else:
                url = f"{self.geocoding_url}/direct"
                params = {
                    "q": location,
                    "limit": 1,
                    "appid": self.api_key
                }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data or (isinstance(data, list) and len(data) == 0):
                raise ValueError(f"Location '{location}' not found. Please check spelling or try a different format.")
            
            if isinstance(data, list):
                result = data[0]
            else:
                result = data
            
            return result["lat"], result["lon"]
                
        except requests.RequestException as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise e
    
    async def get_current_weather(self, location: str) -> Dict:
        try:
            lat, lon = await self.get_coordinates_from_location(location)
            
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_current_weather(data)
            
        except requests.RequestException as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise e
    
    async def get_5day_forecast(self, location: str) -> List[Dict]:
        try:
            lat, lon = await self.get_coordinates_from_location(location)
            
            url = f"{self.base_url}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_5day_forecast(data)
            
        except requests.RequestException as e:
            raise Exception(f"API error: {str(e)}")
        except Exception as e:
            raise e
    
    def _format_current_weather(self, data: Dict) -> Dict:
        return {
            "location": {
                "name": data["name"],
                "country": data["sys"]["country"],
                "coordinates": {
                    "lat": round(data["coord"]["lat"], 4),
                    "lon": round(data["coord"]["lon"], 4)
                }
            },
            "current": {
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "visibility": round(data.get("visibility", 0) / 1000, 1),
                "condition": {
                    "main": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"]
                },
                "wind": {
                    "speed": round(data["wind"]["speed"], 1),
                    "direction": data["wind"].get("deg", 0)
                },
                "clouds": data["clouds"]["all"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
            }
        }
    
    def _format_5day_forecast(self, data: Dict) -> List[Dict]:
        forecast = []
        current_date = None
        daily_data = {}
        
        for item in data["list"]:
            date = datetime.fromtimestamp(item["dt"]).date()
            
            if current_date != date:
                if current_date is not None:
                    forecast.append(self._format_daily_forecast(daily_data))
                current_date = date
                daily_data = {
                    "date": date.isoformat(),
                    "temps": [],
                    "conditions": [],
                    "humidity": [],
                    "wind_speed": [],
                    "pressure": []
                }
            
            daily_data["temps"].append(item["main"]["temp"])
            daily_data["conditions"].append({
                "main": item["weather"][0]["main"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]
            })
            daily_data["humidity"].append(item["main"]["humidity"])
            daily_data["wind_speed"].append(item["wind"]["speed"])
            daily_data["pressure"].append(item["main"]["pressure"])
        
        if daily_data:
            forecast.append(self._format_daily_forecast(daily_data))
        
        return forecast[:5]
    
    def _format_daily_forecast(self, daily_data: Dict) -> Dict:
        temps = daily_data["temps"]
        conditions = daily_data["conditions"]
        
        condition_counts = {}
        for condition in conditions:
            main = condition["main"]
            condition_counts[main] = condition_counts.get(main, 0) + 1
        
        most_common_condition = max(condition_counts, key=condition_counts.get)
        condition_info = next(c for c in conditions if c["main"] == most_common_condition)
        
        return {
            "date": daily_data["date"],
            "day_name": datetime.fromisoformat(daily_data["date"]).strftime("%A"),
            "temperature": {
                "min": round(min(temps)),
                "max": round(max(temps)),
                "avg": round(sum(temps) / len(temps))
            },
            "condition": condition_info,
            "humidity": round(sum(daily_data["humidity"]) / len(daily_data["humidity"])),
            "wind_speed": round(sum(daily_data["wind_speed"]) / len(daily_data["wind_speed"]), 1),
            "pressure": round(sum(daily_data["pressure"]) / len(daily_data["pressure"]))
        }
    
    def validate_location_input(self, location: str) -> Dict:
        if not location or not location.strip():
            return {"valid": False, "error": "Location cannot be empty"}
        
        location = location.strip()
        
        if self._is_coordinate_string(location):
            try:
                lat, lon = self._parse_coordinates(location)
                return {
                    "valid": True, 
                    "type": "coordinates",
                    "coordinates": (lat, lon),
                    "message": f"Coordinates: {lat}, {lon}"
                }
            except:
                return {"valid": False, "error": "Invalid coordinate format"}
        
        if self._is_zip_code(location):
            return {
                "valid": True,
                "type": "zip_code",
                "message": f"Postal code: {location}"
            }
        
        if len(location) >= 2:
            return {
                "valid": True,
                "type": "location_name",
                "message": f"Location: {location}"
            }
        
        return {"valid": False, "error": "Location too short or invalid"}
    
    async def get_weather_summary(self, location: str) -> Dict:
        try:
            current = await self.get_current_weather(location)
            forecast = await self.get_5day_forecast(location)
            
            return {
                "location": current["location"],
                "current": current["current"],
                "forecast": forecast,
                "summary": {
                    "current_temp": current["current"]["temperature"],
                    "condition": current["current"]["condition"]["description"],
                    "forecast_high": max([day["temperature"]["max"] for day in forecast]),
                    "forecast_low": min([day["temperature"]["min"] for day in forecast])
                }
            }
        except Exception as e:
            raise Exception(f"Weather summary error: {str(e)}")
    
    async def get_location_name_from_coordinates(self, lat: float, lon: float) -> str:
        try:
            url = f"{self.geocoding_url}/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "limit": 1,
                "appid": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                result = data[0]
                return f"{result.get('name', 'Unknown')}, {result.get('country', 'Unknown')}"
            else:
                return f"Location at {lat}, {lon}"
                
        except Exception as e:
            return f"Location at {lat}, {lon}"