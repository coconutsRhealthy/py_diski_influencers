import json
from pathlib import Path
import mysql.connector
import random

def get_usernames_from_jsons(directory_path):
    directory = Path(directory_path)
    brands = {
        "gutsgusto",
        "loavies",
        "getdrezzed",
        "begoldennl",
        "mimamsterdam",
        "paulie__pocket",
        "famousstore",
        "terstalnl",
        "maniacnails.official",
        "tessvfashion"
    }
    usernames_with_brands = {}

    for json_file in directory.rglob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Fout bij inladen van {json_file}, wordt overgeslagen")
                continue

        for record in data:
            username = record.get('ownerUsername')
            if not username:
                continue

            mentions = record.get('mentions', [])
            matched_brands = brands.intersection(mentions)

            if matched_brands:
                usernames_with_brands.setdefault(username, set()).update(matched_brands)

    return usernames_with_brands


def check_usernames_in_mysql(usernames):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="diski"
    )
    cursor = connection.cursor()

    results = {}
    for username in usernames:
        cursor.execute("SELECT 1 FROM influencers WHERE name = %s", (username,))
        results[username] = cursor.fetchone() is not None

    cursor.close()
    connection.close()
    return results


def filter_usernames_by_brand_count(usernames_with_brands, min_brands):
    return {u: b for u, b in usernames_with_brands.items() if len(b) >= min_brands}


def summarize_results(db_results):
    total_in_db = sum(1 for v in db_results.values() if v)
    total_not_in_db = sum(1 for v in db_results.values() if not v)
    total = total_in_db + total_not_in_db
    percent_not_in_db = (total_not_in_db / total * 100) if total > 0 else 0
    return total, total_in_db, total_not_in_db, percent_not_in_db


def print_results(filtered_usernames, db_results):
    print("\n🧾 Overzicht van usernames:\n" + "-" * 50)
    for idx, username in enumerate(sorted(filtered_usernames), start=1):
        brands_list = ", ".join(sorted(filtered_usernames[username]))
        in_db = "✅ In DB" if db_results[username] else "❌ Niet in DB"
        print(f"{idx:>3}. @{username:<25} [{brands_list}] --> {in_db}")
    print("-" * 50)


def get_line_count(file_path):
    """Tel aantal regels in een bestand (0 als bestand niet bestaat)."""
    file = Path(file_path)
    if not file.exists():
        return 0
    with open(file, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def save_random_usernames_not_in_db(filtered_usernames, db_results, max_total, input_file_path, output_file):
    """Bepaal dynamisch sample_size en sla random subset op in input_file en output_file."""
    usernames_not_in_db = [u for u in sorted(filtered_usernames) if not db_results[u]]

    existing_lines = get_line_count(input_file_path)
    sample_size = max_total - existing_lines
    sample_size = max(0, min(sample_size, len(usernames_not_in_db)))  # veilig begrenzen

    if sample_size == 0:
        print(f"\n✅ Geen nieuwe usernames nodig (bestand bevat al {existing_lines} regels of er zijn er geen beschikbaar).")
        return

    random_sample = random.sample(usernames_not_in_db, sample_size)

    # Append naar inputbestand (apify_input/instagram_user_urls.txt)
    input_file = Path(input_file_path)
    input_file.parent.mkdir(parents=True, exist_ok=True)
    with open(input_file, "a", encoding="utf-8") as f:
        for username in random_sample:
            f.write(f"https://www.instagram.com/{username}\n")

    # Schrijf ook volledige lijst naar een apart output-bestand
    with open(output_file, "w", encoding="utf-8") as f:
        for username in random_sample:
            f.write(f"https://www.instagram.com/{username}\n")

    print("\n" + "=" * 60)
    print(f"💾 {sample_size} nieuwe usernames toegevoegd aan:")
    print(f"📁 {input_file.resolve()}")
    print("=" * 60)
    print("📋 Toegevoegde usernames:\n")

    for idx, username in enumerate(random_sample, start=1):
        print(f"{idx:>3}. https://www.instagram.com/{username}")

    print("\n📄 Ook opgeslagen in logbestand:")
    print(f"   → {output_file.resolve()}")
    print("=" * 60 + "\n")


def main():
    folder_path = "/Users/LennartMac/Documents/Projects/python/py_diski_influencers/jsons/insta/mentioned"
    min_brands = 1
    max_total = 1345
    input_file_path = "../apify_input/instagram_user_urls.txt"
    output_file = Path("txt/filtered_usernames_not_in_db_added.txt")

    print("🔍 JSON-bestanden worden geanalyseerd...")
    usernames_with_brands = get_usernames_from_jsons(folder_path)

    filtered_usernames = filter_usernames_by_brand_count(usernames_with_brands, min_brands)

    print(f"📊 {len(filtered_usernames)} usernames gevonden met ≥ {min_brands} merk(en).")
    db_results = check_usernames_in_mysql(filtered_usernames.keys())

    #print_results(filtered_usernames, db_results)

    total, total_in_db, total_not_in_db, percent_not_in_db = summarize_results(db_results)
    print("\n--- Samenvatting ---")
    print(f"Totaal usernames gevonden (na filter): {total}")
    print(f"In DB: {total_in_db}")
    print(f"Niet in DB: {total_not_in_db}")
    print(f"Percentage niet in DB: {percent_not_in_db:.2f}%")

    save_random_usernames_not_in_db(filtered_usernames, db_results, max_total, input_file_path, output_file)


if __name__ == "__main__":
    main()