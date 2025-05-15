import json

def read_tiktok_json_data():
    filepath = "/Users/lennartmac/Documents/Projects/python/py_diski_influencers/jsons/tiktok_users_14mei.json"

    # JSON inladen
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    user_posts = {}

    for record in data:
        author_meta = record.get('authorMeta', {})
        username = author_meta.get('name', None)
        if not username:
            continue  # skip als geen username

        # Check of dit record een post is, niet alleen gebruikersinfo
        if not all(k in record for k in ['text', 'createTimeISO', 'webVideoUrl']):
            continue  # skip als het geen volwaardige post is

        caption = record['text']
        timestamp = record['createTimeISO']
        url = record['webVideoUrl']

        post_info = {
            'caption': caption,
            'url': url,
            'timestamp': timestamp
        }

        if username not in user_posts:
            user_posts[username] = []

        user_posts[username].append(post_info)

    return user_posts

if __name__ == "__main__":
    posts = read_tiktok_json_data()
    print(json.dumps(posts, indent=2, ensure_ascii=False))
