import json

def get_usernames_from_json():
    filepath = "/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/mentioned/2025/mei/21mei_big.json"

    # JSON inladen
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    unique_usernames = set()

    for record in data:
        username = record.get('ownerUsername')
        if not username:
            continue  # skip records zonder username

        mentions = record.get('mentions', [])

        if 'gutsgusto' in mentions:
            unique_usernames.add(username)

    # Zet om naar een lijst en sorteer alfabetisch
    sorted_usernames = sorted(unique_usernames)

    for username in sorted_usernames:
        print(username)

if __name__ == "__main__":
    get_usernames_from_json()
