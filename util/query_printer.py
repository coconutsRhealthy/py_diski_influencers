from db.db_access import get_instagram_records
from datetime import datetime, timedelta
import json
import textwrap

def print_records_with_ai_analysis(inserted_after: datetime, post_date_after: datetime = None):
    records = get_instagram_records(inserted_after, post_date_after)

    # Filter records where ai_analysis is NOT None
    filtered = [r for r in records if r.get('ai_analysis') is not None]

    print(f"Found {len(filtered)} records with AI analysis.\n")

    for record in filtered:
        print("Caption:")
        wrapped_caption = textwrap.fill(record['caption'], width=150)
        print(wrapped_caption)
        print("\nPost URL:")
        print(record['post_url'])
        print("\nAI Analysis JSON:")
        # Pretty print the JSON string from ai_analysis column
        try:
            ai_json = json.loads(record['ai_analysis'])
            print(json.dumps(ai_json, indent=2, ensure_ascii=False))
        except Exception:
            # If for some reason it's not valid JSON, print raw text
            print(record['ai_analysis'])
        print("\n" + "="*50 + "\n")

def combine_and_print_unique_ai_analysis(inserted_after: datetime, post_date_after: datetime = None):
    records = get_instagram_records(inserted_after, post_date_after)

    combined_entries = []
    seen = set()  # To track unique (webshop, code) pairs

    for record in records:
        ai_json_str = record.get('ai_analysis')
        influencer_name = record.get('influencer_name', None)  # get influencer name from record

        if not ai_json_str:
            continue

        try:
            intermediate = json.loads(ai_json_str)  # first load, gives a string again
            if isinstance(intermediate, str):
                ai_data = json.loads(intermediate)  # second load, now it's list/dict
            else:
                ai_data = intermediate
        except json.JSONDecodeError:
            continue

        if isinstance(ai_data, list):
            for entry in ai_data:
                key = (entry.get('webshop'), entry.get('code'))
                if key not in seen:
                    seen.add(key)
                    # Add influencer name to the discount code entry
                    entry_with_user = dict(entry)  # make a copy to avoid mutating original
                    entry_with_user['influencer_name'] = influencer_name
                    combined_entries.append(entry_with_user)
        else:
            continue

    #print(json.dumps(combined_entries, indent=2, ensure_ascii=False))
    return combined_entries


def print_json_as_csv_style_oud(data):
    """
    Prints the provided list of discount code dicts in CSV-style lines:
    "webshop, code, percentage, influencer_name, MM-DD"
    """
    today_str = datetime.now().strftime("%m-%d")

    for entry in data:
        webshop = entry.get('webshop', '')
        code = entry.get('code', '')
        percentage = entry.get('percentage', '')
        influencer = entry.get('influencer_name', '')

        line = f'"{webshop}, {code}, {percentage}, {influencer}, {today_str}"'
        print(line)

def print_json_as_csv_style(combined_entries):
    from datetime import datetime
    today_str = datetime.now().strftime("%m-%d")

    for entry in combined_entries:
        webshop = entry.get('webshop', '')
        code = entry.get('code', '')
        percentage_str = str(entry.get('percentage')) if entry.get('percentage') is not None else ''
        influencer_name = entry.get('influencer_name', '')
        print(f'"{webshop}, {code}, {percentage_str}, {influencer_name}, {today_str}"')

if __name__ == "__main__":
    # Example: print all with ai_analysis inserted in last 3 days
    inserted_after = datetime.now() - timedelta(days=3)
    combined_entries = combine_and_print_unique_ai_analysis(inserted_after, inserted_after)
    print_json_as_csv_style(combined_entries)
