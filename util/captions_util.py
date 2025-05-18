import re
import unicodedata

def normalize_caption(caption):
    """
    Normalize the caption to plain text:
    - Remove emojis and non-ASCII characters
    - Normalize unicode
    """
    if not isinstance(caption, str):
        return ""

    # Normalize unicode (e.g. é -> é)
    normalized = unicodedata.normalize("NFKD", caption)

    # Remove emojis and non-ASCII characters
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")

    # Optionally, remove extra whitespace
    return re.sub(r'\s+', ' ', ascii_only).strip()

def check_keywords_in_caption(caption):
    keywords = [
        "korting",
        "discount",
        "% off",
        "%off",
        "% of",
        "%of",
        "my code",
        "mijn code",
        "de code",
        "code:",
        "code",
        "with code",
        "met code",
        "use code",
        "gebruik code",
        "coupon",
        "werbung",
        "anzeige",
        "rabatt",
        "dem code",
        "le code",
        "remise",
        "réduction",
        "reduction",
    ]
    caption_lower = caption.lower()
    return any(keyword.lower() in caption_lower for keyword in keywords)