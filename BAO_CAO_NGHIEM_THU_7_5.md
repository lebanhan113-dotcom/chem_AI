# BÁO CÁO NÂNG CẤP EDUPLAN AI 7.5 – SƠ ĐỒ TƯ DUY KNTT

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## 1. Kết quả hoàn thành

- Tích hợp vào WebApp EduPlan AI 7.4, thêm thanh công cụ **Sơ đồ tư duy KNTT** (15 mục điều hướng).
- Tạo **21 sơ đồ cấp chương** và **78 sơ đồ cấp bài** đúng theo tên, mã chương/bài của `data/curriculum.json`.
- Tổng hợp **4 nhánh kiến thức cho mỗi bài**: 312 nhánh chi tiết, kèm ví dụ/ghi nhớ và các điều kiện áp dụng khi phù hợp.
- Sơ đồ chương chứa nhánh ứng với từng bài học trong chương.
- Hiển thị đồ thị SVG, chọn nhánh, nội dung diễn giải bên dưới, phóng to/thu nhỏ, cuộn ngang trong khung trên điện thoại.
- Liên kết sơ đồ bài và chương với **Luyện từng câu 5/10/15** và **Sổ ôn lỗi sai**; liên kết từ danh mục bài học sang sơ đồ tương ứng.
- Hướng dẫn từng bước riêng ngay trong mục Sơ đồ tư duy.
- Xuất sơ đồ **DOCX có ảnh và phần ý chính** (phông Times New Roman), ảnh PNG và SVG. Không yêu cầu Gemini API key.
- Giữ nguyên **1.958 câu hỏi**, 57 chuyên đề lỗi sai, 21 chương/78 bài, tập tin học liệu cũ và khóa lưu tiến độ.

## 2. Kiểm tra dữ liệu

- 21/21 chương có tên trùng với `curriculum.json`.
- 78/78 bài có số thứ tự, tên, chương gốc và 4 nhánh có nội dung.
- Không thay đổi hash SHA-256 của 5 tệp JSON gốc gồm curriculum, 3 ngân hàng theo khối và Sổ lỗi sai.
- Không thay đổi nội dung của 171 tệp trong các thư mục assets và references.
- Không thêm khóa đáp án vào website công khai.

## 3. Kiểm thử trình duyệt thực tế

Trình duyệt Chromium được kiểm tra bằng cách nạp trực tiếp các tệp HTML/CSS/JS và trả dữ liệu JSON nội bộ, do chính sách môi trường chặn điều hướng localhost.

| Hạng mục | Kết quả |
|---|---|
| Nạp 1.958 câu hỏi và 21 + 78 sơ đồ | Đạt |
| Thanh điều hướng gồm 15 mục | Đạt |
| Sơ đồ chương → bấm nhánh → sơ đồ bài | Đạt |
| Lọc Hóa 10 → Hóa 12, chọn chương/bài khác nhau | Đạt |
| Chọn nhánh, cập nhật nội dung, phóng/thu sơ đồ | Đạt |
| Mở luyện tập từ bài đang xem | Đạt |
| Tải DOCX có ảnh; tệp DOCX/ZIP hợp lệ | Đạt |
| Tải PNG và SVG; XML sơ đồ SVG hợp lệ | Đạt |
| Giao diện 1400 px và 390 px, không tràn trang | Đạt trong luồng thử |
| Lỗi JavaScript trong luồng thử | Không có |

## 4. Chưa hoàn thành/giới hạn

- **Chưa triển khai website trên tài khoản GitHub Pages hoặc Vercel thật**, chưa nghiệm thu trên tên miền thực.
- Đây là các sơ đồ tóm tắt kiến thức được biên soạn cho từng bài; **không phải bản sao nguyên văn sơ đồ từ SGK**. Giáo viên cần thẩm định chuyên môn trước khi dùng làm tài liệu chính thức, đặc biệt các quy tắc có ngoại lệ.
- Sơ đồ cần cuộn ngang trong khung trên màn hình điện thoại để giữ chữ dễ đọc; không có hiện tượng tràn ngang toàn trang.
- Phiên bản hosting tĩnh không cung cấp đăng nhập đa thiết bị hay chấm thi có đáp án bảo mật.

## 5. Cấu trúc mới

- `data/mindmaps.json`: 21 sơ đồ chương và 78 sơ đồ bài.
- `js/app.js`: màn hình sơ đồ, SVG, chuyển trang và điều khiển.
- `js/docx-export.js`: xuất Word kèm ảnh sơ đồ.
- `css/app.css`: giao diện SVG thích ứng thiết bị.
- `index.html`: tệp chạy chính, nhỏ gọn dành cho GitHub.
