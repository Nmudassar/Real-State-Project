
import json
import pandas as pd
import os

def transform(file_path, city, state):
    with open(file_path, "r") as f:
        data = json.load(f)

    print(f"📌 Loaded {len(data)} rows for {city}, {state}")
    df = pd.json_normalize(data)

    columns = [
        'id', 'formattedAddress', 'city',
        'state', 'stateFips', 'zipCode', 'county', 'countyFips',
        'latitude', 'longitude', 'propertyType', 'bedrooms',
        'bathrooms', 'squareFootage', 'yearBuilt'
    ]

    df = df[columns]

    df.rename(columns={
        'formattedAddress': 'address',
        'zipCode': 'zip_code',
        'stateFips': 'state_fips',
        'countyFips': 'county_fips',
        'propertyType': 'property_type',
        'squareFootage': 'square_footage',
        'yearBuilt': 'year_built'
    }, inplace=True)

    city_clean = city.replace(" ", "")
    output_path = f"data/transformed/properties_data_{city_clean}_{state}.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ CSV Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX")
    ]

    for city, state in cities:
        city_clean = city.replace(" ", "")
        file_path = f"data/raw/properties_data_{city_clean}_{state}.json"

        if os.path.exists(file_path):
            transform(file_path, city, state)
        else:
            print(f" File not found: {file_path}")

    print(" Transformation completed for all cities!")