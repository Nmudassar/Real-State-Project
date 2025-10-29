

# Real Estate ETL Project

This project extracts property listing data from the **RentCast API** using Python and saves the results locally for analysis. It covers ETL fundamentals with a focus on the **Extract** phase.

---

##  Learning Objectives

By the end of this session, we should:

1. Create a Python Environment and understand what it is
2. Understand what ETL means and what extraction is
3. Know how to call an API in Python
4. Successfully fetch property data from RentCast (API)
5. Save the data locally as CSV or JSON
6. Understand the overall project structure

---

##  Project Structure

```
real_estate_project/
├─ README.md
├─ requirements.txt
├─ .env
├─ data/
│  └─ raw/
└─ src/
   ├─ config.py
   └─ main.py
```

---

## 🔧 Setup

### 1) Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2) Install dependencies

Create `requirements.txt` with:

```txt
requests
python-dotenv
pandas
```

Then install:

```bash
pip install -r requirements.txt
```

### 3) Add environment variables

Create `.env` in the project root:

```env
API_KEY=your_rentcast_api_key_here
BASE_URL=https://api.rentcast.io/v1/listings
```

---

## 🧩 Code

### `src/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

if not API_KEY:
    raise ValueError("Missing API_KEY in .env")
if not BASE_URL:
    raise ValueError("Missing BASE_URL in .env")
```

### `src/main.py`

```python
import os
import json
import requests
import pandas as pd
from pathlib import Path
from src.config import API_KEY, BASE_URL

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def extract_properties(city: str, state: str) -> dict:
    """Call RentCast API for a city/state and return JSON data."""
    headers = {
        "accept": "application/json",
        "X-Api-Key": API_KEY
    }
    params = {
        "city": city,
        "state": state
    }
    print(f"Fetching properties for {city}, {state} ...")
    resp = requests.get(BASE_URL, headers=headers, params=params, timeout=60)

    if resp.status_code != 200:
        raise RuntimeError(
            f"API error for {city},{state}: {resp.status_code} -> {resp.text[:200]}"
        )
    return resp.json()

def save_json(data: dict, city: str, state: str) -> Path:
    """Save raw JSON to data/raw/."""
    safe_city = city.replace(" ", "_")
    fname = RAW_DIR / f"properties_data_{safe_city}_{state}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return fname

def save_csv(data: dict, city: str, state: str) -> Path:
    """Save results to CSV if records exist."""
    # RentCast typically returns a list of listings; handle dict/list safely.
    records = data if isinstance(data, list) else data.get("data") or data.get("results") or []
    if not isinstance(records, list):
        records = [records]

    df = pd.DataFrame(records)
    safe_city = city.replace(" ", "_")
    fname = RAW_DIR / f"properties_data_{safe_city}_{state}.csv"
    df.to_csv(fname, index=False)
    return fname

if __name__ == "__main__":
    cities = [
        ("San Antonio", "TX"),
        ("Houston", "TX"),
        ("Dallas", "TX"),
    ]

    for city, state in cities:
        try:
            data = extract_properties(city, state)
            jpath = save_json(data, city, state)
            cpath = save_csv(data, city, state)
            print(f"Saved: {jpath} and {cpath}")
        except Exception as e:
            print(f"Failed for {city}, {state}: {e}")

    print("Extraction completed for all cities.")
```

---

##  Run

```bash
python src/main.py
```

Output files will appear in `data/raw/` as both `.json` and `.csv`.

---

## Notes

* API free plans often limit monthly requests. Avoid unnecessary reruns.
* Field names in the CSV depend on the API response shape for your chosen endpoint and params.
* If your city names contain spaces, they are safely handled in filenames.


