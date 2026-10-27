# EDUPlan AI 7.14 – BẢN SỬA LỖI NGÀY 27/10/2026

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Lỗi đã sửa

1. Đổi khối / đổi chương xóa bài cũ (không chọn nhầm bài trùng số từ chương khác).
2. Ôn lại câu sai không còn bị giới hạn bởi bộ lọc lớp/chương/bài đang chọn.
3. Chọn Đúng/Sai không dựng lại toàn bộ bài, giữ vị trí cuộn và trạng thái nút, tăng ổn định trên điện thoại.
4. CSV kiểm tra khóa Đ/S nghiêm ngặt; giá trị bất thường bị đưa vào kho cách ly, không bị hiểu nhầm là “Sai”.
5. Dấu vân tay chống trùng xét cả đề dẫn và 4 nhận định; hai tình huống khác nhau không bị gộp nhầm.
6. Mã băm SHA-256 toàn tệp bảo vệ khỏi nhập lại 21 tài liệu gốc đã tích hợp. Tệp sửa đổi vẫn được xử lý; câu trùng nhưng khóa nguồn khác được cảnh báo và không tự ghi đè.
7. File Word đến 32 MiB (trước đó 12 MiB), tự dò soffice/LibreOffice trên Windows/macOS/Linux và dùng profile tách biệt tránh lỗi khi nhập song song.
8. Giao diện/API dùng danh sách trường dữ liệu công khai cụ thể: kể cả khi JSON có `answerKey`, `answers`, `solution` thì API học sinh không trả về.
9. Chế độ có chấm yêu cầu học sinh chọn đủ cả 4 ý của mọi câu trước khi chấm; không mở khóa đáp án khi chưa hoàn thành.
10. Phiên bài chưa nộp có giới hạn và tự dọn phiên hết hạn.

## Kiểm thử đã đạt

- Dữ liệu gốc giữ nguyên: **773 câu**, 112 câu có khóa nguồn và lời giải đủ điều kiện cấu trúc để chấm; 661 câu tự luyện không chấm.
- API: lấy danh mục, lấy câu học sinh, tạo phiên, từ chối nộp thiếu ý, nộp đủ và trả 4 nhận định + đáp án + lời giải mỗi câu; từ chối nộp trùng phiên.
- Dữ liệu nhập: 2 câu CSV mới (1 có khóa, 1 khóa không hợp lệ): phân luồng đúng; nhập lại cùng tệp tự bỏ qua.
- Word mẫu “Pin điện và điện phân”: nhập lại không tạo câu trùng.
- Word Hóa 11 “Nitrogen – Sulfur” dung lượng 14.139.733 byte: đọc thành công trong kiểm thử.
- Chromium với API thật được mô phỏng qua cầu nối TestClient: giao diện máy tính 1440 px và điện thoại 390 px, làm 5 câu, trả 20 ý, xem 20 lời giải, không tràn ngang, không phát sinh lỗi JavaScript.

## Giới hạn cần ghi rõ

- **Đây là mô-đun độc lập chạy trên máy giáo viên**; chưa sửa code của website Vercel chính thức nếu chưa có quyền repository.
- Tự kiểm định chỉ xác minh **cấu trúc và dữ liệu nguồn**, không bảo đảm tuyệt đối mọi khóa Đúng/Sai về mặt Hóa học. Hệ thống vẫn giữ câu chưa đủ căn cứ trong kho tự luyện không chấm.
- Các công thức/hình MathType, OLE hoặc phức chất bị Word chuyển đổi lỗi cần kiểm chứng trên tài liệu gốc trước khi dùng để kiểm tra chính thức.
- Không công khai `questions_private.json`, `.teacher_password`, hoặc gói giáo viên lên website tĩnh.
- Bản thử chưa có tài khoản học sinh, giới hạn yêu cầu truy cập công khai/HTTPS/ghi nhật ký hay lưu trữ cơ sở dữ liệu nhiều người dùng. Không mở trực tiếp Internet khi chưa có hạ tầng bảo mật.
