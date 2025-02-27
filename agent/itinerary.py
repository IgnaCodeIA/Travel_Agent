from apis.tourism_api import TourismAPI
from apis.weather_api import WeatherAPI
from sklearn.cluster import KMeans
import numpy as np
from collections import defaultdict

class Itinerary:
    """
    A system for generating optimized travel itineraries based on destination, duration, and available activities.
    Now enhanced with clustering techniques and priority-based categorization for efficient planning.
    """
    def __init__(self, tourism_api: TourismAPI, weather_api: WeatherAPI):
        """
        Initializes the Itinerary system with required APIs and clustering model.
        
        :param tourism_api: An instance of the TourismAPI for fetching points of interest.
        :param weather_api: An instance of the WeatherAPI for retrieving weather data.
        """
        self.tourism_api = tourism_api
        self.weather_api = weather_api

    def generate_itinerary(self, city: str, days: int) -> list:
        """
        Creates an optimized travel itinerary for a given city and duration.
        
        :param city: The city for which the itinerary should be generated.
        :param days: The number of days for the trip.
        :return: A list containing structured daily activities and weather information.
        """
        weather = self.weather_api.get_current_weather(city)
        pois = self.tourism_api.get_top_pois(city, limit=days * 5)  # Fetch more points for better categorization

        if not pois:
            return [{"day": i + 1, "activities": "No activities available", "weather": f"{weather['temperature']}°C, {weather['description']}"} for i in range(days)]
        
        # Categorize POIs based on their type
        categorized_pois = defaultdict(list)
        for poi in pois:
            category = poi.get('categories', 'general')
            categorized_pois[category].append(poi)
        
        # Convert POIs into numerical vectors for clustering
        poi_vectors = np.array([[poi['distance']] for poi in pois])
        
        # Cluster POIs into groups corresponding to the number of days
        num_clusters = min(days, len(pois))  # Ensure we do not create more clusters than POIs
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(poi_vectors)
        
        itinerary = []
        for i in range(days):
            day_pois = [pois[j] for j in range(len(pois)) if clusters[j] == i]
            sorted_pois = sorted(day_pois, key=lambda x: x.get('rating', 0), reverse=True)  # Prioritize high-rated places
            
            itinerary.append({
                "day": i + 1,
                "activities": [f"{poi['name']} ({poi.get('categories', 'N/A')})" for poi in sorted_pois[:3]],
                "weather": f"{weather['temperature']}°C, {weather['description']}"
            })
        
        return itinerary
