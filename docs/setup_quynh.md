# Hướng Dẫn & Ghi Chú Thiết Lập Môi Trường (Máy Quỳnh)

**Đồ án:** Nghiên cứu, xây dựng và phát triển AI Agents hỗ trợ tự động hóa trong hoạt động Marketing (AI Livestream Sales Agent)  
**Người thực hiện:** Quỳnh  
**Cập nhật:** Tuần 3  

---

## 1. Thông Số Phần Cứng Máy Thực Tế
- **Hệ điều hành:** Windows 10/11 64-bit
- **Bộ vi xử lý (CPU):** Intel Core thế hệ tương thích tích hợp Intel UHD Graphics 620
- **Bộ nhớ RAM:** 16 GB
- **Card đồ họa:** Intel UHD Graphics 620 (GPU tích hợp, không có NVIDIA CUDA)
- **Định hướng tối ưu:**
  - Máy Quỳnh tập trung phát triển phân hệ **Dữ liệu sản phẩm**, **Logic tư vấn bán hàng bằng văn bản (LLM Agent)** và **Đánh giá kiểm thử**.
  - Không yêu cầu cài đặt CUDA Toolkit, PyTorch GPU nặng hay tải các mô hình trọng số của LiveTalking (Wav2Lip / MuseTalk). Toàn bộ hạ tầng GPU và render Avatar do Toản quản lý trên máy chủ/máy riêng.

---

## 2. Phần Mềm & Công Cụ Yêu Cầu
- **Python:** Phiên bản `3.12.x` (đã kiểm tra `py -3.12 --version`)
- **Git:** Git for Windows (đã cấu hình SSH/HTTPS)
- **Code Editor:** Visual Studio Code

---

## 3. Các Bước Thiết Lập Thực Tế Đã Thực Hiện

### Bước 1: Clone Repository & Chuyển Branch
```powershell
# Clone repo chung của nhóm
git clone https://github.com/CaoThaiToan/ai-livestream-sales-agent.git
cd ai-livestream-sales-agent

# Chuyển sang nhánh tính năng làm việc của Quỳnh
git checkout feature/product-agent
```

### Bước 2: Tạo Môi Trường Ảo Python (.venv)
```powershell
# Khởi tạo venv với Python 3.12
py -3.12 -m venv .venv

# Kiểm tra python và pip trong venv
.\.venv\Scripts\python.exe --version
# Output: Python 3.12.0
.\.venv\Scripts\python.exe -m pip --version
```

### Bước 3: Đảm Bảo Không Push Thư Viện Lên Git (.gitignore)
Kiểm tra file `.gitignore` ở thư mục gốc để đảm bảo các dòng sau đã được kích hoạt:
```text
.venv/
.env
.env.*
!.env.example
__pycache__/
*.pyc
```

---

## 4. Kiểm Tra Tính Toàn Vẹn Của Dữ Liệu
```powershell
# Kiểm tra cú pháp JSON của danh mục sản phẩm
.\.venv\Scripts\python.exe -m json.tool data\products.json > $null
# Đảm bảo không có lỗi trả về
```
