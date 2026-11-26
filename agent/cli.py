"""
cli.py - Giao diện dòng lệnh (CLI) tương tác với AI Livestream Sales Agent.
Hỗ trợ chế độ giả lập (--mock) không tiêu tốn API key để kiểm thử tích hợp Avatar/TTS.
"""

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Đảm bảo thư mục gốc dự án luôn có trong sys.path để hỗ trợ cả:
# 1) python agent/cli.py ...
# 2) python -m agent.cli ...
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Cấu hình encoding UTF-8 cho console Windows tránh lỗi hiển thị tiếng Việt
for stream in (sys.stdout, sys.stderr):
    if isinstance(stream, io.TextIOWrapper):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

try:
    from agent.catalog import default_catalog
except ImportError:
    from catalog import default_catalog


def mock_answer_question(session_id: str, question: str) -> Dict[str, Any]:
    """
    Tạo phản hồi giả lập (Mock) chất lượng cao dựa trên dữ liệu thật của cửa hàng.
    Giúp Toản và nhóm kiểm thử luồng TTS/Avatar độc lập mà không cần LLM API key.
    """
    if not question or not question.strip():
        return {
            "answer": "Dạ em chào bạn ạ! Bạn đang quan tâm đến sản phẩm phụ kiện nào của shop bên em thế ạ?",
            "product_ids": [],
            "status": "need_clarification"
        }

    q_lower = question.strip().lower()

    # Kịch bản 1: Ngoài phạm vi kinh doanh (điện thoại, laptop, thời tiết)
    if any(kw in q_lower for kw in ["iphone", "điện thoại", "laptop dell", "laptop macbook", "mua xe", "quần áo"]):
        return {
            "answer": "Dạ shop em chuyên về phụ kiện máy tính và thiết bị góc làm việc nên hiện chưa kinh doanh mặt hàng này bạn nhé!",
            "product_ids": [],
            "status": "no_data"
        }
    if any(kw in q_lower for kw in ["thời tiết", "mưa", "nắng", "nhiệt độ", "chính trị"]):
        return {
            "answer": "Dạ em là trợ lý bán phụ kiện công nghệ của shop ạ, bạn có cần em tư vấn mẫu chuột, phím hay tai nghe nào đang khuyến mãi không nè!",
            "product_ids": [],
            "status": "no_data"
        }

    # Kịch bản 2: Thiếu dữ liệu thông số (màu sắc, gram, kháng nước IPX)
    if any(kw in q_lower for kw in ["màu gì", "màu hồng", "màu đỏ", "màu sắc", "bao nhiêu gram", "nặng bao nhiêu", "ipx", "chống nước"]):
        matched = default_catalog.search_products(question, limit=1)
        prod_id = [matched[0]["id"]] if matched else []
        return {
            "answer": "Dạ hiện tại hệ thống dữ liệu của em chưa cập nhật thông số chi tiết này, em xin phép ghi nhận để nhân viên kiểm tra kho và phản hồi lại bạn sau nha!",
            "product_ids": prod_id,
            "status": "no_data"
        }

    # Kịch bản 3: Hỏi sản phẩm hết hàng cụ thể (SP003 Delux M618, SP012 Ugreen Hub)
    if any(kw in q_lower for kw in ["delux", "m618", "sp003"]):
        p = default_catalog.get_product("SP003")
        if p is None:
            return {
                "answer": "Dạ hiện tại hệ thống chưa có thông tin chi tiết về mẫu này, em xin phép kiểm tra lại với shop ạ!",
                "product_ids": [],
                "status": "no_data"
            }
        return {
            "answer": f"Dạ mẫu {p['name']} giá {p['price_vnd']:,} VNĐ hiện bên em đang tạm hết hàng rồi ạ, bạn tham khảo sang mẫu Logitech M220 giúp em nhé!",
            "product_ids": ["SP003"],
            "status": "ok"
        }
    if any(kw in q_lower for kw in ["ugreen", "70411", "sp012", "6 in 1"]):
        p = default_catalog.get_product("SP012")
        if p is None:
            return {
                "answer": "Dạ hiện tại hệ thống chưa có thông tin chi tiết về mẫu này, em xin phép kiểm tra lại với shop ạ!",
                "product_ids": [],
                "status": "no_data"
            }
        return {
            "answer": f"Dạ mẫu {p['name']} giá {p['price_vnd']:,} VNĐ hiện đã hết hàng trong kho rồi ạ, shop còn mẫu hub 4 cổng Baseus sẵn hàng bạn nhé!",
            "product_ids": ["SP012"],
            "status": "ok"
        }

    # Kịch bản 4: Tư vấn theo ngân sách cụ thể
    if any(kw in q_lower for kw in ["300k", "300 nghìn", "300.000", "dưới 300"]):
        p = default_catalog.get_product("SP001")
        if p is None:
            return {
                "answer": "Dạ hiện tại hệ thống chưa có thông tin sản phẩm phù hợp với mức giá này, em xin phép kiểm tra lại với shop ạ!",
                "product_ids": [],
                "status": "no_data"
            }
        return {
            "answer": f"Dạ với tầm giá 300k, shop gợi ý ngay mẫu {p['name']} giá chỉ {p['price_vnd']:,} VNĐ, click cực êm không gây tiếng ồn, pin dùng tới 18 tháng rất hợp cho bạn ạ!",
            "product_ids": ["SP001"],
            "status": "ok"
        }
    if any(kw in q_lower for kw in ["dưới 100", "100k", "89k", "giá rẻ"]):
        p = default_catalog.get_product("SP014")
        if p is None:
            return {
                "answer": "Dạ hiện tại hệ thống chưa có thông tin sản phẩm phù hợp với mức giá này, em xin phép kiểm tra lại với shop ạ!",
                "product_ids": [],
                "status": "no_data"
            }
        return {
            "answer": f"Dạ dưới 100k shop có mẫu {p['name']} giá chỉ {p['price_vnd']:,} VNĐ, viền may chắc chắn và chống trượt cực tốt bạn nha!",
            "product_ids": ["SP014"],
            "status": "ok"
        }
    if any(kw in q_lower for kw in ["500k", "dưới 500", "tai nghe zoom", "học online"]):
        p = default_catalog.get_product("SP007")
        if p is None:
            return {
                "answer": "Dạ hiện tại hệ thống chưa có thông tin sản phẩm phù hợp với mức giá này, em xin phép kiểm tra lại với shop ạ!",
                "product_ids": [],
                "status": "no_data"
            }
        return {
            "answer": f"Dạ tầm 500k bạn chọn ngay tai nghe {p['name']} giá {p['price_vnd']:,} VNĐ nhé, mic đàm thoại lọc ồn rất rõ và màng loa 53mm êm ái!",
            "product_ids": ["SP007"],
            "status": "ok"
        }

    # Kịch bản 5: So sánh giữa 2 sản phẩm
    if "so sánh" in q_lower or ("và" in q_lower and any(kw in q_lower for kw in ["khác nhau", "chiếc nào", "hơn"])):
        results = default_catalog.search_products(question, limit=2)
        if len(results) >= 2:
            p1, p2 = results[0], results[1]
            return {
                "answer": f"Dạ so sánh nhanh: mẫu {p1['name']} giá {p1['price_vnd']:,} VNĐ nổi bật với {p1['features'][0]}; còn mẫu {p2['name']} giá {p2['price_vnd']:,} VNĐ thì có {p2['features'][0]}, bạn cân nhắc theo nhu cầu nha!",
                "product_ids": [p1["id"], p2["id"]],
                "status": "ok"
            }

    # Kịch bản chung: Tìm kiếm sản phẩm phù hợp nhất trong Catalog
    matched_products = default_catalog.search_products(question, limit=1)
    if matched_products:
        p = matched_products[0]
        stock_text = "sẵn hàng giao ngay" if p["stock"] > 0 else "đang tạm hết hàng"
        return {
            "answer": f"Dạ shop có mẫu {p['name']} giá {p['price_vnd']:,} VNĐ, hiện đang {stock_text}, bảo hành chính hãng {p['warranty_months']} tháng bạn nhé!",
            "product_ids": [p["id"]],
            "status": "ok"
        }

    # Không xác định được nhu cầu
    return {
        "answer": "Dạ bạn có thể chia sẻ thêm cho em về mức ngân sách dự kiến hoặc nhu cầu sử dụng cụ thể để em tư vấn mẫu phù hợp nhất không ạ?",
        "product_ids": [],
        "status": "need_clarification"
    }


def main():
    parser = argparse.ArgumentParser(description="CLI tương tác với AI Livestream Sales Agent")
    # Cho phép nhận câu hỏi theo cả dạng positional (không cờ) hoặc cờ --question / -q
    parser.add_argument("pos_question", nargs="*", type=str, help="Câu hỏi từ khách hàng (positional)")
    parser.add_argument("-q", "--question", type=str, default=None, help="Câu hỏi từ khách hàng (flag)")
    parser.add_argument("--mock", action="store_true", help="Chạy chế độ giả lập (Mock) không gọi API")
    parser.add_argument("--session-id", type=str, default="cli-session-01", help="Mã phiên hội thoại")

    args = parser.parse_args()

    # Tổng hợp nội dung câu hỏi từ positional hoặc flag
    query = None
    if args.question:
        query = args.question.strip()
    elif args.pos_question:
        query = " ".join(args.pos_question).strip()

    def process_query(user_q: str):
        if args.mock:
            response = mock_answer_question(args.session_id, user_q)
        else:
            try:
                from agent.service import answer_question
                response = answer_question(args.session_id, user_q)
            except ImportError:
                print("[THÔNG BÁO] Chưa cấu hình mô-đun LLM service. Đang chuyển sang chế độ Mock:", file=sys.stderr)
                response = mock_answer_question(args.session_id, user_q)
            except Exception as e:
                response = {
                    "answer": "Dạ kết nối của hệ thống đang bảo trì, bạn thử lại sau nhé!",
                    "product_ids": [],
                    "status": "error"
                }

        print(json.dumps(response, ensure_ascii=False, indent=2))

    if query:
        process_query(query)
    else:
        # Chế độ tương tác liên tục (Interactive REPL)
        print("=== AI LIVESTREAM SALES AGENT CLI ===")
        print(f"Chế độ: {'MOCK (Giả lập)' if args.mock else 'LLM Service (API)'}")
        print("Nhập câu hỏi của bạn (gõ 'exit' hoặc 'quit' để thoát):\n")

        while True:
            try:
                user_q = input("Khách xem livestream hỏi > ").strip()
                if not user_q:
                    continue
                if user_q.lower() in ["exit", "quit", "q"]:
                    print("Tạm biệt!")
                    break
                process_query(user_q)
                print()
            except (KeyboardInterrupt, EOFError):
                print("\nKết thúc phiên CLI.")
                break


if __name__ == "__main__":
    main()
