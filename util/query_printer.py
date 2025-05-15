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
        if not ai_json_str:
            continue

        try:
            intermediate = json.loads(ai_json_str)  # first load, gives a string again
            if isinstance(intermediate, str):
                ai_data = json.loads(intermediate)  # second load, now it's list/dict
            else:
                ai_data = intermediate

            #print(type(ai_data))
        except json.JSONDecodeError:
            # Skip invalid JSON data
            continue

        # ai_data should be a list of discount code dicts
        if isinstance(ai_data, list):
            for entry in ai_data:
                # Create a unique key based on webshop and code
                key = (entry.get('webshop'), entry.get('code'))
                if key not in seen:
                    seen.add(key)
                    combined_entries.append(entry)
        else:
            # If it's not a list, ignore or handle differently if needed
            continue

    # Print combined unique JSON array
    print(json.dumps(combined_entries, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Example: print all with ai_analysis inserted in last 3 days
    inserted_after = datetime.now() - timedelta(days=2)
    combine_and_print_unique_ai_analysis(inserted_after, inserted_after)
