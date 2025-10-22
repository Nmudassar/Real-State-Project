import os
from dotenv import load_dotenv
# dotenv is python laibaray to load the environment variables from .env file
load_dotenv()

API_KEY = os.getenv("RENTCAST_API_KEY")
BASE_URL = "https://api.rentcast.io/v1/properties"
