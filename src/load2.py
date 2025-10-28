import os
import pandas as pd
from sqlalchemy import create_engine

STANDARD_COLS = [
    "id","address","city","state","state_fips","zip_code","county","county_fips",
    "latitude","longitude","property_type","bedrooms","bathrooms","square_footage","year_built"
]

RENAME_MAP = {
    # common mismatches
    "county_Fips": "county_fips",
    "formattedAddress": "address",
    "zipCode": "zip_code",
    "stateFips": "state_fips",
    "countyFips": "county_fips",
    "propertyType": "property_type",
    "squareFootage": "square_footage",
    "yearBuilt": "year_built",
}

engine = create_engine(
    "postgresql+psycopg2://postgres@127.0.0.1:5432/primesquare_prod",
    pool_pre_ping=True,
)

def load_t0_db(file_name, if_exists_mode):
    # 1) read
    df = pd.read_csv(file_name)

    # 2) normalize column names
    df.rename(columns=RENAME_MAP, inplace=True)

    # 3) ensure every standard column exists
    for col in STANDARD_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    # 4) keep only the standard set & order
    df = df[STANDARD_COLS]

    # 5) write
    df.to_sql("properties_data", engine, if_exists=if_exists_mode, index=False)
    print(f"✅ Loaded: {file_name} → {if_exists_mode}")


if __name__ == "__main__":
    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX")
    ]

    first = True
    for city, state in cities:
        city_clean = city.replace(" ", "")
        file_name = f"data/transformed/properties_data_{city_clean}_{state}.csv"
        if os.path.exists(file_name):
            load_t0_db(file_name, "replace" if first else "append")
            first = False
        else:
            print(f" File not found: {file_name}")

    print(" All cities loaded into database!")
