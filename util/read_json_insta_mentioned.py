import json

def read_insta_mentioned_json_data():
    filepath = "/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/mentioned/2025/aug/8aug_small.json"

    # JSON inladen
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mentioned_posts = {}

    for record in data:
        username = record.get('ownerUsername', None)

        if not username:
            continue  # skip records zonder username

        caption = record['caption']
        timestamp = record['timestamp']
        url = record['url']

        post_info = {
            'caption': caption,
            'url': url,
            'timestamp': timestamp
        }

        if username not in mentioned_posts:
            mentioned_posts[username] = []

        mentioned_posts[username].append(post_info)

    return mentioned_posts

if __name__ == "__main__":
    read_insta_mentioned_json_data()
