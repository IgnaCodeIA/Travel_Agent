import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve API keys from environment variables
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
KIWI_KEY = os.getenv("KIWI_API_KEY")
OTM_KEY = os.getenv("OPENTRIPMAP_API_KEY")
OWM_KEY = os.getenv("OPENWEATHER_API_KEY")