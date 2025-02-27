# TravelAgent - AI-Powered Travel Assistant

## Overview
**TravelAgent** is an AI-driven travel assistant that provides:
- Flight information
- Recommendations for points of interest (POIs)
- Weather forecasts
- Personalized travel recommendations
- Automated itinerary generation

The system integrates **OpenAI GPT-4**, various travel-related APIs, and **Redis** for session management, ensuring an interactive and intelligent experience.

## Features
- **Flight Search**: Retrieves flight details using the **Kiwi API**.
- **Tourist Recommendations**: Suggests top attractions using **OpenTripMap API**.
- **Weather Forecast**: Provides real-time weather data from **OpenWeather API**.
- **Personalized Travel Recommendations**: Suggests destinations based on user preferences using **Sentence Transformers**.
- **Automated Itinerary Planning**: Creates structured itineraries using **KMeans clustering**.
- **User Session Management**: Stores conversation history using **Redis**.
- **Secure Authentication**: Implements OAuth2 authentication and JWT token-based session management.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Redis (for session management)
- Virtual environment (recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/IgnaCodeIA/Travel_Agent
cd Travel_Agent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file and add the required API keys:
```
OPENAI_API_KEY=your_openai_key
KIWI_API_KEY=your_kiwi_key
OPENTRIPMAP_API_KEY=your_opentripmap_key
OPENWEATHER_API_KEY=your_openweather_key
JWT_SECRET=your_jwt_secret
```

## Usage

### Running the Application
```bash
uvicorn chatbot.api:app --reload
```
This starts a **FastAPI** server that provides endpoints for interacting with the TravelAgent.

### Authentication and Token Generation
To interact with the chatbot, users must first register and obtain a token.

#### Register a New User
```bash
curl -X POST "http://localhost:8000/register" -d "username=myuser&password=mypass"
```

#### Login to Obtain a JWT Token
```bash
curl -X POST "http://localhost:8000/token" -d "username=myuser&password=mypass"
```

This returns a JSON response with the access token:
```json
{
    "access_token": "your_jwt_token",
    "token_type": "bearer"
}
```

### Interacting with the Chatbot
Use the obtained JWT token to make API calls:
```bash
curl -X GET "http://localhost:8000/chat?user_query=What%20is%20the%20weather%20in%20Paris?" \
     -H "Authorization: Bearer your_jwt_token"
```

### Example Response
```json
{
    "response": {
        "weather": {
            "city": "Paris",
            "temperature": "12°C",
            "description": "Cloudy"
        }
    },
    "session": {
        "history": [{
            "user": "What is the weather in Paris?",
            "assistant": {
                "weather": {
                    "city": "Paris",
                    "temperature": "12°C",
                    "description": "Cloudy"
                }
            }
        }],
        "last_city": "Paris"
    }
}
```

## API Endpoints
| Method | Endpoint           | Description |
|--------|--------------------|-------------|
| POST   | `/register`        | Register a new user |
| POST   | `/token`           | Authenticate and get a JWT token |
| GET    | `/chat`            | Ask the travel assistant questions |

## Technologies Used
- **FastAPI** - API framework
- **Redis** - Session storage
- **OpenAI GPT-4** - NLP processing
- **Kiwi API** - Flight search
- **OpenTripMap API** - Tourism recommendations
- **OpenWeather API** - Weather forecasts
- **Sentence Transformers** - Recommendation engine
- **KMeans Clustering** - Itinerary generation
- **OAuth2 & JWT** - Authentication and authorization

## License
This project is licensed under the MIT License.
