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
        if '(' in canonical:
            canonical = canonical.split('(')[0].strip()

        key = (canonical.lower(), code.lower())

        # Keep the first occurrence (newest date) only
        if key not in discounts_map:
            discounts_map[key] = date

    return discounts_map

def print_unique_discount_records_since_datetime(table: str, inserted_after: datetime, print_urls_end_of_line: bool = False):
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

        # Check if this record has multiple entries in ai_analysis
        multi_prefix = "MULTI__" if len(ai_analysis) > 1 else ""

        for entry in ai_analysis:
            if not isinstance(entry, dict):
                continue

            discount_code = entry.get('code', "N/A")
            discount_percentage = entry.get('percentage', "N/A")

            lookup_key = ((ai_canonical or "unknown").lower(), (discount_code or "unknown").lower())

            display_influencer_name = influencer_name
            if table == "tiktok":
                display_influencer_name += "_tiktok"

            line = f'{multi_prefix}"{ai_canonical}, {discount_code}, {discount_percentage}, {display_influencer_name}, {formatted_date}",'

            if lookup_key in discounts_map:
                discount_date = discounts_map[lookup_key]
                line = f'...{line}..........{discount_date}'

            if print_urls_end_of_line:
                post_url = record.get('post_url', '')
                if post_url:
                    line += f'    {post_url}'

            if line not in seen:
                print(line)
                seen.add(line)
                count += 1

    print(f"\nPrinted {count} unique discount records.")

if __name__ == "__main__":
    print_unique_discount_records_since_datetime("tiktok", datetime(2025, 8, 13), True)
