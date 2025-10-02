import re
import unicodedata

def normalize_caption(caption):
    """
    Normalize the caption to plain text:
    - Remove emojis and non-printable/control characters
    - Preserve ASCII, common symbols like %, #, @, €, etc.
    """
    if not isinstance(caption, str):
        return ""

    # Normalize unicode (e.g., é -> é)
    normalized = unicodedata.normalize("NFKD", caption)

    # Remove emojis and control characters
    cleaned = "".join(c for c in normalized if c.isprintable() and not unicodedata.category(c).startswith("C"))

    # Collapse multiple spaces
    return re.sub(r'\s+', ' ', cleaned).strip()

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
        "save",
        "bespaar",
        "besparen",
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
        "spart",
    ]
    caption_lower = caption.lower()
    return any(keyword.lower() in caption_lower for keyword in keywords)