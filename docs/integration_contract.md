# Hợp Đồng Tích Hợp Mô-đun AI Agent (Integration Contract)

**Đồ án:** AI Agent Livestream Bán Hàng  
**Thành viên thực hiện:** Quỳnh (AI Sales Agent) & Toản (LiveTalking / Avatar & Hạ tầng)  
**Cập nhật:** Tuần 4  
**Trạng thái:** Đã thống nhất (Approved)  

---

## 1. Mục Đích & Nguyên Tắc Tích Hợp
- **Mục đích:** Xác lập giao diện lập trình (API/Chữ ký hàm) và định dạng dữ liệu chuẩn giữa mô-đun tư vấn sản phẩm (`agent/`) của Quỳnh và hệ thống trình chiếu Avatar LiveTalking của Toản.
- **Tính độc lập:** Mô-đun `agent/` hoạt động hoàn toàn độc lập, **tuyệt đối không import các thư viện nặng** của LiveTalking (như `torch`, `torchvision`, `cuda`, `cv2`, `webrtc`). Toản có thể gọi trực tiếp qua hàm Python nội bộ hoặc bọc thành REST API / WebSocket service.
- **Tính tương thích âm thanh (TTS-friendly):** Trường dữ liệu văn bản trả về (`answer`) được định dạng để bộ chuyển đổi giọng nói (Text-To-Speech) đọc tự nhiên, tránh ký tự lạ, bảng biểu phức tạp hoặc markdown khó đọc.

---

## 2. Giao Diện Lập Trình (Function Signature)

```python
def answer_question(session_id: str, question: str) -> dict:
    """
    Tiếp nhận câu hỏi từ khán giả livestream và trả về phản hồi tư vấn chuẩn hóa.
    
    Tham số:
        session_id (str): Mã định danh phiên livestream hoặc người dùng (VD: "live-session-01", "user-102").
        question (str): Chuỗi nội dung câu hỏi hoặc bình luận của khách xem livestream.
        
    Trả về:
        dict: Cấu trúc từ điển JSON chuẩn hóa chứa nội dung câu trả lời, danh sách mã sản phẩm và mã trạng thái.
    """
```

---

## 3. Quy Chuẩn Dữ Liệu (Data Schema)

### 3.1. Dữ liệu đầu vào (Input)
| Trường | Kiểu dữ liệu | Bắt buộc | Mô tả | Ví dụ |
|:---|:---|:---:|:---|:---|
| `session_id` | `str` | Có | Định danh phiên/người xem để phân biệt ngữ cảnh | `"demo-01"` |
| `question` | `str` | Có | Nội dung bình luận tiếng Việt của khách | `"Tôi cần chuột không dây dưới 300 nghìn"` |

```json
{
  "session_id": "demo-01",
  "question": "Tôi cần chuột không dây dưới 300 nghìn"
}
```

### 3.2. Dữ liệu đầu ra (Output)
| Trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
|:---|:---|:---:|:---|
| `answer` | `str` | Có | Câu trả lời tiếng Việt tự nhiên, ngắn gọn, dùng để truyền trực tiếp vào TTS đọc thành tiếng. |
| `product_ids` | `list[str]` | Có | Danh sách các mã sản phẩm được đề cập (trích xuất từ `products.json`). Nếu không có sản phẩm cụ thể, trả về mảng rỗng `[]`. |
| `status` | `str` | Có | Trạng thái xử lý của Agent, gồm 4 giá trị quy ước: `"ok"`, `"need_clarification"`, `"no_data"`, `"error"`. |

```json
{
  "answer": "Dạ bên em có chuột không dây Silent Logitech M220 giá chỉ 299 nghìn, bấm êm không gây tiếng ồn, rất hợp với ngân sách của bạn ạ!",
  "product_ids": ["SP001"],
  "status": "ok"
}
```

---

## 4. Bảng Quy Ước Giá Trị `status`

| Giá trị `status` | Ý nghĩa | Tình huống kích hoạt | Hành động của Avatar / Hệ thống Toản |
|:---|:---|:---|:---|
| `"ok"` | Xử lý thành công | Tìm thấy sản phẩm, giải đáp đầy đủ thông số, giá bán, tồn kho hoặc chính sách. | TTS đọc câu thoại `answer`, có thể hiển thị popup card sản phẩm lên livestream dựa vào `product_ids`. |
| `"need_clarification"` | Cần làm rõ nhu cầu | Nhu cầu của khách mơ hồ (chưa rõ ngân sách, thiết bị sử dụng, làm việc hay chơi game). | TTS đọc câu hỏi gợi ý thêm, chờ khán giả bình luận tiếp. |
| `"no_data"` | Không có thông tin | Thông số bị thiếu trong DB, sản phẩm shop không bán, hoặc câu hỏi ngoài phạm vi cửa hàng. | TTS đọc lời giải thích / từ chối lịch sự theo quy tắc trung thực của shop. |
| `"error"` | Lỗi hệ thống | Mất mạng, timeout API LLM, hết quota hoặc phản hồi bị lỗi định dạng. | TTS đọc câu thông báo dự phòng lịch sự (không để lộ lỗi stack trace hay code). |

---

## 5. Ví Dụ Các Kịch Bản Phản Hồi

### Kịch bản 1: Tư vấn thành công theo ngân sách (`status: ok`)
* **Input:** `{"session_id": "s1", "question": "Có tai nghe gaming nào dưới 500k mic đàm thoại rõ không?"}`
* **Output:**
```json
{
  "answer": "Dạ shop có mẫu tai nghe chụp tai gaming Havit H2002D giá 490 nghìn, micro đàm thoại khử ồn cực tốt và màng loa 53mm âm bass chắc khỏe bạn nhé!",
  "product_ids": ["SP007"],
  "status": "ok"
}
```

### Kịch bản 2: Sản phẩm hết hàng (`status: ok`)
* **Input:** `{"session_id": "s1", "question": "Chuột Delux M618 Mini bên mình còn hàng không shop?"}`
* **Output:**
```json
{
  "answer": "Dạ chuột công thái học Delux M618 Mini giá 550 nghìn hiện bên em đang tạm hết hàng rồi ạ, bạn tham khảo sang mẫu Logitech M220 giúp em nhé!",
  "product_ids": ["SP003"],
  "status": "ok"
}
```

### Kịch bản 3: Thiếu dữ liệu thông số trong hệ thống (`status: no_data`)
* **Input:** `{"session_id": "s1", "question": "Chuột Logitech M220 bên bạn có màu hồng không?"}`
* **Output:**
```json
{
  "answer": "Dạ hiện tại hệ thống của em chưa cập nhật thông tin về màu sắc này, em xin phép ghi nhận để nhân viên kiểm tra kho và phản hồi lại bạn sau nha!",
  "product_ids": ["SP001"],
  "status": "no_data"
}
```

### Kịch bản 4: Câu hỏi ngoài phạm vi cửa hàng (`status: no_data`)
* **Input:** `{"session_id": "s1", "question": "Shop có bán điện thoại iPhone 15 Pro Max không?"}`
* **Output:**
```json
{
  "answer": "Dạ shop em chuyên về phụ kiện máy tính và thiết bị công nghệ bàn làm việc nên hiện chưa kinh doanh điện thoại bạn nhé!",
  "product_ids": [],
  "status": "no_data"
}
```

### Kịch bản 5: Lỗi kỹ thuật / API Timeout (`status: error`)
* **Input:** `{"session_id": "s1", "question": "Tư vấn cho mình chuột máy tính"}`
* **Output:**
```json
{
  "answer": "Dạ đường truyền kết nối của em vừa bị gián đoạn đôi chút, bạn chờ em một giây hoặc để lại bình luận để em tư vấn ngay nhé!",
  "product_ids": [],
  "status": "error"
}
```

---

## 6. Phương Án Tích Hợp Vào LiveTalking (Phía Toản)

Toản có thể tích hợp mô-đun của Quỳnh vào pipeline LiveTalking theo 2 cách:

1. **Gọi trực tiếp trong mã nguồn Python (Khuyến nghị):**
   ```python
   from agent.service import answer_question
   
   # Khi nhận được comment từ livestream:
   result = answer_question(session_id="live-01", question=user_comment)
   tts_text = result["answer"]
   
   # Đẩy vào luồng LiveTalking TTS & Avatar:
   tts_engine.speak(tts_text)
   ```

2. **Chế độ chạy thử không tốn API (Mock mode):**
   Toản có thể chạy lệnh CLI với cờ `--mock` để nhận dữ liệu giả lập ngay lập tức mà không cần cấu hình API key:
   ```powershell
   python -m agent.cli --mock "Tôi cần chuột dưới 300 nghìn"
   ```
