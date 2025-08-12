from datetime import datetime
import json

from ai.identify_canonical import normalize_webshops
from db.db_insert_ai_canonical import insert_ai_canonical
from util.canonical_data_collector import get_webshops_to_be_identified, get_canonical_company_names


def run_pipeline(since_datetime: datetime, canonical_file_path: str):
    # Step 1: Get unknown webshops from DB
    unknown_webshops = get_webshops_to_be_identified(since_datetime)
    print(f"Found {len(unknown_webshops)} unknown webshop(s) since {since_datetime.date()}")

    # Step 2: Load known canonical webshop names from file
    known_webshop_keys = get_canonical_company_names(canonical_file_path)
    print(f"Loaded {len(known_webshop_keys)} canonical webshop name(s) from JSON file")

    # Step 3: Map unknown webshops to canonical names
    mapping = normalize_webshops(unknown_webshops, known_webshop_keys)
    print(f"Created mapping for {len(mapping)} webshops")

    # Debug print mapping (optional)
    print(json.dumps(mapping, indent=2, ensure_ascii=False))

    # Step 4: Insert into DB
    for ai_spotted_webshop_name, canonical in mapping.items():
        insert_ai_canonical(ai_spotted_webshop_name, canonical, since_datetime)
        print(f"Inserted canonical '{canonical}' for webshop '{ai_spotted_webshop_name}'")


if __name__ == "__main__":
    cutoff_date = datetime(2025, 8, 11)
    canonical_json_path = "/Users/lennartmac/Documents/Projects/diski-input-insta/src/assets/discounts.json"
    run_pipeline(cutoff_date, canonical_json_path)
