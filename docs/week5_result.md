# Kết quả kiểm tra tra cứu sản phẩm tuần 5

Ngày tổng hợp: 2026-11-28.

## Phiên bản

- Nhánh: `feature/week5-product-lookup`, tách từ bản tích hợp tuần 3–4.
- HEAD khi kiểm tra: `60f7419`. Các thay đổi tra cứu tuần 5 chưa commit;
  HEAD này chưa đại diện cho toàn bộ mã được kiểm tra.
- Luồng: Chat LLM → `agent.service.answer_question()` → tra cứu danh mục
  15 sản phẩm → Gemini → Edge TTS → avatar LiveTalking.

## Phản hồi kiểm thử thực tế

Toản xác nhận sau lượt thử bằng giọng nói:

> Câu trả lời đã chính xác, từ lúc gửi câu hỏi đến lúc avt trả lời dao động
> từ khoảng 20-35s.

Ghi nhận: nội dung đúng theo xác nhận của người thử; thời gian chờ quan sát
khoảng 20–35 giây. Đây là khoảng ước lượng chung, chưa có số đo riêng từng
câu, bản chép lời từng lượt hoặc xác nhận chi tiết về âm thanh bị ngắt.
Không dùng phản hồi này để suy ra tỷ lệ chính xác trên toàn bộ danh mục.

Các câu được yêu cầu trong lượt thử:

| Mã ca | Câu hỏi | Đáp án mong đợi |
|---|---|---|
| W5-01 | Chuột dưới 299 nghìn còn hàng không? | Không có chuột phù hợp. |
| W5-02 | Chuột tối đa 299 nghìn còn hàng không? | Logitech M220, SP001, giá 299.000 đồng, còn hàng. |
| W5-03 | Logitech M220 có dưới 200 nghìn không? | Giá 299.000 đồng vượt ngân sách. |
| W5-04 | Chuột Delux M618 Mini còn hàng không? | SP003 đã hết hàng. |
| W5-05 | Hub Ugreen 70411 còn hàng không? | SP012 đã hết hàng. |

Bảng trên ghi ca thử và kỳ vọng; không tự gán số giây hoặc bản chép lời cho
từng ca từ khoảng thời gian chung người thử cung cấp.

## Kiểm tra tự động chạy lại

Lệnh dùng môi trường `livetalking`:

```bash
/home/thaitoan/miniconda3/envs/livetalking/bin/python -m unittest discover -s tests -p test_product_lookup.py -v
```

Kết quả: **10/10 đạt**, exit code 0. Phạm vi gồm ranh giới giá `<`/`<=`,
lọc hàng hết kho khi gợi ý, giữ hàng hết kho khi hỏi đích danh, đối chiếu
ngân sách với sản phẩm đích danh, so sánh, phân loại lót chuột, sản phẩm
không tồn tại, ngữ cảnh đủ dữ liệu, callback văn bản tới avatar và từ chối
mã sản phẩm ngoài tập tra cứu.

Các ca tích hợp tự động giả lập API LLM và callback avatar; chúng không đo
Gemini thật, Edge TTS thật hoặc âm thanh nghe được trên trình duyệt.
Thông báo lỗi về mã sản phẩm ngoài kết quả tra cứu trong lượt chạy là
đầu ra dự kiến của ca kiểm tra từ chối phản hồi sai.

## Đối chiếu độ trễ từ log hiện có

Nguồn: `livetalking.log`, các dòng có dấu thời gian sau đây. Thời gian là
nguyên văn theo log, chưa quy đổi múi giờ.

| Thời điểm agent hoàn tất | Kết quả agent | Agent (giây) | Edge TTS (giây) |
|---|---|---:|---:|
| 2026-11-28 21:12:10,290 | no_data, không có chuột dưới 299 nghìn | 1,443 | 15,2170 |
| 2026-11-28 21:12:47,348 | ok, SP001, giá 299 nghìn và còn hàng | 1,329 | 8,1874 |
| 2026-11-28 21:13:07,215 | ok, SP001, vượt ngân sách 200 nghìn | 1,303 | 13,0939 |
| 2026-11-28 21:13:32,609 | ok, SP003, hết hàng | 2,561 | 9,5191 |

Thời gian agent gồm lời gọi `answer_question()`, không phải phép đo riêng
API Gemini. Thời gian Edge TTS đo bước tổng hợp/tải âm thanh trước khi
giải mã, đổi tần số lấy mẫu và đưa frame sang avatar. Không cộng các số này
rồi coi là thời gian từ nút Send đến tiếng đầu tiên trong trình duyệt.

Trong bốn lượt có số liệu trên, Edge TTS tốn thời gian hơn agent.
`tts/edge.py` hiện tải xong âm thanh của cả văn bản rồi mới giải mã và gửi
frame cho avatar. Đây là điểm cần ưu tiên đo và thử tối ưu; chưa đủ bằng
chứng quy toàn bộ khoảng 20–35 giây cho TTS.

Log còn có một lượt `NoAudioReceived` lúc 2026-11-28 21:11:13,567,
trước nhóm lượt thành công trên. Cần lưu ý lỗi cũ này khi đánh giá độ ổn
định, không suy ra mọi lượt hiện tại đều mất tiếng. Chưa tìm thấy lượt Hub
Ugreen 70411 trong log hiện có; kết quả cho câu này hiện dựa trên phản hồi
tổng quát của người thử.

## Công việc tiếp theo

1. Bổ sung kết quả từng ca: câu thực tế nghe được, nghe đủ hay bị ngắt và
   thời gian từ Send đến tiếng đầu tiên; xác nhận riêng W5-05 nếu cần.
2. Đo các mốc nhận câu hỏi, hoàn tất agent, bắt đầu TTS, sẵn sàng audio và
   phát tiếng phía trình duyệt để xác định phần thời gian còn thiếu.
3. Dựa trên số đo, thử một thay đổi giảm độ trễ TTS mỗi lần; đo lại cùng
   câu hỏi và điều kiện trước khi kết luận cải thiện. Chưa sửa hành vi TTS
   hoặc xác nhận độ trễ đã được cải thiện trong lần tổng hợp này.
4. Rà soát mã và báo cáo, commit phần tra cứu tuần 5, rồi tiếp tục tuần 6.
   Bộ chấm tuần 4 vẫn cần Quỳnh rà soát riêng; 10 test trên không thay thế
   việc đánh giá toàn bộ câu trả lời Gemini thật.
