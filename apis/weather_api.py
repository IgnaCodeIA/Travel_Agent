import os
import requests

class WeatherAPIError(Exception):
    """Custom exception for WeatherAPI errors."""
    pass

class WeatherAPI:
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str = None, default_city: str = None):
        """
        Initialize the WeatherAPI with the given API key and default city.
        If no API key is provided, it tries to retrieve it from environment variables.
        
        :param api_key: OpenWeatherMap API key
        :param default_city: Default city for weather queries
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise WeatherAPIError("OpenWeatherMap API key is required.")
        self.default_city = default_city

    def get_current_weather(self, city: str = None, lang: str = "es"):
        """
        Get the current weather for the given city (by name).
        Returns a dictionary with temperature (°C), description, and other basic data.
        
        :param city: Name of the city
        :param lang: Language for the weather description (default is Spanish)
        :return: Dictionary with weather details
        :raises WeatherAPIError: If there is a network error or the city is not specified
        """
        city_query = city or self.default_city
        if not city_query:
            raise WeatherAPIError("You must specify a city to query the weather.")
        
        url = f"{self.BASE_URL}/weather"
        params = {"q": city_query, "appid": self.api_key, "units": "metric", "lang": lang}
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise WeatherAPIError(f"Error fetching weather for '{city_query}': {e}")
        
        data = resp.json()
        
        # Extract relevant information
        main = data.get("main", {})
        weather_list = data.get("weather", [])
        
        if not main or not weather_list:
            # Unexpected response
            raise WeatherAPIError(f"Unexpected weather data for '{city_query}'.")
        
        temp = main.get("temp")
        desc = weather_list[0].get("description")  # textual description
        country = data.get("sys", {}).get("country")
        city_name = data.get("name")
        
        return {
            "city": city_name,
            "country": country,
            "temperature": temp,
            "description": desc
        }