"""
service.py - Mô-đun kết nối LLM API và cung cấp hàm answer_question() cho hệ thống.
Tuân thủ nghiêm ngặt Hợp đồng tích hợp (docs/integration_contract.md).
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

# Tự động nạp biến môi trường từ file .env nếu có
try:
    from dotenv import load_dotenv
    # Tìm file .env ở thư mục gốc dự án
    ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH)
    else:
        load_dotenv()
except ImportError:
    pass

from agent.catalog import default_catalog
from agent.prompts import build_system_prompt, build_user_prompt
from agent.query import select_products

logger = logging.getLogger(__name__)

# Danh sách status hợp lệ theo Hợp đồng tích hợp
VALID_STATUSES = {"ok", "need_clarification", "no_data", "error"}


def _extract_json(text: str) -> Dict[str, Any]:
    """Bóc tách và phân tích JSON từ chuỗi phản hồi của LLM."""
    text = text.strip()
    # Nếu kết quả nằm trong khối markdown ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def _validate_response(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kiểm tra và chuẩn hóa cấu trúc dữ liệu phản hồi theo đúng Schema:
    - answer: str (không rỗng)
    - product_ids: list[str] (mỗi mã phải tồn tại trong products.json)
    - status: str (thuộc 4 giá trị quy ước)
    """
    answer = str(parsed.get("answer", "")).strip()
    if not answer:
        answer = "Dạ bên em sẵn sàng hỗ trợ, bạn cần em tư vấn thêm gì không ạ?"

    raw_product_ids = parsed.get("product_ids", [])
    if not isinstance(raw_product_ids, list):
        raw_product_ids = [str(raw_product_ids)]

    # Lọc chỉ giữ lại các mã sản phẩm có thật trong cơ sở dữ liệu
    valid_ids: List[str] = []
    for pid in raw_product_ids:
        pid_clean = str(pid).strip()
        if pid_clean and default_catalog.get_product(pid_clean) is not None:
            if pid_clean not in valid_ids:
                valid_ids.append(pid_clean)

    status = str(parsed.get("status", "ok")).strip()
    if status not in VALID_STATUSES:
        status = "ok"

    return {
        "answer": answer,
        "product_ids": valid_ids,
        "status": status,
    }


def answer_question(session_id: str, question: str) -> Dict[str, Any]:
    """
    Tiếp nhận câu hỏi từ khán giả livestream và trả về phản hồi tư vấn chuẩn hóa.
    
    Tham số:
        session_id (str): Mã định danh phiên livestream hoặc người dùng.
        question (str): Nội dung câu hỏi/bình luận tiếng Việt.
        
    Trả về:
        dict: {
            "answer": str,
            "product_ids": list[str],
            "status": "ok" | "need_clarification" | "no_data" | "error"
        }
    """
    if not question or not question.strip():
        return {
            "answer": "Dạ em chào bạn ạ! Bạn đang quan tâm đến sản phẩm phụ kiện nào của shop bên em thế ạ?",
            "product_ids": [],
            "status": "need_clarification",
        }

    user_q = question.strip()

    # Cấu hình LLM từ biến môi trường
    provider = (os.getenv("LLM_PROVIDER") or "openai").strip().lower()
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        default_model = "gemini-3.5-flash-lite"
        default_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    else:
        api_key = (
            os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("GROQ_API_KEY")
            or os.getenv("DASHSCOPE_API_KEY")
        )
        default_model = "gpt-4o-mini"
        default_base_url = None

    model = os.getenv("LLM_MODEL") or default_model
    base_url = os.getenv("LLM_BASE_URL") or default_base_url

    # Nếu chưa cấu hình API Key: trả về thông báo lịch sự đúng chuẩn contract
    if not api_key:
        return {
            "answer": "Dạ hệ thống AI chưa nhận được cấu hình API Key. Bạn vui lòng kiểm tra file .env nhé!",
            "product_ids": [],
            "status": "error",
        }

    try:
        from openai import OpenAI

        client_kwargs: Dict[str, Any] = {"api_key": api_key, "timeout": 25.0}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = OpenAI(**client_kwargs)

        # Tra cứu điều kiện trước khi Gemini diễn đạt câu trả lời.
        products, lookup_instruction = select_products(default_catalog, user_q)
        selected_ids = {product["id"] for product in products}
        logger.info("Product lookup selected=%s", sorted(selected_ids))
        context = default_catalog.format_context_for_prompt(products)
        context += "\n\n=== KẾT QUẢ ĐỐI CHIẾU ĐIỀU KIỆN ===\n" + lookup_instruction
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(user_q, context)

        # Gọi LLM
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"} if "gpt" in model or "deepseek" in model else None,
        )

        content = completion.choices[0].message.content or ""
        parsed = _extract_json(content)
        response = _validate_response(parsed)
        if not set(response["product_ids"]).issubset(selected_ids):
            raise ValueError("Agent returned a product outside the lookup result")
        return response

    except Exception as e:
        # Ghi log ra stderr để debug, nhưng đầu ra trả về người dùng / TTS vẫn tuân thủ schema bảo vệ
        print(f"[ERROR] LLM Service encountered an error: {e}", file=sys.stderr)
        return {
            "answer": "Dạ kết nối của hệ thống đang bảo trì, bạn thử lại sau nhé!",
            "product_ids": [],
            "status": "error",
        }
