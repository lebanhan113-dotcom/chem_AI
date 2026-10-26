# EduPlan AI 7.8 – Bài tập tương tác trực tiếp trong mọi học liệu

## Cài đặt
- Giải nén. Đưa **tất cả các tệp** lên GitHub Pages / Vercel. Giữ `index.html` ở thư mục gốc. Không chỉ tải riêng HTML.
- Bản GitHub Pages (PUBLIC) chạy tĩnh, không có `/api/grade`, nên **không hiển thị đáp án chính thức**.
- Bản Vercel (PRIVATE) có `/api/grade` và khóa đáp án phía server cho nhóm câu có khóa đủ điều kiện theo dữ liệu từ 7.7; chỉ dùng repository riêng tư. Trình duyệt không tải tệp khóa đáp án.
- Không yêu cầu học sinh nhập `GEMINI_API_KEY`.

## Cách học trực tiếp
1. Chọn Hóa 10/11/12 và chương, bài KNTT.
2. Vào Sơ đồ tư duy, Sổ ôn lỗi sai, Kho câu hỏi hoặc Học liệu. Cuối mỗi nội dung có mục **Em thử làm bài ngay**.
3. Chọn 5/10/15 câu, trả lời từng câu, xác nhận để sang câu tiếp theo.
4. Kết thúc: xem tiến độ và đáp án (chỉ khi kết nối API Vercel với câu đã kiểm duyệt).
5. Tải phiếu Word `.docx` khi cần in. Trong Phiếu học tập, Tạo đề và Kết quả đã có chức năng DOCX.
6. Lịch sử lưu cục bộ theo trình duyệt. Không phải số liệu lớp/trường tập trung.

## Hạn chế
- Dữ liệu học sinh trên GitHub Pages là LocalStorage; không đồng bộ qua các thiết bị.
- Toàn ngân hàng 1.958 câu được tra cứu và tự giải; **không phải tất cả có khóa chính thức**.
- Chưa kiểm tra khoa học độc lập toàn bộ 1.958 câu; câu có MathType/OLE/hình phức tạp phải đối chiếu bản gốc.
- API Vercel hiện chỉ phục vụ tự luyện; chưa có đăng nhập, chưa phù hợp dùng cho thi chính thức chống gian lận.
- Không đăng PRIVATE ZIP hoặc tệp `api/grade.js` trên GitHub Pages công khai.

Tác giả: Lê Bá Nhẫn – Trường THPT Hòn Đất.
