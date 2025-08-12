from db.db_access import get_records_since_datetime
from datetime import datetime
import json


def print_unique_discount_records_since_datetime2(table: str, inserted_after: datetime):
    records = get_records_since_datetime(table, inserted_after)

    seen = set()
    count = 0

    for record in records:
        ai_analysis = record.get('ai_analysis')
        ai_canonical = record.get('ai_canonical') or "UNKNOWN"

        if not ai_analysis:
            continue

        try:
            ai_analysis = json.loads(ai_analysis) if isinstance(ai_analysis, str) else ai_analysis
        except Exception:
            continue

        if not isinstance(ai_analysis, list):
            continue

        influencer_name = record.get('influencer_name', 'UNKNOWN')
        inserted_at = record.get('inserted_at')
        if not inserted_at:
            continue

        # Format inserted_at as MM-DD
        formatted_date = inserted_at.strftime("%m-%d")

        for entry in ai_analysis:
            if not isinstance(entry, dict):
                continue

            discount_code = entry.get('code', "N/A")
            discount_percentage = entry.get('percentage', "N/A")

            line = f'"{ai_canonical}, {discount_code}, {discount_percentage}, {influencer_name}, {formatted_date}",'

            if line not in seen:
                print(line)
                seen.add(line)
                count += 1

    print(f"\nPrinted {count} unique discount records.")



if __name__ == "__main__":
    print_unique_discount_records_since_datetime2("instagram_canonical", datetime(2025, 8, 11))