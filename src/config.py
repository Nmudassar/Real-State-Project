import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('RENTCAST_API_KEY')

BASE_URL = "https://api.rentcast.io/v1/properties"