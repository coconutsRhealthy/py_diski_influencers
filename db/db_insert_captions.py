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


def insert_archive_records(records, platform, batch_size=500):
    """Insert ALL captions (unfiltered, incl. empty) into the raw captions_archive table.

    `platform` is stored as a column ('instagram' or 'tiktok') rather than being the
    table name, so the full corpus lives in one table. Idempotent via INSERT IGNORE
    on the unique_post key, so re-scrapes of the same posts are deduped.
    """
    if not records:
        print("No archive records to insert.")
        return

    with get_database_connection() as conn:
        cursor = conn.cursor()

        insert_query = """
            INSERT IGNORE INTO captions_archive (platform, influencer_name, caption, post_url, post_date)
            VALUES (%s, %s, %s, %s, %s);
        """

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            values = [
                (
                    platform,
                    record['influencer_name'],
                    record['caption'],
                    record['post_url'],
                    record['post_date']
                )
                for record in batch
            ]

            cursor.executemany(insert_query, values)
            conn.commit()

    print(f"Tried archiving {len(records)} '{platform}' captions into 'captions_archive' in batches of {batch_size}. Duplicate entries were ignored.")