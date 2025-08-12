from apify_client import ApifyClient
import os

def load_tiktok_usernames():
    with open("util/apify_input/tiktok_usernames.txt", "r", encoding="utf-8") as f:
        tiktok_usernames = [line.strip() for line in f if line.strip()]
    return tiktok_usernames

def fetch_insta_json_data(tiktok_usernames):
    apify_token = os.environ.get("APIFY_TOKEN", "secret")
    client = ApifyClient(apify_token)

    run_input = {
        "excludePinnedPosts": False,
        "oldestPostDateUnified": "3 days",
        "profiles": tiktok_usernames,
        "resultsPerPage": 100,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadVideos": False,
        "profileScrapeSections": [
            "videos"
        ],
        "profileSorting": "latest",
        "searchSection": "",
        "maxProfilesPerQuery": 10
    }

    run = client.actor("clockworks/free-tiktok-scraper").call(run_input=run_input)

    dataset_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    return dataset_items



def read_tiktok_json_data():
    tiktok_usernames = load_tiktok_usernames()
    data = fetch_insta_json_data(tiktok_usernames)

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
    print(posts)
