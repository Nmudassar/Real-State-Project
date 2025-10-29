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

    
    