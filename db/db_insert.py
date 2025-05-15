from db.db_connection import get_database_connection

def insert_records(records):
    with get_database_connection() as conn:
        cursor = conn.cursor()

        insert_query = """
            INSERT IGNORE INTO instagram (influencer_name, caption, post_url, post_date)
            VALUES (%s, %s, %s, %s);
        """

        values = [
            (
                record['influencer_name'],
                record['caption'],
                record['post_url'],
                record['post_date']
            )
            for record in records
        ]

        cursor.executemany(insert_query, values)
        conn.commit()

        print(f"Tried inserting {len(records)} records. Duplicate entries were ignored.")