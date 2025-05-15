
from util.read_json import read_insta_json_data
from db.db_insert import insert_records
from util.captions_util import normalize_caption, check_keywords_in_caption

def main():
    user_posts = read_insta_json_data()

    # Stap 3: Omzetten naar lijst met records voor db_insert
    records = []
    for username, posts in user_posts.items():
        for post in posts:
            normalized_caption = normalize_caption(post['caption'])

            if check_keywords_in_caption(normalized_caption):
                records.append({
                    'influencer_name': username,
                    'caption': normalized_caption,
                    'post_url': post['url'],
                    'post_date': post['timestamp']
                })

    # Stap 4: Records in database steken
    insert_records(records, "instagram")

if __name__ == "__main__":
    main()
