from datetime import date, datetime, timedelta
from db.db_access import get_records
from ai.extract_discount_codes import extract_discount_codes
from db.db_insert_ai_analysis import insert_ai_analysis

def run_pipeline(table: str, inserted_at: date, post_date_after: datetime = None):
    records = get_records(table, inserted_at, post_date_after)

    print(f"[{table.upper()}] Found {len(records)} records to process...")

    insert_count = 0

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
        insert_count += 1
        print(f"Inserted AI analysis. Total inserted so far: {insert_count}")

if __name__ == "__main__":
    inserted_at = date(2025, 5, 16)
    post_date_after = datetime.now() - timedelta(days=3)

    # Example runs
    run_pipeline("instagram", inserted_at, post_date_after)
    run_pipeline("tiktok", inserted_at, post_date_after)