"""Recherche universelle Telegram : sans IA payante, sans dépendances externes.

Les marques sont des libellés lus dans les publications, pas une preuve
d'authenticité ni une reconnaissance fiable de photos sans légende.
"""
import re
import unicodedata
from collections import Counter

# L'index est stable : les callbacks Telegram transportent un indice de cette liste.
BRAND_ALIASES = [
    ("Nike", ["nike", "air max", "vapormax"]),
    ("Jordan", ["jordan", "air jordan"]),
    ("Adidas", ["adidas", "samba", "gazelle", "campus"]),
    ("New Balance", ["new balance"]),
    ("ASICS", ["asics", "gel kayano", "gel nyc"]),
    ("On Running", ["on running", "cloudtilt", "cloudmonster"]),
    ("Puma", ["puma"]),
    ("Salomon", ["salomon"]),
    ("Mizuno", ["mizuno"]),
    ("Saucony", ["saucony"]),
    ("Hoka", ["hoka"]),
    ("Under Armour", ["under armour", "underarmor"]),
    ("Reebok", ["reebok"]),
    ("Converse", ["converse"]),
    ("Vans", ["vans"]),
    ("UGG", ["ugg"]),
    ("Crocs", ["crocs"]),
    ("Dior", ["dior", "dior b22", "dior b30"]),
    ("Louis Vuitton", ["louis vuitton", "lv runner", "lv trainer"]),
    ("Prada", ["prada"]),
    ("Gucci", ["gucci"]),
    ("Hermès", ["hermes", "hermès"]),
    ("Chanel", ["chanel"]),
    ("Balenciaga", ["balenciaga"]),
    ("Louboutin", ["louboutin"]),
    ("Moncler", ["moncler"]),
    ("Stone Island", ["stone island"]),
    ("CP Company", ["cp company", "c p company"]),
    ("Essentials", ["essentials", "fear of god"]),
    ("Burberry", ["burberry"]),
    ("Céline", ["celine", "céline"]),
    ("Lacoste", ["lacoste"]),
    ("Ralph Lauren", ["ralph lauren", "polo ralph lauren"]),
    ("Palm Angels", ["palm angels"]),
    ("Off-White", ["off white", "off-white"]),
    ("Amiri", ["amiri"]),
    ("Givenchy", ["givenchy"]),
    ("Fendi", ["fendi"]),
    ("Loewe", ["loewe"]),
    ("Loro Piana", ["loro piana"]),
    ("Versace", ["versace"]),
    ("Valentino", ["valentino"]),
    ("Cartier", ["cartier"]),
    ("Rolex", ["rolex"]),
    ("Audemars Piguet", ["audemars piguet", "royal oak"]),
    ("G-Shock", ["g shock", "gshock", "g-shock"]),
    ("Apple", ["apple", "iphone", "airpods", "macbook", "ipad", "apple watch"]),
    ("Samsung", ["samsung", "galaxy"]),
    ("Dyson", ["dyson", "airwrap"]),
    ("Smeg", ["smeg"]),
    ("Sony", ["sony", "playstation", "ps5"]),
    ("Xbox", ["xbox"]),
    ("Meta", ["meta glasses", "ray ban meta", "ray-ban meta"]),
    ("Columbia", ["columbia"]),
    ("The North Face", ["the north face"]),
    ("Canada Goose", ["canada goose"]),
    ("Whoop", ["whoop"]),
]
BRANDS = [name for name, _ in BRAND_ALIASES]


def normalized(value):
    text = unicodedata.normalize("NFKD", str(value or "")).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def flatten(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(filter(None, (flatten(v) for v in value)))
    if isinstance(value, dict):
        return flatten(value.get("text") or value.get("caption") or "")
    return ""


def message_text(m):
    doc = m.get("document") or {}
    if not isinstance(doc, dict):
        doc = {}
    values = (
        m.get("caption"), m.get("text"), m.get("message"),
        m.get("file_name"), doc.get("file_name")
    )
    return " ".join(s for s in (flatten(value) for value in values) if s).strip()[:3000]


def extract_brands(text):
    haystack = " " + normalized(text) + " "
    matches = []
    if not haystack.strip():
        return matches
    for brand, aliases in BRAND_ALIASES:
        if any(" " + normalized(alias) + " " in haystack for alias in aliases):
            matches.append(brand)
    return matches


def index_entry(message):
    text = message_text(message)
    if not text:
        return None
    return {"text": text, "brands": extract_brands(text)}


def index_export_messages(messages):
    result = {}
    for message in messages:
        if message.get("type") != "message":
            continue
        mid = message.get("id")
        if not isinstance(mid, int) or isinstance(mid, bool) or mid <= 0:
            continue
        entry = index_entry(message)
        if entry:
            result[str(mid)] = entry
    return result


def matched(message_text_value, query):
    haystack = normalized(message_text_value)
    needle = normalized(query)
    if not haystack or not needle:
        return False
    # "dior b30" doit retrouver "Dior B30", "b30 dior" aussi.
    words = set(haystack.split())
    return needle in haystack or all(word in words for word in needle.split())


def search_ids(message_ids, search_index, query):
    # Plus récent en premier : les IDs Telegram augmentent au fil des publications.
    result = []
    for mid in sorted(set(message_ids), reverse=True):
        entry = search_index.get(str(mid)) or {}
        text = entry.get("text", "")
        names = " ".join(entry.get("brands") or [])
        if matched(text + " " + names, query):
            result.append(mid)
    return result


def brands_for_ids(message_ids, search_index):
    counts = Counter()
    for mid in set(message_ids):
        entry = search_index.get(str(mid)) or {}
        for brand in entry.get("brands") or []:
            if brand in BRANDS:
                counts[brand] += 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def ids_for_brand(message_ids, search_index, brand):
    return sorted(
        (mid for mid in set(message_ids)
         if brand in (search_index.get(str(mid)) or {}).get("brands", [])),
        reverse=True
    )
