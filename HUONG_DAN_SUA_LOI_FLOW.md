# Quy tắc sử dụng câu lệnh chỉnh sửa trong Flow (bảo toàn tính năng)

**Không gửi cùng lúc 15 câu lệnh sửa lỗi cho một phiên làm việc.** Trước tiên kiểm tra và chọn đúng trường hợp lỗi đang xuất hiện trong app. Chỉ gửi 1 câu lệnh sửa mỗi lần.

## Trình tự chẩn đoán

1. Xác định Scene ID và triệu chứng cụ thể.
2. Xem kết quả đầu ra của bước trước: bài học → phân tích → kịch bản → cảnh → Bible → prompt → ảnh → video → ghép.
3. Xác định tầng lỗi: frontend, dữ liệu, Gemini, Nano Banana, Veo, FFmpeg hay trạng thái workflow.
4. Chỉ chỉnh sửa hàm, API hoặc thành phần phụ thuộc trực tiếp.
5. Bảo toàn media, phiên bản, các Scene đã hoàn thành.
6. Chạy lại kiểm thử chức năng vừa sửa và kiểm thử hồi quy.

## Câu lệnh khóa bảo toàn – thêm cuối mọi lệnh sửa

> Chỉ sửa đúng chức năng và phạm vi được yêu cầu. Giữ nguyên toàn bộ giao diện, component, chức năng, dữ liệu, API, biến môi trường, cấu trúc project và luồng xử lý khác đang hoạt động đúng. Không xóa, đổi tên, viết lại hoặc vô hiệu hóa các tính năng không liên quan. Không tái cấu trúc toàn bộ app nếu không cần thiết. Sau khi sửa phải kiểm tra để bảo đảm các chức năng cũ vẫn hoạt động bình thường.

## Bảng chọn tình huống lỗi

| Nhóm | Mục tiêu sửa tối thiểu |
|---|---|
| Continuity | Start State/End State, trạng thái chuyển tiếp |
| Character | Character ID/Bible cố định |
| Environment | Environment ID/Bible cố định |
| Prompt video | Prompt tham chiếu kịch bản, thoại khóa, Bible |
| Prompt ảnh | Prompt bám nội dung và đạo cụ cảnh |
| Reference Lock | Ảnh được duyệt làm tham chiếu ổn định |
| Veo mapping | Scene ID chính xác, ảnh/prompt/thoại cùng cảnh |
| Lời thoại | Dialogue nguyên văn, phù hợp thời lượng |
| Regenerate Scene | Chỉ tạo lại cảnh được chọn |
| Merge | Đủ cảnh, đúng Scene Order, không cắt lời |
| Dependency | Chỉ vô hiệu hóa đầu ra phụ thuộc |
| Progress | Theo dõi trạng thái thật |
| UI | Sửa nhỏ, không phá hành vi nút cũ |
| Regression | Test đầu vào đến MP4 sau mỗi lần sửa |

Các hiện tượng chưa có bằng chứng nên kiểm tra bằng log/thử nghiệm trước, không kết luận là lỗi thật.
