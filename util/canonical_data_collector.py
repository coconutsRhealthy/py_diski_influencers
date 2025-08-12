import json
from datetime import datetime
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

        # Case: direct dict
        if isinstance(ai_analysis, dict):
            webshop_name = ai_analysis.get("webshop")
            if webshop_name:
                webshops.add(webshop_name)

        # Case: list of dicts
        elif isinstance(ai_analysis, list):
            for entry in ai_analysis:
                if isinstance(entry, dict):
                    webshop_name = entry.get("webshop")
                    if webshop_name:
                        webshops.add(webshop_name)

    return list(webshops)

if __name__ == "__main__":
    cutoff_date = datetime(2025, 8, 10)
    result = get_webshops_to_be_identified(cutoff_date)
    print(result)
