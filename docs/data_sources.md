# Nguồn Gốc Dữ Liệu & Phương Pháp Xây Dựng (Data Sources)

**Đồ án:** AI Agent Livestream Bán Hàng  
**Thực hiện:** Quỳnh  
**Cập nhật:** Tuần 3

---

## 1. Bản Chất & Phân Loại Dữ Liệu

Toàn bộ dữ liệu sản phẩm trong [data/products.json](file:///C:/bell/%C4%91acn/ai-livestream-sales-agent/data/products.json) và chính sách cửa hàng trong [data/store_policy.md](file:///C:/bell/%C4%91acn/ai-livestream-sales-agent/data/store_policy.md) đều được gắn nhãn:

```json
"data_type": "simulated"
```

**Mục đích:** Phục vụ nghiên cứu, xây dựng thuật toán tư vấn và đánh giá kiểm thử mô hình AI Agent trong môi trường học thuật, không phục vụ mục đích thương mại trực tiếp.

---

## 2. Phương Pháp Xây Dựng Danh Mục Sản Phẩm (products.json)

Danh mục được xây dựng dựa trên khảo sát thực tế thị trường phụ kiện máy tính và thiết bị ngoại vi tại Việt Nam (tham khảo thông số từ các thương hiệu phổ biến: Logitech, Razer, DareU, Baseus, Ugreen, Sony):

- **Quy mô danh mục:** 15 sản phẩm.
- **Các nhóm ngành hàng đại diện:**
  1. _Chuột máy tính:_ Chuột không dây văn phòng chống ồn, chuột gaming có dây, chuột công thái học.
  2. _Bàn phím:_ Bàn phím không dây đa thiết bị, bàn phím cơ TKL, bàn phím cơ custom 3-mode.
  3. _Tai nghe:_ Tai nghe gaming over-ear có mic đàm thoại, tai nghe True Wireless ANC, tai nghe chụp tai chống ồn cao cấp.
  4. _Webcam:_ Webcam Full HD 1080P cho học tập, họp trực tuyến và livestream.
  5. _Giá đỡ & Phụ kiện bàn làm việc:_ Giá đỡ laptop nhôm tản nhiệt, lót chuột khổ lớn, đèn kẹp màn hình chống cận.
  6. _Hub & Cáp chuyển đổi:_ Hub Type-C 4 cổng USB, Hub đa năng 6-in-1 HDMI 4K.

### Đặc tả phục vụ kiểm thử:

- **Biên độ giá:** Trải dài từ 89.000 VNĐ (lót chuột) đến 2.290.000 VNĐ (tai nghe Sony), cho phép kiểm thử lọc theo nhiều mức ngân sách (<100k, <300k, <500k, >1tr).
- **Trạng thái tồn kho:** Có 13 sản phẩm còn hàng (`stock > 0`) và 2 sản phẩm hết hàng chủ đích (`stock = 0`: SP003 - Chuột Delux M618 Mini, SP012 - Hub Ugreen 6-in-1) nhằm kiểm tra khả năng phát hiện hết hàng và cảnh báo khách của AI Agent.

---

## 3. Nguồn Gốc Chính Sách Cửa Hàng (store_policy.md)

Chính sách cửa hàng được thiết kế tổng hợp từ các quy chuẩn dịch vụ khách hàng thương mại điện tử phổ thông:

- Phạm vi toàn quốc, phân tách giao nhanh nội thành và giao liên tỉnh.
- Ngưỡng miễn phí vận chuyển 300.000 VNĐ.
- Quy định đổi trả 7 ngày đối với lỗi nhà sản xuất và điều kiện bảo hành điện tử.
- Bổ sung nguyên tắc đạo đức và hành vi ứng xử cho AI Agent: trung thực, không bịa đặt thông tin khi thiếu dữ liệu, hỏi lại khách khi nhu cầu chưa rõ ràng.

---

## 4. Bộ Câu Hỏi Kiểm Thử (tests/questions_week3.csv)

Bộ 20 câu hỏi được thiết kế có chủ đích bao phủ 6 tình huống tư vấn thực tế trên livestream:

1. `product_info` (4 câu): Hỏi thông số, tính năng chi tiết.
2. `price_stock` (4 câu): Hỏi giá và tình trạng kho (bao gồm cả sản phẩm còn hàng và hết hàng).
3. `budget_need` (4 câu): Tư vấn theo mức tiền và mục đích sử dụng cụ thể.
4. `comparison` (3 câu): So sánh tính năng, giá cả giữa 2 sản phẩm tương đương.
5. `missing_info` (3 câu): Hỏi các thông số cố tình không cung cấp trong dữ liệu (màu sắc, trọng lượng gram, chuẩn IPX) để kiểm tra khả năng chống ảo giác (anti-hallucination).
6. `out_of_scope` (2 câu): Hỏi mặt hàng cửa hàng không kinh doanh (điện thoại, laptop) và hỏi ngoài lề (thời tiết).
