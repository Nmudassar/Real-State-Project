# PrimeSquare Properties Ltd — Real Estate ETL Pipeline

A production-style ETL (Extract, Transform, Load) pipeline that collects real estate property listings from the RentCast API, standardizes the data model, and loads analytics-ready records into PostgreSQL. Designed for clarity, reproducibility, and portfolio presentation.

---

## Table of Contents

1. Project Overview
2. Architecture Diagram
3. Skills Demonstrated
4. Tech Stack
5. File/Folder Structure
6. Setup and Configuration
7. End-to-End Run
8. Code (Extract, Transform, Load, Orchestration)
9. Before & After Data Example
10. SQL Query Examples
11. Pipeline Execution Output
12. Challenges & Learning
13. Future Enhancements
14. License and Contact

---

## 1) Project Overview

This project implements a complete ETL pipeline to automate the ingestion of property listing data from the RentCast API for three Texas cities (San Antonio, Houston, Dallas). Raw JSON is normalized into a consistent tabular schema and loaded into a PostgreSQL table for analytics and dashboards. The pipeline emphasizes secure secret handling, robust paths, and repeatable runs.

---

## 2) Architecture Diagram

```
             +-------------------+
             |   Scheduler/CLI   |
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
               Analytics & BI (SQL/Power BI)
```

If you maintain visuals, place a PNG at `assets/dataflow.png` and reference it here.

---

## 3) Skills Demonstrated

* API integration and request handling with authentication
* Data normalization and schema standardization
* Robust file I/O and path management for cross-environment runs
* PostgreSQL loading using SQLAlchemy
* Secret management with `.env` and `python-dotenv`
* GitHub-ready project structure and documentation

---

## 4) Tech Stack

* Python 3.10+
* Requests, pandas, SQLAlchemy, psycopg2-binary, python-dotenv
* PostgreSQL
* Git/GitHub
* (Optional) Power BI or other BI tools for visualization

---

## 5) File/Folder Structure

```
real-estate-etl-pipeline/
├─ assets/                    # (optional) diagrams, screenshots
├─ data/
│  ├─ raw/                    # raw JSON from API (ignored by Git)
│  └─ transformed/            # cleaned CSVs (ignored by Git)
├─ src/
│  ├─ __init__.py
│  ├─ config.py               # loads API key, base URL from .env
│  ├─ extract.py              # API calls, writes raw JSON
│  ├─ transform2.py           # JSON -> standardized CSV
│  └─ load2.py                # CSV -> PostgreSQL table
├─ .env                       # API secrets (ignored by Git)
├─ .gitignore
├─ requirements.txt
├─ README.md
└─ run.py                     # optional one-city runner for quick checks
```

Recommended `.gitignore`:

```gitignore
# venv
my-env/
.venv/
venv/

# env and secrets
.env

# python cache
__pycache__/
*/__pycache__/
*.pyc
*.pyo
*.pyd

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Data artifacts```

---

## 6) Setup and Configuration

### 6.1 Create and activate a virtual environment

```bash
python -m venv my-env
# Windows
my-env\Scripts\activate
# macOS/Linux
# source my-env/bin/activate
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

### 6.3 Obtain and configure API credentials

1. Visit [https://www.rentcast.io/api](https://www.rentcast.io/api) and create an account.
2. Generate an API key from the API Dashboard.
3. Create `.env` in the project root:

```env
API_KEY=your_rentcast_api_key_here
BASE_URL=https://api.rentcast.io/v1/properties
```

---

## 7) End-to-End Run

Run the full pipeline (extract → transform → load):

```bash
python src/main.py
```

Expected outputs:

* Raw JSON files in `data/raw/`
* Clean CSV files in `data/transformed/`
* Records loaded into PostgreSQL table `properties_data`

---

## 8) Code

### 8.1 `src/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.rentcast.io/v1/properties")

if not API_KEY:
    raise RuntimeError("API_KEY missing. Add it to your .env")
```

### 8.2 `src/extract.py`

```python
import json
from pathlib import Path
import requests
from src.config import API_KEY, BASE_URL

# Save into project-root/data/raw regardless of where you run
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

def extract_properties(city: str, state: str):
    headers = {"Accept": "application/json", "X-Api-Key": API_KEY}
    params = {"city": city, "state": state}
    print(f"Fetching properties for {city}, {state}")
    r = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    safe_city = city.replace(" ", "_")
    out_path = RAW_DIR / f"properties_data_{safe_city}_{state}.json"
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(out_path)

if __name__ == "__main__":
    print(extract_properties("San Antonio", "TX"))
```

### 8.3 `src/transform2.py`

```python
import json
from pathlib import Path
import pandas as pd

TRANSFORM_DIR = Path(__file__).resolve().parents[1] / "data" / "transformed"
TRANSFORM_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    'id', 'formattedAddress', 'city', 'state', 'stateFips', 'zipCode',
    'county', 'countyFips', 'latitude', 'longitude', 'propertyType',
    'bedrooms', 'bathrooms', 'squareFootage', 'yearBuilt'
]

RENAME = {
    'formattedAddress': 'address',
    'stateFips': 'state_fips',
    'zipCode': 'zip_code',
    'countyFips': 'county_fips',
    'propertyType': 'property_type',
    'squareFootage': 'square_footage',
    'yearBuilt': 'year_built',
}

def transform(file_path: str, city: str, state: str):
    data = json.loads(Path(file_path).read_text(encoding="utf-8"))
    df = pd.json_normalize(data)

    # If the API returns different shapes, adjust the column selection here
    df = df[COLUMNS]
    df = df.rename(columns=RENAME)

    safe_city = city.replace(" ", "")
    out_path = TRANSFORM_DIR / f"properties_data_{safe_city}_{state}.csv"
    df.to_csv(out_path, index=False)
    print(f"Clean CSV saved: {out_path}")
    return str(out_path)
```

### 8.4 `src/load2.py`

```python
from sqlalchemy import create_engine
import pandas as pd

# Adjust for your environment
ENGINE = create_engine("postgresql+psycopg2://postgres@127.0.0.1:5432/primesquare_prod")

TABLE = "properties_data"

def load_t0_db(csv_path: str, mode: str = "append"):
    df = pd.read_csv(csv_path)
    df.to_sql(TABLE, ENGINE, if_exists=mode, index=False)
    print(f"Loaded {len(df)} rows into {TABLE} ({mode}) from {csv_path}")
```

### 8.5 `src/main.py`

```python
from pathlib import Path
from extract import extract_properties
from transform2 import transform
from load2 import load_t0_db

def run_pipeline():
    print("Starting ETL pipeline run")
    (Path(__file__).resolve().parents[1] / "data" / "transformed").mkdir(parents=True, exist_ok=True)

    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX"),
    ]

    first = True
    for city, state in cities:
        raw_file = extract_properties(city, state)
        clean_file = transform(raw_file, city, state)
        load_t0_db(clean_file, "replace" if first else "append")
        first = False
        print(f"ETL completed for {city}, {state}")

    print("Pipeline finished")

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

## 12) Challenges & Learning

* Managing environment paths so that file outputs resolve correctly regardless of the working directory. Solved by anchoring paths to `Path(__file__).resolve().parents[1]`.
* Ensuring secret safety by using `.env` and excluding it via `.gitignore`.
* Normalizing API fields into a consistent schema that downstream consumers can depend on.
* Handling CSV directory creation before writes to avoid `FileNotFoundError`.

---

## 13) Future Enhancements

* Add pagination and rate limiting handling for larger result sets.
* Introduce structured logging with log levels and rotating files.
* Add data quality checks and schema validation before load.
* Parameterize database connection via `.env`.
* Add a GitHub Action for linting and static checks without calling the API.
* Provide Docker Compose for PostgreSQL and a reproducible dev environment.

---

## 14) License and Contact

License: MIT (or your preferred license)

Contact:

* GitHub: `nadiamudassar`
* Project: `real-estate-etl-pipeline`
* Summary: This project implements a complete ETL pipeline that collects real estate property listing data from the RentCast API, transforms and standardizes the dataset, and loads the final records into a PostgreSQL database for analytics.

---


