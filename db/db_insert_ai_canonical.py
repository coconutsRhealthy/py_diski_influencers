import json
from datetime import datetime
from db.db_connection import get_database_connection

def insert_ai_canonical(ai_spotted_webshop_name: str, canonical: str, since_datetime: datetime):
    with get_database_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Fetch records after the cutoff date
        select_sql = """
            SELECT id, ai_analysis
            FROM instagram_canonical
            WHERE inserted_at >= %s
        """
        cursor.execute(select_sql, (since_datetime,))
        records = cursor.fetchall()

        update_sql = """
            UPDATE instagram_canonical
            SET ai_canonical = %s
            WHERE id = %s
        """

        updated_count = 0

        for record in records:
            ai_analysis = record.get('ai_analysis')

            if not ai_analysis:
                continue

            # Parse JSON if it's a string
            if isinstance(ai_analysis, str):
                try:
                    ai_analysis = json.loads(ai_analysis)
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON

            if isinstance(ai_analysis, list):
                for entry in ai_analysis:
                    if isinstance(entry, dict):
                        webshop_name = entry.get("webshop")
                        if webshop_name == ai_spotted_webshop_name:
                            cursor.execute(update_sql, (canonical, record['id']))
                            updated_count += 1
                            break  # Avoid double-updating same row

        conn.commit()

    print(f"Updated {updated_count} rows with ai_canonical = '{canonical}'")


if __name__ == "__main__":
    # Example usage
    cutoff = datetime(2025, 8, 1)
    insert_ai_canonical(
        ai_spotted_webshop_name="aybl",
        canonical="HENK",
        since_datetime=cutoff
    )
