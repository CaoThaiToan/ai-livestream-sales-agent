"""Tra cứu các mẫu câu bán hàng trong danh mục demo."""
import re
import unicodedata

from .catalog import filter_products, find_product

TYPES = {"chuột": "chuot", "bàn phím": "ban_phim", "tai nghe": "tai_nghe"}


def lookup(products, question):
    text = unicodedata.normalize("NFC", question).casefold().strip()
    kinds = [label for label in TYPES if label in text]
    category = TYPES[kinds[0]] if len(kinds) == 1 else None
    code = re.search(r"\bdemo\d+\b", text)
    model = re.search(r"\bmẫu\s+([a-z0-9]+)\b", text)
    if any(word in text for word in ("giao hàng", "giao trong", "bảo hành", "đổi trả")):
        return "missing_policy", []
    if code or model:
        query = code.group() if code else " ".join(kinds + [model.group()])
        product = find_product(products, query)
        return ("found", [product]) if product else ("clarify", [])

    budget = re.search(r"(dưới|tối đa|không quá)\s+(\d+(?:\.\d{3})*)\s*(nghìn|ngàn|k|đồng|đ)?\b", text)
    features = [term for term in ("usb", "bluetooth", "micro") if term in text]
    if len(kinds) > 1 or (not category and not budget and not features):
        return "clarify", []
    limit = None
    if budget:
        limit = int(budget[2].replace(".", ""))
        if budget[3] in ("nghìn", "ngàn", "k"):
            limit *= 1000
    matches = filter_products(products, category=category, max_price=limit,
                              inclusive=not budget or budget[1] != "dưới")
    for term in features:
        matches = [p for p in matches if any(term in s.casefold() for s in p["features"])]
    return ("found" if matches else "no_match"), matches
