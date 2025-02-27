import os
import json
import semantic_kernel as sk
from semantic_kernel.connectors.ai.openai import OpenAIChatCompletion
from apis.flight_api import FlightAPI
from apis.tourism_api import TourismAPI
from apis.weather_api import WeatherAPI
from agent.recommender import Recommender
from agent.itinerary import Itinerary
import redis

class TravelAgent:
    """
    An AI-powered travel assistant that provides flight, tourism, weather information,
    recommendations, and itinerary generation. Now supports session management via Redis.
    """
    def __init__(self, openai_key, kiwi_key, otm_key, owm_key, redis_host='localhost', redis_port=6379):
        """
        Initializes the TravelAgent with API keys, Redis for session storage, and configures the Semantic Kernel.
        """
        self.kernel = sk.Kernel()
        self.llm = OpenAIChatCompletion(service_id="gpt-4", api_key=openai_key)
        self.kernel.add_text_completion_service("gpt", self.llm)

        self.flight_api = FlightAPI(kiwi_key)
        self.tourism_api = TourismAPI(otm_key)
        self.weather_api = WeatherAPI(owm_key)
        
        self.recommender = Recommender()
        self.itinerary = Itinerary(self.tourism_api, self.weather_api)

        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

        self.kernel.register_native_function("get_flight", self.get_flight_info)
        self.kernel.register_native_function("get_pois", self.get_pois_info)
        self.kernel.register_native_function("get_weather", self.get_weather_info)
        self.kernel.register_native_function("get_recommendation", self.get_recommendation)
        self.kernel.register_native_function("generate_itinerary", self.generate_itinerary)
    
    def preprocess_query(self, user_query: str) -> str:
        """
        Cleans and preprocesses the user query to ensure clarity before sending it to the LLM.
        """
        return user_query.strip().lower()
    
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
        
        return result if result else {"message": "No flights available."}

    def get_pois_info(self, city: str):
        """
        Retrieves points of interest for a given city.
        """
        try:
            pois = self.tourism_api.get_top_pois(city)
        except Exception as e:
            return {"error": f"[Tourism error] {e}"}
        
        return pois if pois else {"message": "No points of interest found."}

    def get_weather_info(self, city: str):
        """
        Retrieves weather information for a specific city.
        """
        try:
            return self.weather_api.get_current_weather(city)
        except Exception as e:
            return {"error": f"[Weather error] {e}"}

    def get_recommendation(self, user_preference: str):
        """
        Suggests a travel destination based on user preference.
        """
        return {"recommendation": self.recommender.recommend_destination(user_preference)}

    def generate_itinerary(self, city: str, days: int):
        """
        Generates a structured travel itinerary for a given city and duration.
        """
        return self.itinerary.generate_itinerary(city, days)
    
    def get_session(self, user_id: str):
        """
        Retrieve the user's session from Redis. If not found, create an empty session.
        """
        session_data = self.redis_client.get(user_id)
        return json.loads(session_data) if session_data else {"history": [], "last_city": None}

    def update_session(self, user_id: str, new_data: dict):
        """
        Update the user's session data in Redis.
        """
        self.redis_client.set(user_id, json.dumps(new_data), ex=3600)  # Expires in 1 hour

    def handle_query(self, user_id: str, user_query: str):
        """
        Processes the user query, determines the necessary information, and calls the appropriate functions.
        Now supports session storage via Redis.
        """
        session = self.get_session(user_id)
        clean_query = self.preprocess_query(user_query)
        
        prompt = f'''
        You are an AI travel assistant. A user has made the following request:
        "{clean_query}"
        
        Identify the required information and return a structured JSON response.
        The response should include only relevant sections: flights, tourism, weather, recommendations, or itinerary.
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
        
        if "recommendations" in structured_response:
            rec_data = structured_response["recommendations"]
            if rec_data:
                result["recommendations"] = self.get_recommendation(rec_data.get("preference"))
        
        if "itinerary" in structured_response:
            itinerary_data = structured_response["itinerary"]
            if itinerary_data:
                result["itinerary"] = self.generate_itinerary(itinerary_data.get("city"), itinerary_data.get("days"))
        
        # Update session with latest request
        session["history"].append({"user": user_query, "assistant": result})
        self.update_session(user_id, session)

        return result
