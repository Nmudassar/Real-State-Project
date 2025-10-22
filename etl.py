import requests
# importan json
from src.config import BASE_URL, API_KEY



def extract_properties(city='San Antonio', state='TX'):
    headers = {"accept": "application/json",
               X-Api-Key: "RENCAST_API_KEY"
               }
    params = {
        "city": city,
        "state": state,
    }
