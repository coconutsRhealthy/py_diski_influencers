from datetime import datetime
from db.db_connection import get_database_connection

def get_records(table: str, inserted_after: datetime, post_date_after: datetime = None):
    allowed_tables = {"instagram", "tiktok"}
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name {table!r}. "
                         f"Must be one of {allowed_tables}")

    base_query = f"""
    SELECT id, influencer_name, caption, post_url, post_date, inserted_at, ai_analysis, ai_analysis_time
    FROM `{table}`
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

    one_day_ago = datetime.now() - timedelta(days=1)

    # Instagram example
    insta_records = get_records("instagram", one_day_ago, one_day_ago)
    print("\nInstagram records:")
    pprint.pprint(insta_records)

    # TikTok example
    tiktok_records = get_records("tiktok", one_day_ago)
    print("\nTikTok records:")
    pprint.pprint(tiktok_records)
