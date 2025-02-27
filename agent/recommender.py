import random
from sentence_transformers import SentenceTransformer, util

class Recommender:
    """
    An advanced recommendation system for suggesting travel destinations based on user preferences.
    Now powered by sentence-transformers for more accurate recommendations.
    """
    def __init__(self):
        """
        Initializes the Recommender with predefined categories and a sentence-transformers model.
        """
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.recommendations = {
            "beach": ["Maldives", "Hawaii", "Cancun", "Bali", "Ibiza"],
            "adventure": ["Patagonia", "Swiss Alps", "Peru", "Nepal", "New Zealand"],
            "culture": ["Rome", "Kyoto", "Paris", "Cairo", "Istanbul"],
            "nature": ["Amazon Rainforest", "Yosemite", "Banff National Park", "Kruger National Park"],
            "luxury": ["Dubai", "Monaco", "Santorini", "Bora Bora", "Singapore"],
            "budget": ["Thailand", "Vietnam", "Mexico", "Portugal", "Poland"]
        }
        self.category_embeddings = {
            category: self.model.encode(category) for category in self.recommendations
        }
    
    def recommend_destination(self, user_preference: str) -> str:
        """
        Suggests a travel destination based on user preference using sentence embeddings.
        
        :param user_preference: A string indicating the user's preferred travel style.
        :return: A destination best matching the user's preference.
        """
        user_embedding = self.model.encode(user_preference)
        best_match = max(self.category_embeddings.keys(), 
                         key=lambda category: util.cos_sim(user_embedding, self.category_embeddings[category]))
        
        return random.choice(self.recommendations[best_match])

    def get_available_categories(self) -> list:
        """
        Retrieves all available travel categories.
        
        :return: A list of available travel categories.
        """
        return list(self.recommendations.keys())