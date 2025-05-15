import json

def read_insta_json_data():
    filepath = "/Users/lennartmac/Documents/Projects/python/py_diski_influencers/util/users_14may.json"  # Pas dit aan naar jouw bestand

    # JSON inladen
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    user_posts = {}

    for record in data:
        username = record.get('username', None)
        if not username:
            continue  # skip records zonder username

        latest_posts = record.get('latestPosts', [])
        if not isinstance(latest_posts, list):
            continue  # skip als latestPosts geen lijst is

        posts_info = []
        for post in latest_posts:
            caption = post.get('caption', '')
            url = post.get('url', '')
            timestamp = post.get('timestamp', None)

            posts_info.append({
                'caption': caption,
                'url': url,
                'timestamp': timestamp
            })

        user_posts[username] = posts_info

    return user_posts

if __name__ == "__main__":
    read_insta_json_data()
