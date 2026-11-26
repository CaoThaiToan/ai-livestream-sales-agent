# Nhật Ký Kết Quả Thực Hiện Tuần 3 (Week 3 Result)

**Đồ án:** AI Agent Livestream Bán Hàng  
**Thành viên thực hiện:** Quỳnh  
**Vai trò:** Xây dựng dữ liệu sản phẩm, chính sách và bộ kịch bản kiểm thử  
**Người phụ trách tích hợp:** Toản  
**Thời gian hoàn thành:** 23/11/2026  

---

## 1. Tổng Quan Tiến Độ & Mục Tiêu Đạt Được
Theo hướng dẫn công việc Tuần 3, Quỳnh đã hoàn thành toàn bộ các đầu việc từ Bước 1 đến Bước 8 trên nhánh cá nhân `feature/product-agent`:

| STT | Đầu việc | Kết quả | Trạng thái |
|:---:|:---|:---|:---:|
| 1 | Môi trường lập trình | Python 3.12, .venv cục bộ, kiểm tra .gitignore | Hoàn thành |
| 2 | Danh mục sản phẩm | `data/products.json` gồm 15 sản phẩm phụ kiện công nghệ | Hoàn thành |
| 3 | Chính sách cửa hàng | `data/store_policy.md` chuẩn 5 mục chính, dán nhãn mô phỏng | Hoàn thành |
| 4 | Bộ câu hỏi kiểm thử | `tests/questions_week3.csv` gồm 20 câu hỏi chuẩn hóa 6 nhóm | Hoàn thành |
| 5 | Tài liệu hướng dẫn | `docs/setup_quynh.md`, `docs/data_sources.md`, `docs/week3_result.md` | Hoàn thành |
| 6 | Cấu trúc thư mục Agent | `agent/__init__.py` sẵn sàng cho Tuần 4 | Hoàn thành |

---

## 2. Thống Kê & Chi Tiết Sản Phẩm Bàn Giao

### 2.1. Danh mục sản phẩm (`data/products.json`)
- **Tổng số lượng:** 15 sản phẩm.
- **Ngành hàng:** Phụ kiện máy tính, thiết bị ngoại vi và đồ dùng bàn làm việc.
- **Phân khúc giá:**
  - Dưới 100.000 VNĐ: 1 sản phẩm (Lót chuột cỡ lớn - 89.000 VNĐ).
  - Từ 100.000 – 500.000 VNĐ: 8 sản phẩm (Chuột M220, Razer DeathAdder, Tai nghe Havit, Hub Baseus, Giá đỡ Orico, Webcam Rapoo, Đèn Baseus, Hub Ugreen).
  - Từ 500.000 – 1.000.000 VNĐ: 4 sản phẩm (Chuột Delux, Phím DareU, Phím K380, Tai nghe Baseus ANC).
  - Trên 1.000.000 VNĐ: 2 sản phẩm (Phím FL-Esports - 1.450.000 VNĐ, Tai nghe Sony ANC - 2.290.000 VNĐ).
- **Trạng thái tồn kho đặc biệt:**
  - `SP003` (Chuột công thái học Delux M618 Mini): `stock = 0` (Hết hàng).
  - `SP012` (Hub chuyển đổi USB-C 6 in 1 Ugreen): `stock = 0` (Hết hàng).
  *(Phục vụ kiểm thử tính năng phát hiện hết hàng và từ chối bán của AI Agent)*.

### 2.2. Chính sách cửa hàng (`data/store_policy.md`)
- Quy định rõ phạm vi giao hàng toàn quốc, giao hỏa tốc nội thành 2-4h.
- Miễn phí vận chuyển cho đơn hàng từ 300.000 VNĐ.
- Đổi trả 1 đổi 1 trong 7 ngày đối với lỗi nhà sản xuất.
- Thời hạn bảo hành từ 3 – 24 tháng theo từng sản phẩm.
- Quy chuẩn ứng xử cho AI Agent: không bịa đặt khi thiếu thông tin, gợi ý làm rõ nhu cầu khách.

### 2.3. Bộ 20 câu hỏi kiểm thử (`tests/questions_week3.csv`)
Cơ cấu phân bổ đầy đủ theo 6 nhóm yêu cầu:
1. `product_info` (4 câu: Q01 - Q04): Kiểm tra truy xuất tính năng sản phẩm.
2. `price_stock` (4 câu: Q05 - Q08): Kiểm tra báo giá và phân biệt còn hàng / hết hàng.
3. `budget_need` (4 câu: Q09 - Q12): Tư vấn theo khoảng ngân sách và mục đích sử dụng.
4. `comparison` (3 câu: Q13 - Q15): So sánh chi tiết ưu/nhược điểm 2 sản phẩm.
5. `missing_info` (3 câu: Q16 - Q18): Kiểm tra khả năng từ chối bịa đặt thông số không có trong DB.
6. `out_of_scope` (2 câu: Q19 - Q20): Xử lý câu hỏi ngoài ngành hàng hoặc câu hỏi thời tiết ngoài lề.

---

## 3. Kết Quả Kiểm Tra Tính Hợp Lệ Kỹ Thuật (Validation)
1. **Kiểm tra JSON Schema:**
   - Lệnh thực thi: `python -m json.tool data/products.json`
   - Kết quả: **PASSED (Hợp lệ, không có lỗi cú pháp)**.
2. **Kiểm tra mã hóa CSV:**
   - Định dạng: UTF-8 with BOM (`utf-8-sig`), tương thích tốt với cả Excel và các thư viện đọc dữ liệu Python/Pandas.
   - Kết quả: 20 dòng dữ liệu, 6 cột trường thông tin chuẩn xác.
3. **Kiểm tra Git Workspace:**
   - Nhánh hiện tại: `feature/product-agent`.
   - Các thư mục thư viện nặng (`.venv/`), file môi trường cục bộ (`.env`) đã được bỏ qua an toàn qua `.gitignore`.

---

## 4. Kế Hoạch Tuần 4 Tiếp Theo
- Xây dựng mô-đun tư vấn bán hàng độc lập trong thư mục `agent/`:
  - `agent/catalog.py`: Xây dựng hàm đọc và tìm kiếm sản phẩm.
  - `agent/prompts.py`: Thiết kế System Prompt tối ưu cho giọng đọc TTS của Avatar.
  - `agent/service.py`: Tích hợp gọi LLM API và bọc hàm chuẩn `answer_question(session_id, question)`.
  - `agent/cli.py`: Hỗ trợ kiểm thử trực tiếp trên dòng lệnh và chế độ `--mock`.
- Chạy tự động 20 câu hỏi kiểm thử và xuất kết quả `tests/results_week4.csv`.
- Phối hợp với Toản để thử nghiệm toàn luồng với TTS và Avatar của LiveTalking.
