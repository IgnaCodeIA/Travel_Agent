import os
import requests

class TourismAPIError(Exception):
    """Custom exception for TourismAPI errors."""
    pass

class TourismAPI:
    BASE_URL = "https://api.opentripmap.com/0.1"

    def __init__(self, api_key: str = None, lang: str = "en"):
        """
        Initialize the TourismAPI with the given API key and language.
        If no API key is provided, it tries to retrieve it from environment variables.
        
        :param api_key: OpenTripMap API key
        :param lang: Language for results (default is English)
        """
        self.api_key = api_key or os.getenv("OPENTRIPMAP_API_KEY")
        if not self.api_key:
            raise TourismAPIError("OpenTripMap API key is required.")
        
        self.lang = lang  # Language for results (default is English)

    def get_city_coordinates(self, city_name: str):
        """
        Get the coordinates (latitude, longitude) of a city by name.
        
        :param city_name: Name of the city
        :return: Tuple with latitude and longitude
        :raises TourismAPIError: If there is a network error or the city is not found
        """
        url = f"{self.BASE_URL}/{self.lang}/places/geoname"
        params = {"name": city_name, "apikey": self.api_key}
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise TourismAPIError(f"Error fetching city coordinates: {e}")
        
        data = resp.json()
        
        if "lat" not in data or "lon" not in data:
            raise TourismAPIError(f"City '{city_name}' not found.")
        
        return data["lat"], data["lon"]

    def get_top_pois(self, city_name: str, radius_m: int = 5000, limit: int = 5):
        """
        Get a list of points of interest (POIs) near the center of the given city.
        Returns up to 'limit' places within 'radius_m' meters.
        
        :param city_name: Name of the city
        :param radius_m: Radius in meters to search for POIs
        :param limit: Maximum number of POIs to return
        :return: List of dictionaries with POI details
        :raises TourismAPIError: If there is a network error
        """
        # First, get the coordinates of the city
        lat, lon = self.get_city_coordinates(city_name)
        
        url = f"{self.BASE_URL}/{self.lang}/places/radius"
        params = {
            "lat": lat,
            "lon": lon,
            "radius": radius_m,
            "limit": limit,
            "rate": 2,  # Consider places with rating 2+ (1=less relevant, 3=most relevant)
            "format": "json",
            "apikey": self.api_key,
            # Example of category filter: "kinds": "cultural,historic,natural"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise TourismAPIError(f"Error fetching points of interest: {e}")
        
        data = resp.json()
        
        pois = []
        for item in data:
            name = item.get("name")
            kinds = item.get("kinds")
            dist = item.get("dist")
            
            if name:
                pois.append({
                    "name": name,
                    "categories": kinds,
                    "distance": dist
                })
        
        return pois