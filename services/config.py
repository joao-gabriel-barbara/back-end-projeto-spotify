from dotenv import load_dotenv
import os

load_dotenv()  # carrega o .env

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
frontend_url = os.getenv("FRONTEND_URL")
API_URL = os.getenv("API_URL") 
scope= os.getenv("SCOPE")
SECRET_KEY = os.getenv("SECRET_KEY", "dengoso")
BACKEND_URL = os.getenv("BACKEND_URL")