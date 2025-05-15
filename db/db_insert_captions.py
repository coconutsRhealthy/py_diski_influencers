from db.db_connection import get_database_connection

def insert_records(records, table, batch_size=500):
    allowed_tables = {"instagram", "tiktok"}
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name: {table}")

    with get_database_connection() as conn:
        cursor = conn.cursor()

        insert_query = f"""
            INSERT IGNORE INTO {table} (influencer_name, caption, post_url, post_date)
            VALUES (%s, %s, %s, %s);
        """

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            values = [
                (
                    record['influencer_name'],
                    record['caption'],
                    record['post_url'],
                    record['post_date']
                )
                for record in batch
            ]

            cursor.executemany(insert_query, values)
            conn.commit()

    print(f"Tried inserting {len(records)} records into '{table}' in batches of {batch_size}. Duplicate entries were ignored.")