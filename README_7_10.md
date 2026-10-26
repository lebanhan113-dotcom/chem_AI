# EduPlan AI 7.10 — Bố cục tất cả chức năng trên màn hình chính

**Tác giả:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Điểm mới

- Bỏ sidebar và menu **Học liệu & công cụ** ẩn, thay bằng 17 thẻ chức năng nhìn thấy ngay trên trang chính, phân thành 3 nhóm: Học kiến thức, Luyện tập/kiểm tra, Kết quả/công cụ.
- Nhấn một thẻ để mở ngay màn hình của công cụ, tự cuộn tới phần thao tác. Luôn có nút **Tất cả chức năng** để quay lên.
- Trên điện thoại, các thẻ hiển thị 2 cột, không cuộn ngang.
- Giữ nguyên nguyên trạng `data/` và các tệp API máy chủ, mã ngân hàng câu hỏi, tài liệu/ảnh, DOCX export.
- Form 2025 giữ 3 phần chính thức: 18 câu A–D, 4 câu Đúng/Sai bốn ý, 6 câu trả lời ngắn.

## Triển khai

Đưa **toàn bộ** nội dung giải nén của ZIP vào repository **Private**, vì gói có `api/grade.js` và khóa đáp án máy chủ.
Triển khai trên Vercel theo cấu hình `vercel.json` có sẵn. Giữ `index.html` ở thư mục gốc cùng `css`, `js`, `data`, `assets`, `api`. Không đưa gói có khóa đáp án lên GitHub Pages công khai.

Có thể thử trên máy bằng `python -m http.server 8000` rồi mở `http://localhost:8000`. Truy cập bằng cách mở `index.html` dưới dạng `file://` không hoạt động với `fetch` dữ liệu.

## Lưu ý về đáp án

API chỉ trả khóa được rà soát **sau khi nộp bài**; câu chưa đạt điều kiện chấm vẫn có thể tự ôn nhưng không được tự đoán đáp án. Phiên bản tĩnh không an toàn cho chấm điểm hoặc lưu kết quả toàn trường. Chưa xác minh toàn bộ ngân hàng câu hỏi về độ chính xác khoa học.
