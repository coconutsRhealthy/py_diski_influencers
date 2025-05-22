import json
import textwrap
from util.captions_util import check_keywords_in_caption

def read_insta_hashtag_json_data():
    filepath = "/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/hashtag/21mei_nakdfashion.json"

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hashtag_posts = []

    for record in data:
        username = record.get('ownerUsername', None)
        caption = record['caption']
        timestamp = record['timestamp']
        url = record['url']

        post_info = {
            'username': username,
            'caption': caption,
            'url': url,
            'timestamp': timestamp
        }

        hashtag_posts.append(post_info)

    hashtag_posts.sort(key=lambda x: x['timestamp'], reverse=True)
    return hashtag_posts

def print_hashtag_posts(posts, scan_for_discount_words=False):
    count = 0  # counts printed posts
    filtered_posts = posts

    if scan_for_discount_words:
        filtered_posts = [post for post in posts if check_keywords_in_caption(post['caption'])]

    total = len(filtered_posts)

    for record in filtered_posts:
        count += 1
        print(f"[{count}/{total}]")
        print(record['username'])
        print(record['timestamp'])
        print("")
        print("Caption:")
        wrapped_caption = textwrap.fill(record['caption'], width=150)
        print(wrapped_caption)
        print("\nPost URL:")
        print(record['url'])
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    posts = read_insta_hashtag_json_data()
    print_hashtag_posts(posts, True)