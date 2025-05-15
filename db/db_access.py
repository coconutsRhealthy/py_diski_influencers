from datetime import datetime
from db.db_connection import get_database_connection

def get_instagram_records(inserted_after: datetime, post_date_after: datetime = None):
    base_query = """
    SELECT id, influencer_name, caption, post_url, post_date, inserted_at, ai_analysis, ai_analysis_time
    FROM instagram
    WHERE inserted_at > %s
    """

    params = [inserted_after]

    if post_date_after:
        base_query += " AND post_date > %s"
        params.append(post_date_after)

    base_query += " ORDER BY inserted_at ASC"

    with get_database_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(base_query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        return results

if __name__ == "__main__":
    import pprint
    from datetime import datetime, timedelta

    one_day_ago = datetime.now() - timedelta(days=2)
    records_with_post_date = get_instagram_records(one_day_ago, one_day_ago)

    print("\nRecords filtered by inserted_at AND post_date:")
    pprint.pprint(records_with_post_date)
