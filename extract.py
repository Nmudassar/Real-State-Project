import requests
import json
from src.config import BASE_URL, API_KEY

city ='San Antonio'
state ='TX'

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
        file_name = f"data/raw/properties_data_{city}_{state}.json" 

        with open(file_name, "w") as f:
            json.dump(data, f, indent = 2)

        return file_name    
if __name__ == "__main__":
    # ✅ Just add the 3 cities here (like your instructor said)
    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX")
    ]

    for city, state in cities:
        extract_properties(city, state)

    print("🎉 Extraction completed for all 3 cities!")
