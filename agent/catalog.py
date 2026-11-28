"""
catalog.py - Module nạp, xác thực và tra cứu dữ liệu sản phẩm & chính sách cửa hàng.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Đường dẫn mặc định tương đối theo cấu trúc thư mục dự án
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PRODUCTS_PATH = BASE_DIR / "data" / "products.json"
DEFAULT_POLICY_PATH = BASE_DIR / "data" / "store_policy.md"

REQUIRED_FIELDS = [
    "id",
    "name",
    "category",
    "description",
    "price_vnd",
    "stock",
    "features",
    "suitable_for",
    "warranty_months",
    "data_type",
]


class ProductCatalog:
    """
    Quản lý danh mục sản phẩm và tài liệu chính sách của cửa hàng.
    Hỗ trợ kiểm tra hợp lệ dữ liệu và các thao tác tìm kiếm/lọc nhanh.
    """

    def __init__(
        self,
        products_path: Optional[Path] = None,
        policy_path: Optional[Path] = None,
    ):
        self.products_path = products_path or DEFAULT_PRODUCTS_PATH
        self.policy_path = policy_path or DEFAULT_POLICY_PATH
        self.products: List[Dict[str, Any]] = []
        self.products_by_id: Dict[str, Dict[str, Any]] = {}
        self.policy_text: str = ""

        self.load_data()

    def load_data(self) -> None:
        """Đọc và kiểm tra tính hợp lệ của toàn bộ dữ liệu."""
        self._load_products()
        self._load_policy()

    def _load_products(self) -> None:
        if not self.products_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file sản phẩm tại: {self.products_path}")

        with open(self.products_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Dữ liệu products.json phải là một danh sách (list).")

        seen_ids = set()
        validated_products = []

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Sản phẩm tại vị trí {idx} không phải là từ điển (dict).")

            # Kiểm tra các trường bắt buộc
            for field in REQUIRED_FIELDS:
                if field not in item:
                    raise ValueError(f"Sản phẩm thứ {idx} thiếu trường bắt buộc: '{field}'.")

            # Kiểm tra ID duy nhất
            prod_id = str(item["id"]).strip()
            if not prod_id:
                raise ValueError(f"Sản phẩm thứ {idx} có ID rỗng.")
            if prod_id in seen_ids:
                raise ValueError(f"Mã sản phẩm bị trùng lặp: '{prod_id}'.")
            seen_ids.add(prod_id)

            # Kiểm tra giá và tồn kho là số nguyên không âm
            price = item["price_vnd"]
            if not isinstance(price, int) or price < 0:
                raise ValueError(f"Sản phẩm '{prod_id}' có price_vnd không hợp lệ (phải là số nguyên >= 0): {price}")

            stock = item["stock"]
            if not isinstance(stock, int) or stock < 0:
                raise ValueError(f"Sản phẩm '{prod_id}' có stock không hợp lệ (phải là số nguyên >= 0): {stock}")

            validated_products.append(item)

        self.products = validated_products
        self.products_by_id = {p["id"]: p for p in validated_products}

    def _load_policy(self) -> None:
        if not self.policy_path.exists():
            raise FileNotFoundError(f"Không tìm thấy file chính sách tại: {self.policy_path}")

        with open(self.policy_path, "r", encoding="utf-8") as f:
            self.policy_text = f.read().strip()

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin chi tiết một sản phẩm theo ID."""
        return self.products_by_id.get(product_id.strip())

    def get_all_products(self) -> List[Dict[str, Any]]:
        """Trả về toàn bộ danh mục sản phẩm."""
        return self.products

    def get_policy(self) -> str:
        """Trả về nội dung văn bản chính sách cửa hàng."""
        return self.policy_text

    def filter_by_budget(self, max_budget_vnd: int, min_budget_vnd: int = 0) -> List[Dict[str, Any]]:
        """Lọc các sản phẩm nằm trong khoảng giá cho phép."""
        return [
            p for p in self.products
            if min_budget_vnd <= p["price_vnd"] <= max_budget_vnd
        ]

    def filter_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Lọc các sản phẩm theo danh mục."""
        cat_lower = category_name.strip().lower()
        return [
            p for p in self.products
            if cat_lower in p["category"].lower()
        ]

    def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Tìm kiếm nhanh sản phẩm theo từ khóa trong tên, danh mục, mô tả hoặc tính năng.
        """
        q = query.strip().lower()
        if not q:
            return self.products[:limit]

        keywords = q.split()
        scored_products = []

        for p in self.products:
            score = 0
            # Trọng số ưu tiên khi khớp tên hoặc mã ID
            if p["id"].lower() == q or p["id"].lower() in q:
                score += 20
            if q in p["name"].lower():
                score += 15

            # Tìm kiếm theo từng từ khóa
            searchable_text = f"{p['name']} {p['category']} {p['description']} {' '.join(p['features'])} {' '.join(p['suitable_for'])}".lower()
            
            matched_count = sum(1 for kw in keywords if kw in searchable_text)
            score += matched_count * 3

            if score > 0:
                scored_products.append((score, p))

        # Sắp xếp theo điểm giảm dần
        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_products[:limit]]

    def format_context_for_prompt(self, relevant_products: Optional[List[Dict[str, Any]]] = None) -> str:
        """Giữ đủ dữ kiện của sản phẩm được chọn và chính sách cho câu trả lời."""
        products_to_format = relevant_products if relevant_products is not None else self.products
        return (
            "=== SẢN PHẨM ĐÃ TRA CỨU ===\n"
            + json.dumps(products_to_format, ensure_ascii=False, indent=2)
            + "\n\n=== CHÍNH SÁCH CỬA HÀNG ===\n"
            + self.policy_text
        )


# Singleton instance tiện lợi khi import dùng ngay
default_catalog = ProductCatalog()


if __name__ == "__main__":
    print("=== KIỂM TRA MÔ-ĐUN CATALOG ===")
    catalog = ProductCatalog()
    print(f"-> Đã nạp thành công {len(catalog.products)} sản phẩm.")
    print(f"-> Đã nạp chính sách với độ dài {len(catalog.policy_text)} ký tự.")
    
    # Kiểm tra thử nghiệm lọc ngân sách < 300k
    under_300k = catalog.filter_by_budget(300000)
    print(f"-> Sản phẩm dưới 300k ({len(under_300k)} SP): {[p['name'] for p in under_300k]}")

    # Kiểm tra thử nghiệm tìm kiếm từ khóa 'chuột'
    mouse_results = catalog.search_products("chuột không dây")
    print(f"-> Tìm kiếm 'chuột không dây' ({len(mouse_results)} SP): {[p['id'] + ' - ' + p['name'] for p in mouse_results]}")

    print("=> Mô-đun catalog.py hoạt động hoàn hảo!")
