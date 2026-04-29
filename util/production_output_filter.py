import argparse
import random
import re
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

RECENT_REPOST_WEEKS_DEFAULT = 3
DEFAULT_DISCOUNT_VALUE = "10"
BRAND_DEFAULT_DISCOUNT_VALUES = {
    "shein": "15",
}
PERCENT_REVIEW_THRESHOLD = 40
EURO_REVIEW_THRESHOLD = 100
REVIEW_MARKER = "REVIEW__"

DISCOUNTS_JSON_PATH = Path(
    "/Users/lennartmac/Documents/Projects/diski-input-insta/src/assets/discounts.json"
)
ARCHIVE_TXT_PATH = Path(
    "/Users/lennartmac/Documents/Projects/diski-input-insta/src/assets/archive5.txt"
)
ARCHIVE_BATCH_LIMIT = 120
MIN_TRAINING_BATCH_SIZE = 20
LOW_PRIORITY_BRANDS = {
    "temu",
    "bylashbabe",
    "idealofsweden",
    "vitakruid",
    "desenio",
    "myproteinnl",
    "smartphonehoesjes.nl",
    "hellofresh.nl",
    "rosental-organics.nl",
}
LOW_PRIORITY_BASE_SCORE = 4.0

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = PROJECT_ROOT / "logs/raw_output_for_day/testoutput.txt"
DEFAULT_OUTPUT = PROJECT_ROOT / "logs/raw_output_for_day/testoutput_production.txt"

PREV_SEEN_DATE_RE = re.compile(r"\.{10}(\d{2})-(\d{2})")
QUOTED_FIELDS_RE = re.compile(r'"([^"]*)"')
DISCOUNT_VALUE_RE = re.compile(r"^€?(\d+(?:\.\d+)?)%?$")
URL_RE = re.compile(r"https?://\S+")


def parse_prev_seen_date(line: str, today: date) -> Optional[date]:
    match = PREV_SEEN_DATE_RE.search(line)
    if not match:
        return None
    month, day = int(match.group(1)), int(match.group(2))
    # Source date has no year — pick the most recent occurrence on/before today.
    candidate = date(today.year, month, day)
    if candidate > today:
        candidate = candidate.replace(year=today.year - 1)
    return candidate


def should_drop_recent_repost(line: str, today: date, recent_weeks: int) -> bool:
    if not line.startswith("..."):
        return False
    prev = parse_prev_seen_date(line, today)
    if prev is None:
        return False
    return (today - prev) < timedelta(weeks=recent_weeks)


def should_drop_unknown_brand(line: str) -> bool:
    return '"UNKNOWN,' in line


def should_drop_missing_code(line: str) -> bool:
    match = QUOTED_FIELDS_RE.search(line)
    if not match:
        return False
    fields = [f.strip() for f in match.group(1).split(",")]
    if len(fields) < 2:
        return False
    return fields[1].lower() == "none"


def process_discount_value(line: str):
    match = QUOTED_FIELDS_RE.search(line)
    if not match:
        return line, None
    inner = match.group(1)
    parts = [p.strip() for p in inner.split(",")]
    if len(parts) < 3:
        return line, None

    value = parts[2]
    action = None

    if value.lower() == "none":
        brand_key = parts[0].lstrip("_").lower()
        parts[2] = BRAND_DEFAULT_DISCOUNT_VALUES.get(brand_key, DEFAULT_DISCOUNT_VALUE)
        action = "defaulted"
    else:
        m = DISCOUNT_VALUE_RE.match(value)
        if not m:
            action = "marked"
        else:
            num = float(m.group(1))
            is_euro = value.startswith("€")
            if is_euro and num > EURO_REVIEW_THRESHOLD:
                action = "marked"
            elif not is_euro and num > PERCENT_REVIEW_THRESHOLD:
                action = "marked"

    new_inner = ", ".join(parts)
    new_line = line.replace(f'"{inner}"', f'"{new_inner}"', 1)
    if action == "marked" and not new_line.startswith(REVIEW_MARKER):
        new_line = REVIEW_MARKER + new_line
    return new_line, action


def clean_new_company_line(line: str) -> Optional[str]:
    if "MULTI__" in line:
        return None
    match = QUOTED_FIELDS_RE.search(line)
    if not match:
        return None
    inner = match.group(1)
    parts = [p.strip() for p in inner.split(",")]
    if not parts or not parts[0].startswith("___"):
        return None
    bare_brand = parts[0][3:].lower()
    cleaned_brand = re.sub(r"[^a-z0-9._]", "", bare_brand)
    parts[0] = cleaned_brand
    new_inner = ", ".join(parts)
    return line.replace(f'"{inner}"', f'"{new_inner}"', 1)


def filter_lines(lines, today: date, recent_weeks: int):
    kept = []
    dropped_recent = []
    dropped_unknown = []
    dropped_missing_code = []
    stripped_old_repost = 0
    cleaned_new_company = 0
    defaulted_discount = 0
    marked_review = 0
    dropped_multi_dup = []
    multi_seen_urls = set()
    for line in lines:
        if should_drop_unknown_brand(line):
            dropped_unknown.append(line)
        elif should_drop_missing_code(line):
            dropped_missing_code.append(line)
        elif should_drop_recent_repost(line, today, recent_weeks):
            dropped_recent.append(line)
        else:
            if line.startswith("..."):
                line = line[3:]
                stripped_old_repost += 1
            transformed = clean_new_company_line(line)
            if transformed is not None:
                line = transformed
                cleaned_new_company += 1
            line, action = process_discount_value(line)
            if action == "defaulted":
                defaulted_discount += 1
            elif action == "marked":
                marked_review += 1

            if "MULTI__" in line:
                url_match = URL_RE.search(line)
                url = url_match.group(0) if url_match else None
                if url and url in multi_seen_urls:
                    dropped_multi_dup.append(line)
                    continue
                if url:
                    multi_seen_urls.add(url)
                if not line.startswith(REVIEW_MARKER):
                    line = REVIEW_MARKER + line
                    marked_review += 1
                line = line.replace("MULTI__", "", 1)

            kept.append(line)
    return (
        kept,
        dropped_recent,
        dropped_unknown,
        dropped_missing_code,
        dropped_multi_dup,
        stripped_old_repost,
        cleaned_new_company,
        defaulted_discount,
        marked_review,
    )


def line_to_brand(line: str) -> str:
    payload = line[len(REVIEW_MARKER):] if line.startswith(REVIEW_MARKER) else line
    match = QUOTED_FIELDS_RE.search(payload)
    if not match:
        return ""
    return match.group(1).split(",", 1)[0].strip().lower()


def extract_company(record_line: str) -> str:
    s = record_line.strip()
    if not s:
        return ""
    first = s.split(",", 1)[0].replace('"', '').strip()
    if "(" in first:
        first = first.split("(", 1)[0].strip()
    return first.lower()


def read_batches_from_discounts_json(path: Path) -> List[List[str]]:
    batches: List[List[str]] = []
    current: List[str] = []
    in_array = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "[" in raw:
            in_array = True
            continue
        stripped = raw.strip()
        if in_array and stripped and "]" not in stripped:
            current.append(stripped)
        if in_array and (not stripped or "]" in raw):
            if current:
                batches.append(current[:])
                current.clear()
    if current:
        batches.append(current[:])
    return batches


def read_batches_from_archive(path: Path) -> List[List[str]]:
    batches: List[List[str]] = []
    current: List[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped:
            current.append(stripped)
        elif current:
            batches.append(current[:])
            current.clear()
    if current:
        batches.append(current[:])
    return batches


def build_training_batches() -> List[List[str]]:
    discounts_batches = read_batches_from_discounts_json(DISCOUNTS_JSON_PATH)
    archive_batches = read_batches_from_archive(ARCHIVE_TXT_PATH)

    discounts_brands = [[extract_company(line) for line in batch] for batch in discounts_batches]
    archive_brands = [[extract_company(line) for line in batch] for batch in archive_batches]

    training: List[List[str]] = []
    if len(discounts_brands) > 1:
        training.extend(discounts_brands[1:])
    training.extend(archive_brands[:ARCHIVE_BATCH_LIMIT])
    return [b for b in training if len(b) >= MIN_TRAINING_BATCH_SIZE]


def compute_brand_avg_positions(brands, training_batches):
    avg = {}
    for brand in brands:
        total = 0
        count = 0
        for batch in training_batches:
            try:
                idx = batch.index(brand)
            except ValueError:
                continue
            total += idx
            count += 1
        if count > 0:
            avg[brand] = total / count
    return avg


def sort_kept_lines(
    kept_lines: List[str],
    training_batches: List[List[str]],
    rng: random.Random,
) -> List[str]:
    line_brands: List[Tuple[str, str]] = [(line, line_to_brand(line)) for line in kept_lines]

    seen = set()
    primary: List[Tuple[str, str]] = []
    duplicates: List[Tuple[str, str]] = []
    for line, brand in line_brands:
        if brand and brand in seen:
            duplicates.append((line, brand))
        else:
            if brand:
                seen.add(brand)
            primary.append((line, brand))

    unique_brands = [b for _, b in primary if b]
    avg = compute_brand_avg_positions(unique_brands, training_batches)
    for brand in unique_brands:
        if brand in LOW_PRIORITY_BRANDS:
            avg[brand] = LOW_PRIORITY_BASE_SCORE + rng.random()

    sortable: List[Tuple[str, str]] = []
    new_companies: List[Tuple[str, str]] = []
    for line, brand in primary:
        if brand and brand in avg:
            sortable.append((line, brand))
        else:
            new_companies.append((line, brand))

    sortable.sort(key=lambda lb: avg[lb[1]])

    half = len(sortable) // 2
    first_half = sortable[:half]
    second_half = list(sortable[half:])

    mixed: List[Tuple[str, str]] = []
    list1 = list(second_half)
    list2 = list(duplicates)
    while list1 or list2:
        if list1 and (not list2 or rng.random() < 0.5):
            mixed.append(list1.pop(0))
        else:
            mixed.append(list2.pop(0))

    final = first_half + mixed + new_companies
    return [line for line, _ in final]


def strip_urls_from_non_review(lines: List[str]) -> Tuple[List[str], int]:
    cleaned = []
    stripped_count = 0
    for line in lines:
        if line.startswith(REVIEW_MARKER):
            cleaned.append(line)
            continue
        new_line = URL_RE.sub("", line).rstrip()
        if new_line != line:
            stripped_count += 1
        cleaned.append(new_line)
    return cleaned, stripped_count


def strip_prev_seen_dates(lines: List[str]) -> Tuple[List[str], int]:
    cleaned = []
    stripped_count = 0
    for line in lines:
        new_line = PREV_SEEN_DATE_RE.sub("", line)
        if new_line != line:
            stripped_count += 1
        cleaned.append(new_line)
    return cleaned, stripped_count


def main():
    parser = argparse.ArgumentParser(
        description="Filter main_pipeline raw output into a production-ready txt."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--recent-weeks",
        type=int,
        default=RECENT_REPOST_WEEKS_DEFAULT,
        help="Drop '...' lines whose previous-seen date is newer than this many weeks ago (default: 3).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for sort jitter and duplicate-mixing (default: nondeterministic).",
    )
    parser.add_argument("--no-sort", action="store_true", help="Skip the brand sort pass.")
    args = parser.parse_args()

    today = date.today()
    lines = args.input.read_text(encoding="utf-8").splitlines()
    (
        kept,
        dropped_recent,
        dropped_unknown,
        dropped_missing_code,
        dropped_multi_dup,
        stripped_old_repost,
        cleaned_new_company,
        defaulted_discount,
        marked_review,
    ) = filter_lines(lines, today, args.recent_weeks)

    rng = random.Random(args.seed)
    training_batch_count = 0
    if not args.no_sort:
        training_batches = build_training_batches()
        training_batch_count = len(training_batches)
        kept = sort_kept_lines(kept, training_batches, rng)

    kept, urls_stripped = strip_urls_from_non_review(kept)
    kept, prev_dates_stripped = strip_prev_seen_dates(kept)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")

    print(f"Input : {args.input} ({len(lines)} lines)")
    print(f"Output: {args.output} ({len(kept)} lines)")
    print(
        f"Dropped {len(dropped_recent)} '...' line(s) with previous-seen date < {args.recent_weeks} week(s) ago"
    )
    print(f"Dropped {len(dropped_unknown)} UNKNOWN-brand line(s)")
    print(f"Dropped {len(dropped_missing_code)} line(s) with no discount code (None)")
    print(f"Dropped {len(dropped_multi_dup)} extra MULTI line(s) sharing a post URL")
    print(f"Stripped leading '...' from {stripped_old_repost} old-repost line(s)")
    print(f"Cleaned {cleaned_new_company} new-company '___' line(s)")
    print(f"Defaulted {defaulted_discount} discount value(s) from None to {DEFAULT_DISCOUNT_VALUE}")
    print(
        f"Marked {marked_review} line(s) with REVIEW__ "
        f"(weird value, percent > {PERCENT_REVIEW_THRESHOLD}, or euro > {EURO_REVIEW_THRESHOLD})"
    )
    if args.no_sort:
        print("Sort: skipped (--no-sort)")
    else:
        print(f"Sorted using {training_batch_count} training batch(es)")
    print(f"Stripped URL from {urls_stripped} non-REVIEW line(s)")
    print(f"Stripped trailing previous-seen date from {prev_dates_stripped} line(s)")


if __name__ == "__main__":
    main()
