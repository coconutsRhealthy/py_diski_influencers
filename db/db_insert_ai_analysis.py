import json
from datetime import datetime
from db.db_connection import get_database_connection

def insert_ai_analysis(post_url, caption, ai_analysis):
    ai_analysis_time = datetime.now()
    ai_analysis_json = json.dumps(ai_analysis, ensure_ascii=False)

    update_sql = """
    UPDATE instagram
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
        print(f"Updated AI analysis for post_url: {post_url} and caption prefix")

# Example usage:
if __name__ == "__main__":
    test_caption = "testcaption"
    test_post_url = "https://instagram.com/p/abc123"
    test_ai_analysis = [
        {
            "webshop": "CoolShop",
            "code": "SAVE20",
            "percentage": 20
        }
    ]

    insert_ai_analysis(test_post_url, test_caption, test_ai_analysis)
