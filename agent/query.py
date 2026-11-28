"""Chọn dữ liệu sản phẩm trước khi gửi câu hỏi cho mô hình ngôn ngữ."""

import re
import unicodedata
from decimal import Decimal, InvalidOperation


CATEGORY_NAMES = (
    ("lót chuột", "Giá đỡ & Phụ kiện bàn làm việc"),
    ("giá đỡ", "Giá đỡ & Phụ kiện bàn làm việc"),
    ("bàn phím", "Bàn phím"),
    ("tai nghe", "Tai nghe"),
    ("webcam", "Webcam"),
    ("hub", "Hub & Cáp chuyển đổi"),
    ("đèn", "Giá đỡ & Phụ kiện bàn làm việc"),
    ("chuột", "Chuột máy tính"),
)
MODEL_TOKEN = re.compile(r"(?<!\w)[a-z][a-z0-9]*(?:[-+][a-z0-9]+)*\+?(?!\w)")
BUDGET_PATTERN = re.compile(
    r"\b(dưới|tối đa|không quá|ngân sách(?:\s+(?:tầm|khoảng))?|có đúng)\s+"
    r"(\d+(?:[.,]\d+)*)\s*(triệu|nghìn|ngàn|vnđ|vnd|đồng|tr|k|đ)?(?!\w)"
)


def _normalize(text):
    return unicodedata.normalize("NFC", text).casefold()


def _read_budget(question):
    """Đọc cận trên giá bằng đồng, kèm quy tắc nhận hoặc loại giá bằng cận."""
    match = BUDGET_PATTERN.search(question)
    if match is None:
        return None

    amount = match[2]
    groups = re.split(r"[.,]", amount)
    if len(groups) > 1 and all(len(group) == 3 for group in groups[1:]):
        amount = "".join(groups)
    else:
        amount = amount.replace(",", ".")
    multipliers = {"k": 1000, "nghìn": 1000, "ngàn": 1000, "triệu": 1000000, "tr": 1000000}
    try:
        value = Decimal(amount) * multipliers.get(match[3], 1)
    except InvalidOperation:
        return None
    if value != value.to_integral_value():
        return None
    return int(value), match[1] != "dưới"


def _models(text):
    """Giữ mã kiểu M220, WH-CH720N và M2+, bỏ các từ thông thường."""
    return {
        token for token in MODEL_TOKEN.findall(text)
        if any(char.isdigit() for char in token)
        and not re.fullmatch(r"(?:usb|hdmi|bluetooth|ipx)\d+", token)
    }


def _named_products(catalog, question):
    identifiers = set(re.findall(r"\bsp\d+\b", question))
    if identifiers:
        known = {_normalize(product["id"]): product for product in catalog.products}
        unknown = identifiers - known.keys()
        if unknown:
            return [], "Chưa có mã " + ", ".join(sorted(unknown)).upper() + " trong danh mục. Hỏi khách kiểm tra lại mã."
        return [product for product in catalog.products if _normalize(product["id"]) in identifiers], ""

    requested_models = _models(question)
    all_models = set()
    products = []
    for product in catalog.products:
        name = _normalize(product["name"])
        models = _models(name)
        all_models.update(models)
        numeric_models = re.findall(r"\b\d{4,}\b", name)
        numeric_match = any(
            re.search(r"\b" + model + r"\b", question)
            for model in numeric_models
        )
        # Hai tên mẫu trong danh mục không có mã liền chữ và số.
        phrase_match = (
            "deathadder essential" in name and "deathadder essential" in question
        ) or (
            "i-wok 3" in name and re.search(r"\bi-wok\s*3\b", question)
        )
        if models & requested_models or phrase_match or numeric_match:
            products.append(product)

    unknown = requested_models - all_models - {"i-wok3"}
    if unknown:
        return [], "Chưa xác định được mẫu " + ", ".join(sorted(unknown)) + ". Hỏi lại tên hoặc mã, không thay bằng mẫu khác."
    return products, ""


def _category_products(catalog, question):
    products_by_id = {}
    found_category = False
    for label, category in CATEGORY_NAMES:
        if not re.search(r"(?<!\w)" + re.escape(label) + r"(?!\w)", question):
            continue
        if label == "chuột" and ("lót chuột" in question or "di chuột" in question):
            continue
        found_category = True
        matches = catalog.filter_by_category(category)
        if label in {"lót chuột", "giá đỡ", "đèn"}:
            matches = [product for product in matches if label in _normalize(product["name"])]
        for product in matches:
            products_by_id[product["id"]] = product
    return list(products_by_id.values()), found_category


def select_products(catalog, question) -> tuple[list[dict], str]:
    """Trả sản phẩm liên quan và hướng dẫn đối chiếu các điều kiện đã lọc."""
    text = _normalize(question)
    budget = _read_budget(text)
    named, clarification = _named_products(catalog, text)
    if clarification:
        return [], clarification

    if named:
        instructions = [
            "Khách nêu sản phẩm cụ thể. Giữ đúng mẫu được hỏi kể cả khi hết hàng. "
            "Đọc giá và tồn kho từ dữ liệu, không đề xuất đặt mua sản phẩm hết hàng."
        ]
        if budget:
            limit, inclusive = budget
            relation = "không quá" if inclusive else "dưới"
            for product in named:
                price = product["price_vnd"]
                fits = price <= limit if inclusive else price < limit
                verdict = "đáp ứng" if fits else "không đáp ứng"
                instructions.append(
                    f"Python đã đối chiếu {product['id']} giá {price} đồng {verdict} "
                    f"ngân sách {relation} {limit} đồng. Nêu đúng kết quả này."
                )
        return named, "\n".join(instructions)

    products, found_category = _category_products(catalog, text)
    if not found_category:
        products = catalog.get_all_products()

    if budget:
        limit, inclusive = budget
        maximum = limit if inclusive else limit - 1
        allowed_ids = {product["id"] for product in catalog.filter_by_budget(maximum)}
        products = [product for product in products if product["id"] in allowed_ids]

    if found_category or budget:
        products = [product for product in products if product["stock"] > 0]
        instruction = (
            "Python đã lọc theo loại sản phẩm, cận trên ngân sách được nhận diện và tồn kho. "
            "Chỉ gợi ý mua các mẫu còn lại. Đối chiếu thêm tính năng và mục đích khách hỏi."
        )
        if not products:
            instruction += " Không có mẫu còn hàng đáp ứng các điều kiện đã lọc; báo rõ chưa có sản phẩm phù hợp."
        return products, instruction

    return products, (
        "Câu hỏi chưa có mã mẫu, loại hàng hoặc cận trên ngân sách rõ ràng. "
        "Dùng danh mục và chính sách để trả lời trong phạm vi có dữ liệu, "
        "hỏi lại nếu chưa rõ nhu cầu. Không tự suy diễn rằng có mẫu đáp ứng điều kiện chưa kiểm tra."
    )
