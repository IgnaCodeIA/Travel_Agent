from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from agent.travel_agent import TravelAgent
import os
import redis
import json
import jwt
import datetime
from typing import Dict

# Initialize FastAPI app
app = FastAPI()

# OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize Redis for session storage
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# File where user data will be stored
USERS_FILE = "users.json"

def load_users():
    """ Load users from the JSON file. """
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as file:
        return json.load(file)

def save_users(users):
    """ Save users to the JSON file. """
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    """
    Generates a JWT access token.
    
    :param data: User data to encode in the token.
    :param expires_delta: Expiration time of the token.
    :return: JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register")
async def register(username: str, password: str):
    """
    Register a new user and store credentials in a JSON file.
    
    :param username: The desired username.
    :param password: The password for the account.
    :return: A success message if registration is successful.
    """
    users = load_users()
    
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")

    users[username] = {"password": password}
    save_users(users)
    
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 authentication endpoint for user login.
    
    :param form_data: User login credentials.
    :return: Access token if credentials are valid.
    """
    users = load_users()
    
    user = users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    # Store the token in Redis for session tracking
    redis_client.set(form_data.username, access_token, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return {"access_token": access_token, "token_type": "bearer"}

def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Verifies the validity of a JWT token.
    
    :param token: JWT token provided in request headers.
    :return: The username of the authenticated user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or not redis_client.get(username):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/chat")
async def chat(user_query: str = Query(..., description="User's travel-related query"), user_id: str = Depends(verify_token)):
    """
    API endpoint to process user queries through the Travel Agent, maintaining session context.
    
    :param user_query: A travel-related question from the user.
    :param user_id: Authenticated user's ID.
    :return: A structured response from the AI travel assistant.
    """
    session_data = redis_client.get(user_id)
    session = json.loads(session_data) if session_data else {"history": [], "last_city": None}

    response = agent.handle_query(user_query)

    # Store the last mentioned city if relevant
    if "flights" in response:
        session["last_city"] = response["flights"]["destination"]
    elif "tourism" in response:
        session["last_city"] = response["tourism"]["city"]
    elif "weather" in response:
        session["last_city"] = response["weather"]["city"]

    # Store conversation history
    session["history"].append({"user": user_query, "assistant": response})

    # Update session in Redis
    redis_client.set(user_id, json.dumps(session), ex=3600)  # Expires in 1 hour

    return {"response": response, "session": session}
