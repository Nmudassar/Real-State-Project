import requests
import json
from src.config import BASE_URL, API_KEY



def extract_properties(city='San Antonio', state='TX'):
    headers = {
        "accept": "application/json",
        "X-Api-Key": API_KEY
    }
    params = {
             "city": city,
             "state": state,
    }
    print(f"fetching properties data for {city}, {state}")
    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    
    else:
        
        print({response.status_code} - {response.text})
        