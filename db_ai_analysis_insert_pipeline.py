from datetime import datetime, timedelta
import json
from db.db_access import get_instagram_records
from ai.extract_discount_codes import extract_discount_codes
from db.db_insert_ai_analysis import insert_ai_analysis

def run_pipeline(inserted_after: datetime, post_date_after: datetime = None):
    records = get_instagram_records(inserted_after, post_date_after)

    print(f"Found {len(records)} records to process...")

    for record in records:
        post_url = record['post_url']
        caption = record['caption'] or ""
        ai_analysis = record.get('ai_analysis')  # or record['ai_analysis']

        #Proceed only if ai_analysis is NULL / None
        if ai_analysis is not None:
            print(f"Skipping {post_url} because AI analysis already exists.")
            continue

        print(f"\nProcessing post_url: {post_url}")

        # Call your AI extraction
        ai_result = extract_discount_codes(caption)

        if ai_result is None:
            print("Warning: AI extraction returned None. Skipping insert.")
            continue

        # Convert the AI result back to JSON string for storage
        ai_result_json = json.dumps(ai_result, ensure_ascii=False)

        # Insert AI analysis into the database
        insert_ai_analysis(post_url, caption, ai_result_json)

        print("Inserted AI analysis.")

if __name__ == "__main__":
    # Example: run the pipeline for records inserted in the last day,
    # optionally filter by post_date as well
    inserted_after = datetime.now() - timedelta(days=2)
    post_date_after = datetime.now() - timedelta(days=2)

    run_pipeline(inserted_after, post_date_after)
