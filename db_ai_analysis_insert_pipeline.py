from datetime import datetime, timedelta
from db.db_access import get_records
from ai.extract_discount_codes import extract_discount_codes
from db.db_insert_ai_analysis import insert_ai_analysis

def run_pipeline(table: str, inserted_after: datetime, post_date_after: datetime = None):
    records = get_records(table, inserted_after, post_date_after)

    print(f"[{table.upper()}] Found {len(records)} records to process...")

    for record in records:
        post_url = record['post_url']
        caption = record['caption'] or ""
        ai_analysis = record.get('ai_analysis')

        if ai_analysis is not None:
            print(f"Skipping {post_url} (already analyzed).")
            continue

        print(f"\nProcessing {post_url}...")

        # Run AI extraction
        ai_result = extract_discount_codes(caption)

        if ai_result is None:
            print("Warning: AI extraction returned None. Skipping insert.")
            continue

        # Insert into the correct table
        insert_ai_analysis(post_url, caption, ai_result, table=table)
        print("Inserted AI analysis.")

if __name__ == "__main__":
    inserted_after = datetime.now() - timedelta(days=2)
    post_date_after = datetime.now() - timedelta(days=2)

    # Example runs
    run_pipeline("instagram", inserted_after, post_date_after)
    run_pipeline("tiktok", inserted_after, post_date_after)