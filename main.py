# Import necessary modules
from agent import TravelAgent
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve API keys from environment variables
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
KIWI_API_KEY = os.getenv("KIWI_API_KEY")
OTM_API_KEY = os.getenv("OPENTRIPMAP_API_KEY")
OWM_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def main():
    """
    Main function to initialize the TravelAgent and handle user queries.
    """
    # Initialize the travel agent with all API keys
    agent = TravelAgent(OPENAI_KEY, KIWI_API_KEY, OTM_API_KEY, OWM_API_KEY)

    print("Welcome to the AI Travel Assistant. Please enter your query:")

    # Get user input
    user_input = input("Your query: ")

    # The agent interprets the query and decides what to do
    response = agent.handle_query(user_input)

    # Print the agent's response
    print("\n=== Agent's Response ===")
    print(response)

if __name__ == "__main__":
    main()