import json
from db.db_access import get_records_since_datetime
from datetime import datetime

DISCOUNTS_JSON_PATH = "/Users/lennartmac/Documents/Projects/diski-input-insta/src/assets/discounts.json"

def load_discounts_map():
    with open(DISCOUNTS_JSON_PATH, 'r', encoding='utf-8') as f:
        discounts_lines = json.load(f)
    discounts_map = {}
    for line in discounts_lines:
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 3:
            continue
        canonical = parts[0]
        code = parts[1]
        date = parts[-1]  # last part is date

        # Strip possible extra parentheses or info in canonical (like "zalando (11 aug)")
        # Just keep the canonical name before any parentheses:
        if '(' in canonical:
            canonical = canonical.split('(')[0].strip()

        discounts_map[(canonical.lower(), code.lower())] = date
    return discounts_map

def print_unique_discount_records_since_datetime_with_flag(table: str, inserted_after: datetime):
    discounts_map = load_discounts_map()
    records = get_records_since_datetime(table, inserted_after)

    seen = set()
    count = 0

    for record in records:
        ai_analysis = record.get('ai_analysis')
        ai_canonical = record.get('ai_canonical')
        if not ai_canonical or ai_canonical.upper() == "UNKNOWN":
            webshop_name = None
            try:
                if isinstance(ai_analysis, str):
                    ai_analysis_json = json.loads(ai_analysis)
                else:
                    ai_analysis_json = ai_analysis
            except Exception:
                ai_analysis_json = None
            if isinstance(ai_analysis_json, list):
                for entry in ai_analysis_json:
                    if isinstance(entry, dict) and entry.get("webshop"):
                        webshop_name = entry.get("webshop").upper()
                        break
            ai_canonical = webshop_name or "UNKNOWN"

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

        formatted_date = inserted_at.strftime("%m-%d")

        for entry in ai_analysis:
            if not isinstance(entry, dict):
                continue

            discount_code = entry.get('code', "N/A")
            discount_percentage = entry.get('percentage', "N/A")

            lookup_key = ((ai_canonical or "unknown").lower(), (discount_code or "unknown").lower())

            line = f'"{ai_canonical}, {discount_code}, {discount_percentage}, {influencer_name}, {formatted_date}",'

            if lookup_key in discounts_map:
                discount_date = discounts_map[lookup_key]
                line = f'...{line}..........{discount_date}'

            if line not in seen:
                print(line)
                seen.add(line)
                count += 1

    print(f"\nPrinted {count} unique discount records.")

if __name__ == "__main__":
    print_unique_discount_records_since_datetime_with_flag("instagram", datetime(2025, 8, 11))
