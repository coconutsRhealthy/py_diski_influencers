import json
import re
from pathlib import Path
from datetime import datetime

from ai.identify_canonical import normalize_webshops
from db.db_access import get_records_since_datetime

def get_webshops_to_be_identified(inserted_after: datetime):
    table = "instagram"
    records = get_records_since_datetime(table, inserted_after)

    webshops = set()

    for record in records:
        ai_analysis = record.get('ai_analysis')

        if not ai_analysis:
            continue  # NULL or empty

        # Parse JSON if it's a string
        if isinstance(ai_analysis, str):
            try:
                ai_analysis = json.loads(ai_analysis)
            except json.JSONDecodeError:
                continue  # skip bad JSON

        if isinstance(ai_analysis, list):
            for entry in ai_analysis:
                if isinstance(entry, dict):
                    webshop_name = entry.get("webshop")
                    if webshop_name:
                        webshops.add(webshop_name)

    return list(webshops)


def get_canonical_company_names(file_path: str) -> list:
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    company_names = set()
    for line in data:
        if not line or not isinstance(line, str):
            continue
        # Take text before the first comma
        company = line.split(",", 1)[0].strip()
        # Remove anything in parentheses
        company = re.sub(r"\s*\(.*?\)", "", company)
        # Normalize spacing
        company = company.strip()
        if company:
            company_names.add(company)

    return sorted(company_names)

if __name__ == "__main__":
    cutoff_date = datetime(2025, 8, 1)
    result = get_webshops_to_be_identified(cutoff_date)
    #print(result)
    #print(f"Number of webshops to be identified: {len(result)}")

    canonical_names = get_canonical_company_names("/Users/lennartmac/Documents/Projects/diski-input-insta/src/assets/discounts.json")
    #print(canonical_names)
    #print(f"Number of unique canonical company names: {len(canonical_names)}")

    mapping_result = normalize_webshops(result, canonical_names)
    sorted_mapping_result = dict(sorted(mapping_result.items()))
    print(json.dumps(sorted_mapping_result, indent=2, ensure_ascii=False))