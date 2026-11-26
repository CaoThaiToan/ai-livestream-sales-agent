# Báo Cáo Kết Quả Thực Hiện Tuần 4 (Week 4 Result)

**Đồ án:** AI Agent Livestream Bán Hàng  
**Thành viên thực hiện:** Quỳnh  
**Vai trò:** Phát triển mô-đun tư vấn sản phẩm AI Sales Agent (`agent/`) & Kiểm thử  
**Người phụ trách tích hợp:** Toản (LiveTalking / Avatar & Hạ tầng)  
**Thời gian hoàn thành:** 26/11/2026  
**Nhánh Git:** `feature/product-agent`  

---

## 1. Tổng Quan Tiến Độ & Mục Tiêu Đạt Được

Trong Tuần 4, Quỳnh đã hoàn thành toàn bộ các đầu việc từ Bước 1 đến Bước 10 theo đúng tài liệu hướng dẫn và quy trình Git Workflow mới nhất:

| STT | Đầu việc | Kết quả | Trạng thái |
|:---:|:---|:---|:---:|
| 1 | Đồng bộ nhánh cá nhân & môi trường | Git branch `feature/product-agent` cập nhật từ `origin/main` | Hoàn thành |
| 2 | Chốt hợp đồng tích hợp | `docs/integration_contract.md` quy chuẩn JSON đầu ra | Hoàn thành |
| 3 | Mô-đun tra cứu dữ liệu | `agent/catalog.py` nạp, xác thực, lọc ngân sách, tìm kiếm | Hoàn thành |
| 4 | Giao diện dòng lệnh CLI & Mock | `agent/cli.py` hỗ trợ tương tác console & cờ `--mock` | Hoàn thành |
| 5 | Quản lý phụ thuộc & Bảo mật Git | `requirements-agent.txt`, cập nhật `.env.example`, bảo vệ `.gitignore` | Hoàn thành |
| 6 | Thiết kế System Prompt tư vấn | `agent/prompts.py` chuẩn TTS, trung thực, kháng injection | Hoàn thành |
| 7 | Kết nối LLM & Xử lý ngoại lệ | `agent/service.py` triển khai `answer_question()` chuẩn hóa | Hoàn thành |
| 8 | Kiểm thử tự động 20 câu hỏi | `tests/run_tests.py` xuất kết quả ra `tests/results_week4.csv` | Hoàn thành |
| 9 | Báo cáo kỹ thuật tổng kết | `docs/week4_result.md` | Hoàn thành |
| 10 | Bàn giao & Tạo Pull Request | Commit sạch, mở Pull Request trên GitHub cho Toản | Hoàn thành |

---

## 2. Thông Số Kỹ Thuật Mô-Đun Agent

- **Ngôn ngữ:** Python 3.12 / Python 3.14 compatible.
- **SDK chính:** `openai>=1.0.0` (tương thích OpenAI, Groq, Gemini OpenAI Endpoint, DeepSeek, DashScope), `python-dotenv>=1.0.0`, `requests>=2.31.0`.
- **Kiến trúc mô-đun:**
  - `agent/catalog.py`: Quản lý danh mục 15 sản phẩm và chính sách cửa hàng; nạp context tối ưu không vượt ngưỡng token.
  - `agent/prompts.py`: Thiết lập prompt nghiêm ngặt, ép định dạng đầu ra JSON chuẩn:
    ```json
    {
      "answer": "string",
      "product_ids": ["SP001"],
      "status": "ok"
    }
    ```
  - `agent/service.py`: Cổng giao tiếp chính (`answer_question`), xác thực mã sản phẩm tồn tại trong database, xử lý an toàn lỗi mạng/quota/timeout mà không để lộ stack trace.
  - `agent/cli.py`: Hỗ trợ Toản kiểm thử ngay luồng TTS/Avatar bằng cờ `--mock` độc lập mà không tiêu tốn API Key.

---

## 3. Kết Quả Kiểm Thử Tự Động 20 Câu Hỏi (`tests/results_week4.csv`)

Toàn bộ 20 câu hỏi phân loại theo 6 nhóm kịch bản từ `tests/questions_week3.csv` đã được đánh giá qua script tự động `tests/run_tests.py`:

- **Tổng số câu kiểm thử:** 20 câu.
- **Số câu đạt chuẩn (Passed):** 20/20 câu (Tỷ lệ: 100%).
- **Đánh giá chi tiết theo nhóm kịch bản:**
  1. `product_info` (Q01 - Q04): Trả lời chính xác thông số, tính năng, cổng kết nối và bảo hành của sản phẩm.
  2. `price_stock` (Q05 - Q08): Báo đúng giá niêm yết; đặc biệt phát hiện chính xác các sản phẩm hết hàng (`SP003`, `SP012`), từ chối nhận đơn theo đúng quy định.
  3. `budget_need` (Q09 - Q12): Tư vấn chuẩn xác sản phẩm nằm trong tầm giá dưới 100k, 300k, 500k và phù hợp với mục đích học tập/văn phòng.
  4. `comparison` (Q13 - Q15): So sánh trực quan sự khác biệt về kết nối, tính năng nổi bật giữa hai sản phẩm được hỏi.
  5. `missing_info` (Q16 - Q18): Thừa nhận trung thực dữ liệu hệ thống chưa có chi tiết thông số (màu sắc, gram cân nặng, chuẩn IPX), không tự ý bịa đặt thông tin.
  6. `out_of_scope` (Q19 - Q20): Nhắc nhở lịch sự phạm vi kinh doanh của shop khi khách hỏi điện thoại iPhone hoặc thời tiết ngoài lề.

---

## 4. Hạn Chế Hiện Tại & Định Hướng Tuần 5

### 4.1. Hạn chế hiện tại
- **Quản lý hội thoại:** Hiện tại mới xử lý theo từng lượt tương tác đơn lẻ (`session_id`), chưa lưu ngữ cảnh bộ nhớ dài hạn (Multi-turn conversational memory).
- **Hàng đợi bình luận livestream:** Chưa có cơ chế lọc trùng và xếp hàng ưu tiên bình luận khi có nhiều khán giả chat đồng thời.

### 4.2. Định hướng triển khai Tuần 5
- Tích hợp bộ nhớ ngắn hạn cho từng session để hỗ trợ các câu hỏi tiếp nối ("còn mẫu nào khác nữa không shop?", "cái vừa rồi bảo hành sao?").
- Xây dựng hàng đợi bình luận (Comment Queue) và kết nối đồng bộ thời gian thực với mô-đun TTS/Avatar của Toản.
