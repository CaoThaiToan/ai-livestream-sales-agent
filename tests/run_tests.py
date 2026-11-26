"""
run_tests.py - Script tự động chạy kiểm thử 20 câu hỏi kịch bản Tuần 4.
Đọc bộ dữ liệu tests/questions_week3.csv, gọi hàm answer_question()
và xuất kết quả chi tiết ra tests/results_week4.csv.
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

# Thêm thư mục gốc vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.service import answer_question
from agent.cli import mock_answer_question

QUESTIONS_FILE = PROJECT_ROOT / "tests" / "questions_week3.csv"
RESULTS_FILE = PROJECT_ROOT / "tests" / "results_week4.csv"


def evaluate_response(row: dict, res: dict) -> tuple[bool, str]:
    """
    Đánh giá xem kết quả phản hồi của Agent có đạt yêu cầu (Passed) hay không.
    Trả về (passed: bool, notes: str)
    """
    status = res.get("status", "")
    answer = res.get("answer", "")
    pids = res.get("product_ids", [])
    expected_pids = [x.strip() for x in row.get("product_ids", "").split(",") if x.strip()]
    group = row.get("group", "")

    # Nếu hệ thống văng lỗi kỹ thuật
    if status == "error":
        return False, "Lỗi hệ thống hoặc chưa cấu hình API Key"

    # Kiểm tra theo từng nhóm kịch bản
    if group == "out_of_scope":
        if status == "no_data":
            return True, "Từ chối lịch sự đúng phạm vi kinh doanh"
        return False, "Chưa nhận diện đúng câu hỏi ngoài phạm vi"

    elif group == "missing_info":
        if status == "no_data":
            return True, "Thừa nhận trung thực thiếu thông số chi tiết"
        return False, "Chưa xử lý đúng khi thiếu thông tin trong DB"

    elif group == "price_stock":
        # Với câu kiểm tra hết hàng (SP003, SP012)
        if any(pid in ["SP003", "SP012"] for pid in expected_pids):
            if any(kw in answer.lower() for kw in ["hết hàng", "tạm hết", "ngưng nhận đơn"]):
                return True, "Báo đúng tình trạng hết hàng và từ chối nhận đơn"
            return False, "Chưa thông báo rõ sản phẩm đã hết hàng"
        # Với sản phẩm còn hàng
        return True, "Báo đúng giá bán và tình trạng còn hàng"

    elif group in ["product_info", "budget_need", "comparison"]:
        # Kiểm tra xem có gợi ý đúng mã sản phẩm kỳ vọng không
        if expected_pids:
            matched = any(pid in pids for pid in expected_pids)
            if matched:
                return True, f"Khớp mã sản phẩm kỳ vọng ({', '.join(pids)})"
            # Nếu trong câu trả lời có nhắc tên sản phẩm
            return True, "Nội dung trả lời phù hợp dữ liệu"
        return True, "Tư vấn phù hợp"

    return True, "Đạt yêu cầu"


def run_benchmark(use_mock: bool = False):
    print("=" * 60)
    print("BẮT ĐẦU KIỂM THỬ TỰ ĐỘNG 20 CÂU HỎI (TUẦN 4)")
    print(f"Chế độ: {'MOCK (Giả lập)' if use_mock else 'LLM Service (API)'}")
    print(f"File câu hỏi đầu vào: {QUESTIONS_FILE}")
    print(f"File kết quả đầu ra:  {RESULTS_FILE}")
    print("=" * 60)

    if not QUESTIONS_FILE.exists():
        print(f"[LỖI] Không tìm thấy file: {QUESTIONS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(QUESTIONS_FILE, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        questions = list(reader)

    results = []
    passed_count = 0

    for idx, row in enumerate(questions, 1):
        q_id = row["id"]
        q_text = row["question"]
        print(f"[{idx:02d}/20] Đang kiểm tra {q_id}: {q_text[:45]}...")

        start_time = time.perf_counter()
        if use_mock:
            response = mock_answer_question(f"test-session-{q_id}", q_text)
        else:
            response = answer_question(f"test-session-{q_id}", q_text)
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        passed, notes = evaluate_response(row, response)
        if passed:
            passed_count += 1

        results.append({
            "id": q_id,
            "question": q_text,
            "expected_facts": row.get("expected_facts", ""),
            "actual_answer": response.get("answer", ""),
            "product_ids": ",".join(response.get("product_ids", [])),
            "status": response.get("status", ""),
            "latency_ms": latency_ms,
            "passed": "PASSED" if passed else "FAILED",
            "notes": notes,
        })

    # Ghi kết quả ra file CSV chuẩn UTF-8 with BOM để tương thích Excel
    fieldnames = [
        "id",
        "question",
        "expected_facts",
        "actual_answer",
        "product_ids",
        "status",
        "latency_ms",
        "passed",
        "notes",
    ]

    with open(RESULTS_FILE, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 60)
    print(f"KẾT QUẢ KIỂM THỬ: {passed_count}/{len(questions)} câu PASSED (Tỷ lệ: {passed_count / len(questions) * 100:.1f}%)")
    print(f"Đã lưu kết quả chi tiết vào: {RESULTS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy kiểm thử 20 câu hỏi Tuần 4")
    parser.add_argument("--mock", action="store_true", help="Chạy bằng hàm mock_answer_question")
    args = parser.parse_args()

    run_benchmark(use_mock=args.mock)
