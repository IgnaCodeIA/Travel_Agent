import os
import requests

class FlightAPIError(Exception):
    """Custom exception for FlightAPI errors."""
    pass

class FlightAPI:
    BASE_URL = "https://tequila-api.kiwi.com"

    def __init__(self, api_key: str = None):
        """
        Initialize the FlightAPI with the given API key.
        If no API key is provided, it tries to retrieve it from environment variables.
        
        :param api_key: Kiwi (Tequila) API key
        """
        self.api_key = api_key or os.getenv("KIWI_API_KEY")
        if not self.api_key:
            raise FlightAPIError("Kiwi (Tequila) API key is required.")
        
        # Common header for all requests
        self.headers = {"apikey": self.api_key}

    def get_city_code(self, city_name: str) -> str:
        """
        Get the IATA code for a given city using the location query endpoint.
        
        :param city_name: Name of the city
        :return: IATA code of the city
        :raises FlightAPIError: If there is a network error or the city code is not found
        """
        url = f"{self.BASE_URL}/locations/query"
        params = {"term": city_name, "location_types": "city"}
        
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise FlightAPIError(f"Network error while fetching city code: {e}")
        
        data = resp.json()
        locations = data.get("locations")
        
        if not locations:
            raise FlightAPIError(f"No IATA code found for city: {city_name}")
        
        return locations[0]["code"]  # IATA code of the first match

    def search_flights(self, origin: str, destination: str, date: str):
        """
        Search for flights from origin to destination on the given date (format DD/MM/YYYY).
        Returns data of the cheapest flight found (price, airline, schedule, etc.).
        
        :param origin: IATA code of the origin city
        :param destination: IATA code of the destination city
        :param date: Date of the flight in DD/MM/YYYY format
        :return: Dictionary with flight details or None if no flights are found
        :raises FlightAPIError: If there is a network error
        """
        url = f"{self.BASE_URL}/v2/search"
        params = {
            "fly_from": origin,
            "fly_to": destination,
            "date_from": date,
            "date_to": date,
            "one_for_city": 1,
            "curr": "USD"
        }
        
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise FlightAPIError(f"Network error while searching for flights: {e}")
        
        data = resp.json()
        flights = data.get("data")
        
        if not flights:
            return None  # No flights found for the given parameters
        
        # Take the first flight (the cheapest according to Kiwi)
        best = flights[0]
        
        result = {
            "price": best.get("price"),
            "origin_city": best.get("cityFrom"),
            "origin_airport": best.get("flyFrom"),
            "dest_city": best.get("cityTo"),
            "dest_airport": best.get("flyTo"),
            "departure": best.get("route")[0].get("local_departure") if best.get("route") else None,
            "airline": best.get("airlines")[0] if best.get("airlines") else None
        }
        
        return result