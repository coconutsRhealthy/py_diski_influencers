import json
from datetime import datetime
from db.db_connection import get_database_connection

def insert_ai_analysis(post_url: str, caption: str, ai_analysis, table: str):
    allowed_tables = {"instagram", "tiktok"}
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name: {table!r}. Must be one of {allowed_tables}")

    ai_analysis_time = datetime.now()
    ai_analysis_json = json.dumps(ai_analysis, ensure_ascii=False)

    update_sql = f"""
    UPDATE {table}
    SET ai_analysis = %s,
        ai_analysis_time = %s
    WHERE post_url = %s
      AND LEFT(caption, 255) = %s
    """

    with get_database_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(update_sql, (ai_analysis_json, ai_analysis_time, post_url, caption[:255]))
        conn.commit()
        cursor.close()
        print(f"[{table}] Updated AI analysis for post_url: {post_url} and caption prefix")

