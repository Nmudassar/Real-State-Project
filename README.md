
---

# PrimeSquare Properties Ltd — Real Estate ETL Pipeline

A production-style ETL (Extract, Transform, Load) pipeline that collects real estate property listings from the RentCast API, standardizes the data model, and loads analytics-ready records into PostgreSQL. Designed for clarity, automation, and data analytics enablement.

---

## Table of Contents

1. Project Overview
2. Architecture Diagram
3. Skills Demonstrated
4. Tech Stack
5. File/Folder Structure
6. Setup and Configuration
7. End-to-End Run
8. Code (Extract, Transform, Load & Orchestration)
9. Before & After Data Example
10. SQL Query Examples
11. Pipeline Execution Output
12. Notes on Usage and Limits
13. Automated Scheduling with Windows Task Scheduler
14. Challenges & Learning
15. Future Enhancements
16. License and Contact

---

## 1) Project Overview

This project automates real estate data ingestion from the RentCast API for selected cities in Texas (San Antonio, Houston, and Dallas). The data is cleaned, transformed into a standardized schema, and loaded into PostgreSQL to support analytics and reporting use cases. Secrets are handled via `.env` and never committed to source control.

---

## 2) Architecture Diagram

```
             +-------------------+
             |  Scheduler / CLI  |
             +---------+---------+
                       |
                       v
+----------------------+----------------------+
|                   EXTRACT                  |
|  Python requests -> RentCast API -> JSON   |
+----------------------+----------------------+
                       |
                       v
+----------------------+----------------------+
|                  TRANSFORM                 |
|  Normalize JSON -> Standard Columns -> CSV |
+----------------------+----------------------+
                       |
                       v
+----------------------+----------------------+
|                     LOAD                   |
|  pandas.to_sql -> PostgreSQL (properties)  |
+----------------------+----------------------+
                       |
                       v
               Analytics & BI (SQL / Power BI)
```

---

## 3) Skills Demonstrated

* API integration using Python requests
* JSON data extraction and normalization
* Schema design and data transformation
* PostgreSQL loading via SQLAlchemy
* Secure secret management with `.env`
* Production automation using Windows Task Scheduler
* Clean GitHub repository structure and documentation

---

## 4) Tech Stack

* Python 3.10+
* PostgreSQL
* Libraries: Requests, Pandas, SQLAlchemy, Psycopg2-binary, python-dotenv
* Windows Task Scheduler (automation)
* Git & GitHub

---

## 5) File/Folder Structure

```
real-estate-etl-pipeline/
├─ assets/                        # optional: diagrams, screenshots
├─ data/
│  ├─ raw/                        # raw JSON from API (ignored by Git)
│  └─ transformed/                # CSV cleaned for loading (ignored by Git)
├─ logs/                          # optional pipeline run logs
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ extract.py
│  ├─ transform2.py
│  └─ load2.py
├─ .env                           # secret credentials (ignored by Git)
├─ .gitignore
├─ requirements.txt
├─ README.md
└─ run.py                         # optional quick runner
```

Recommended `.gitignore`:

```gitignore
my-env/
.venv/
venv/
.env
__pycache__/
*.pyc
.vscode/
.DS_Store
Thumbs.db
data/raw/
data/transformed/
logs/
```

---

## 6) Setup and Configuration

### 6.1 Create and activate a virtual environment

```bash
python -m venv my-env
my-env\Scripts\activate
```

### 6.2 Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```txt
requests
pandas
sqlalchemy
psycopg2-binary
python-dotenv
```

### 6.3 Create `.env` with API key

```env
API_KEY=your_rentcast_api_key_here
BASE_URL=https://api.rentcast.io/v1/properties
```

> Get your key at [https://www.rentcast.io/api](https://www.rentcast.io/api) and keep it private.

---

## 7) End-to-End Run

Execute:

```bash
python src/main.py
```

Expected outputs:

* JSON stored: `data/raw/`
* CSV stored: `data/transformed/`
* PostgreSQL updated: `properties_data` table

---

## 8) Code (Extract, Transform, Load & Orchestration)

Place the following files under `src/`.

### 8.1 `src/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.rentcast.io/v1/properties")



```

### 8.2 `src/extract.py`

```python
iimport requests
import json
from config import BASE_URL, API_KEY
from pathlib import Path

#
RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def extract_properties(city, state):
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
        file_name = RAW_DIR / f"properties_data_{city}_{state}.json"

        with open(file_name, "w") as f:
            json.dump(data, f, indent=2)

        return file_name
if __name__ == "__main__":
    #  Just add the 3 cities here 
    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX")
    ]

    for city, state in cities:
        extract_properties(city, state)

    print(" Extraction completed for all 3 cities!")

```

### 8.3 `src/transform2.py`

```python

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
```

### 8.4 `src/load2.py`

```python
fimport os
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

```

### 8.5 `src/main.py`

```python
from extract import extract_properties
from transform2 import transform
from load2 import load_t0_db
from pathlib import Path

def run_pipeline():
    print("Starting ETL pipeline run")

    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX")
    ]
    Path("data/transformed").mkdir(parents=True, exist_ok=True)
    # Step 1: Extract
    first = True

    for city, state in cities:
        raw_file = extract_properties(city=city, state=state)
        if raw_file:
            clean_file = transform(raw_file, city, state)
            if first:
                load_t0_db(clean_file, "replace")
                first = False
            else:
                load_t0_db(clean_file, "append")
            print(f"ETL pipeline successfully completed for {city}, {state}\n")
        else:
            print(f"ETL pipeline failed during extraction step for {city}, {state}\n")

if __name__ == "__main__":
    run_pipeline()

    
    
```

### 8.6 Optional `run.py` (root) for a single quick run

```python
from src.extract import extract_properties
from src.transform2 import transform

if __name__ == "__main__":
    raw = extract_properties("San Antonio", "TX")
    transform(raw, "San Antonio", "TX")
```

---

## 9) Before & After Data Example

**Before (raw JSON snippet):**

```json
[
  {
    "id": "abc123",
    "formattedAddress": "123 Main St, San Antonio, TX 78201",
    "city": "San Antonio",
    "state": "TX",
    "zipCode": "78201",
    "stateFips": "48",
    "countyFips": "029",
    "county": "Bexar",
    "latitude": 29.46,
    "longitude": -98.49,
    "propertyType": "Single Family",
    "bedrooms": 3,
    "bathrooms": 2,
    "squareFootage": 1450,
    "yearBuilt": 1998
  }
]
```

**After (transformed CSV columns):**

```
id,address,city,state,state_fips,zip_code,county,county_fips,latitude,longitude,property_type,bedrooms,bathrooms,square_footage,year_built
abc123,123 Main St, San Antonio, TX 78201,San Antonio,TX,48,78201,Bexar,029,29.46,-98.49,Single Family,3,2,1450,1998
```

---

## 10) SQL Query Examples

Top 10 properties by most recent year built:

```sql
SELECT id, address, city, state, year_built
FROM properties_data
ORDER BY year_built DESC, id
LIMIT 10;
```

City-level counts:

```sql
SELECT city, state, COUNT(*) AS listings
FROM properties_data
GROUP BY city, state
ORDER BY listings DESC;
```

Bedrooms distribution for a city:

```sql
SELECT bedrooms, COUNT(*) AS cnt
FROM properties_data
WHERE city = 'San Antonio' AND state = 'TX'
GROUP BY bedrooms
ORDER BY bedrooms;
```

---

## 11) Pipeline Execution Output

Example console output:

```
Starting ETL pipeline run
Fetching properties for San Antonio, TX
Clean CSV saved: .../data/transformed/properties_data_SanAntonio_TX.csv
Loaded 250 rows into properties_data (replace) from .../SanAntonio_TX.csv
ETL completed for San Antonio, TX

Fetching properties for Houston, TX
Clean CSV saved: .../data/transformed/properties_data_Houston_TX.csv
Loaded 300 rows into properties_data (append) from .../Houston_TX.csv
ETL completed for Houston, TX

Fetching properties for Dallas, TX
Clean CSV saved: .../data/transformed/properties_data_Dallas_TX.csv
Loaded 275 rows into properties_data (append) from .../Dallas_TX.csv
ETL completed for Dallas, TX

Pipeline finished
```

---

## 12) Notes on Usage and Limits

* Free API plans often limit monthly requests. Avoid unnecessary reruns during development.
* Field names in the CSV depend on the API response shape for your chosen endpoint and parameters.
* City names with spaces are handled in filenames; raw uses underscores, transformed removes spaces in the city token.

---

## 13) Automated Scheduling with Windows Task Scheduler

Automate daily execution using Windows Task Scheduler to keep PostgreSQL refreshed without manual intervention.

### 13.1 Create a batch file

Create `run_etl.bat` in the project root and adjust paths as needed:

```bat
@echo off
echo Running Real Estate ETL Pipeline...
cd "C:\Users\Labee\onedrive\desktop\Projects\REal-State-Project"
call my-env\Scripts\activate
python src\main.py
pause
```

Optional: log output to a file:

```bat
@echo off
cd "C:\Users\Labee\onedrive\desktop\Projects\REal-State-Project"
call my-env\Scripts\activate
python src\main.py >> logs\etl_run.log 2>&1
```

Create logs folder once:

```bash
mkdir logs
```

### 13.2 Schedule the task

1. Open Task Scheduler → Create Basic Task
2. Name: Real Estate ETL Pipeline
3. Trigger: Daily at the desired time
4. Action: Start a Program → select `run_etl.bat`
5. Enable “Run whether user is logged on or not”
6. Enable “Run with highest privileges”
7. Save

### 13.3 Validate

* New files appear in `data/raw` and `data/transformed`
* PostgreSQL row count increases:

```sql
SELECT COUNT(*) FROM properties_data;
```

If it runs manually but not from Task Scheduler, use absolute paths or call Python directly:

```bat
"C:\Users\Labee\onedrive\desktop\Projects\REal-State-Project\my-env\Scripts\python.exe" src\main.py
```

---

## 14) Challenges & Learning

* Managing environment paths so file outputs resolve correctly regardless of the working directory. Solved by anchoring paths to `Path(__file__).resolve().parents[1]`.
* Ensuring secret safety by using `.env` and excluding it via `.gitignore`.
* Normalizing API fields into a consistent schema that downstream consumers can depend on.
* Handling CSV directory creation before writes to avoid `FileNotFoundError`.

---

## 15) Future Enhancements

* Add pagination and rate limiting handling for larger result sets.
* Introduce structured logging with log levels and rotating files.
* Add data quality checks and schema validation before load.
* Parameterize database connection via `.env`.
* Add a GitHub Action for linting and static checks without calling the API.
* Provide Docker Compose for PostgreSQL and a reproducible dev environment.

---

## 16) License and Contact

License: MIT (or your preferred license)

Contact:

* GitHub: `nadiamudassar`
* Repository: `real-estate-etl-pipeline`
* Summary: This project implements a complete ETL pipeline that collects real estate property listing data from the RentCast API, transforms and standardizes the dataset, and loads the final records into a PostgreSQL database for analytics.

---