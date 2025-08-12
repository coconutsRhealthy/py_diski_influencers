from datetime import date, datetime
from typing import Optional, List, Dict, Union
from db.db_connection import get_database_connection

def get_records_for_date(table: str, inserted_at: date, post_date_after: Optional[datetime] = None) -> List[Dict]:
    _validate_table(table)
    if not isinstance(inserted_at, date) or isinstance(inserted_at, datetime):
        raise TypeError("'inserted_at' must be a date object (not datetime)")

    where_clause = "DATE(inserted_at) = %s"
    params: List[Union[date, datetime]] = [inserted_at]

    if post_date_after:
        where_clause += " AND post_date > %s"
        params.append(post_date_after)

    return _execute_query(table, where_clause, params)

def get_records_since_datetime(table: str, inserted_after: datetime, post_date_after: Optional[datetime] = None) -> List[Dict]:
    _validate_table(table)
    if not isinstance(inserted_after, datetime):
        raise TypeError("'inserted_after' must be a datetime object")

    where_clause = "inserted_at > %s"
    params: List[Union[date, datetime]] = [inserted_after]

    if post_date_after:
        where_clause += " AND post_date > %s"
        params.append(post_date_after)

    return _execute_query(table, where_clause, params)

def _execute_query(table: str, where_clause: str, params: List[Union[date, datetime]]) -> List[Dict]:
    query = f"""
    SELECT id, influencer_name, caption, post_url, post_date, inserted_at, ai_analysis, ai_canonical, ai_analysis_time
    FROM `{table}`
    WHERE {where_clause}
    ORDER BY inserted_at ASC
    """
    with get_database_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        return results

def _validate_table(table: str):
    allowed_tables = {"instagram", "tiktok"}
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name {table!r}. Must be one of {allowed_tables}")

if __name__ == "__main__":
    import pprint
    from datetime import datetime, timedelta

    inserted_at = date(2025, 5, 21)
    post_date_after = datetime.now() - timedelta(days=200)
    inserted_after = datetime(2025, 5, 21, 14, 11, 42)

    insta_records = get_records_for_date("instagram", inserted_at, post_date_after)
    print("\nInstagram records:")
    pprint.pprint(insta_records)
