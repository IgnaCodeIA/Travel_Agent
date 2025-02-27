import os
import json
import semantic_kernel as sk
from semantic_kernel.connectors.ai.openai import OpenAIChatCompletion
from apis.flight_api import FlightAPI
from apis.tourism_api import TourismAPI
from apis.weather_api import WeatherAPI

class TravelAgent:
    def __init__(self, openai_key, kiwi_key, otm_key, owm_key):
        """
        Initializes the TravelAgent with API keys and configures the Semantic Kernel.
        """
        self.kernel = sk.Kernel()
        self.llm = OpenAIChatCompletion(service_id="gpt-4", api_key=openai_key)
        self.kernel.add_text_completion_service("gpt", self.llm)

        self.flight_api = FlightAPI(kiwi_key)
        self.tourism_api = TourismAPI(otm_key)
        self.weather_api = WeatherAPI(owm_key)

        self.kernel.register_native_function("get_flight", self.get_flight_info)
        self.kernel.register_native_function("get_pois", self.get_pois_info)
        self.kernel.register_native_function("get_weather", self.get_weather_info)
    
    def preprocess_query(self, user_query: str) -> str:
        """
        Cleans and preprocesses the user query to ensure clarity before sending it to the LLM.
        """
        user_query = user_query.strip().lower()
        return user_query if user_query else "User provided an empty query."
    
    def get_flight_info(self, origin_city: str, dest_city: str, date: str):
        """
        Retrieves flight information between two cities on a specific date.
        """
        try:
            origin_code = self.flight_api.get_city_code(origin_city)
            dest_code = self.flight_api.get_city_code(dest_city)
            result = self.flight_api.search_flights(origin_code, dest_code, date)
        except Exception as e:
            return {"error": f"[Flight error] {e}"}
        
        if not result:
            return {"message": f"No flights found from {origin_city} to {dest_city} on {date}."}
        
        return {
            "origin": origin_city,
            "destination": dest_city,
            "price": result["price"],
            "airline": result.get("airline", "N/A"),
            "departure": result.get("departure")
        }

    def get_pois_info(self, city: str):
        """
        Retrieves points of interest for a given city.
        """
        try:
            pois = self.tourism_api.get_top_pois(city)
        except Exception as e:
            return {"error": f"[Tourism error] {e}"}
        
        if not pois:
            return {"message": f"No points of interest found in {city}."}
        
        return {"city": city, "points_of_interest": pois}

    def get_weather_info(self, city: str):
        """
        Retrieves weather information for a specific city.
        """
        try:
            weather = self.weather_api.get_current_weather(city)
        except Exception as e:
            return {"error": f"[Weather error] {e}"}
        
        return {
            "city": city,
            "temperature": weather["temperature"],
            "description": weather["description"]
        }
    
    def handle_query(self, user_query: str):
        """
        Processes the user query, determines the necessary information, and calls the appropriate functions.
        """
        clean_query = self.preprocess_query(user_query)
        
        prompt = f'''
        You are an AI travel assistant. A user has made the following request:
        "{clean_query}"
        
        Identify the required information and return a structured JSON response.
        If the request involves flights, call get_flight.
        If the request is about tourism, call get_pois.
        If the request is about weather, call get_weather.
        Ensure the output follows this structure:
        {{"flights": <data>, "tourism": <data>, "weather": <data>}}
        '''
        
        response = self.kernel.invoke(self.llm, prompt)
        
        try:
            structured_response = json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Invalid response format from AI."}
        
        result = {}
        
        if "flights" in structured_response:
            flight_data = structured_response["flights"]
            if flight_data:
                result["flights"] = self.get_flight_info(
                    flight_data.get("origin"), 
                    flight_data.get("destination"), 
                    flight_data.get("date")
                )
        
        if "tourism" in structured_response:
            tourism_data = structured_response["tourism"]
            if tourism_data:
                result["tourism"] = self.get_pois_info(tourism_data.get("city"))
        
        if "weather" in structured_response:
            weather_data = structured_response["weather"]
            if weather_data:
                result["weather"] = self.get_weather_info(weather_data.get("city"))
        
        return result
