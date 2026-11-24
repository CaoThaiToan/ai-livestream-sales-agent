import json
import re
import unicodedata
from pathlib import Path


CATALOG_PATH = (
    Path(__file__).resolve().parent.parent
    / "sales_data"
    / "products_demo.json"
)


def load_products(path=CATALOG_PATH):
    """Đọc danh mục và kiểm tra các trường cần cho việc tra cứu."""
    products = json.loads(Path(path).read_text(encoding="utf-8"))

    if not isinstance(products, list):
        raise ValueError("Danh mục phải là một danh sách sản phẩm.")

    seen_ids = set()
    for index, product in enumerate(products, start=1):
        if not isinstance(product, dict):
            raise ValueError(f"Sản phẩm thứ {index} phải là một đối tượng JSON.")

        for field in ("id", "name"):
            value = product.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Sản phẩm thứ {index} thiếu {field} hợp lệ.")

        product_id = product["id"].strip().casefold()
        if product_id in seen_ids:
            raise ValueError(f"Mã sản phẩm bị trùng: {product['id']}")
        seen_ids.add(product_id)

        for field in ("price_vnd", "stock"):
            value = product.get(field)
            if type(value) is not int or value < 0:
                raise ValueError(
                    f"{product['id']}: {field} phải là số nguyên không âm."
                )

    return products


def _words(text):
    """Chuẩn hóa chữ hoa, chữ thường, dấu câu và khoảng trắng."""
    text = unicodedata.normalize("NFC", text).casefold()
    return re.findall(r"\w+", text)


def find_product(products, query):
    """Tìm theo mã hoặc cụm tên. Trả về sản phẩm khi có đúng một kết quả."""
    words = _words(query)
    if not words:
        return None

    for product in products:
        if words == _words(product["id"]):
            return product

    query_words = set(words)
    matches = [
        product
        for product in products
        if query_words.issubset(set(_words(product["name"])))
    ]
    return matches[0] if len(matches) == 1 else None



def filter_products(products, *, category=None, max_price=None, inclusive=True, in_stock=True):
    """Lọc theo loại, ngân sách tính bằng đồng và tình trạng còn hàng."""
    legacy_names = {"chuot": "chuột", "ban_phim": "bàn phím", "tai_nghe": "tai nghe"}
    matches = []
    for product in products:
        if in_stock and product["stock"] == 0:
            continue
        if category is not None:
            actual = product.get("category")
            if actual is None:
                name = product["name"].casefold()
                actual = next((key for key, label in legacy_names.items()
                               if name == label or name.startswith(label + " ")), None)
            if actual != category:
                continue
        price = product["price_vnd"]
        if max_price is not None and (price > max_price or (price == max_price and not inclusive)):
            continue
        matches.append(product)
    return matches
