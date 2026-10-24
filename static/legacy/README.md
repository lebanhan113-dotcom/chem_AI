# CHEM-MAP TUTOR AI 2.0 — Bản WebApp chạy thử

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Chạy trực tiếp

- Mở `CHEM_MAP_TUTOR_AI_2_0_Offline.html` trong trình duyệt (phiên bản tất cả trong một).
- Hoặc mở thư mục này trong một terminal và chạy `python -m http.server 8080`, sau đó truy cập `http://localhost:8080`.
- Không cần GEMINI_API_KEY, không cần npm hoặc server CSDL cho bản demo.

## Các chức năng đã hoạt động

1. 51 câu hỏi tự biên soạn minh họa cho Hóa 10, 11, 12: 36 trắc nghiệm A–D, 6 đúng/sai bốn ý, 6 trả lời ngắn dạng số, 3 tự luận.
2. Tạo/trộn đề luyện và kiểm tra; làm/nộp bài. Kết quả hiển thị điểm /10, từng câu hỏi, bài làm, đáp án, lời giải, phân tích phương án nhiễu.
3. Chấm Đúng/Sai từng ý; trắc nghiệm và trả lời ngắn theo đáp án quy tắc. Câu tự luận được giữ chờ giáo viên duyệt điểm.
4. Bản đồ 16 mã lỗi; giải thích lỗi từ phương án nhiễu với nhãn **giả thuyết** (không khẳng định đã biết nguyên nhân tư duy của học sinh).
5. Gói luyện cá nhân hóa và lịch sử trước/sau; bản đồ thành thạo theo từng kỹ năng có nhãn mức dữ liệu.
6. Giao diện học sinh / giáo viên / quản trị; giáo viên soạn bản nháp và xác nhận kiểm duyệt câu hỏi, tạo đề, duyệt điểm tự luận, gọi tên ngẫu nhiên.
7. Báo cáo CSV và sao lưu / khôi phục dữ liệu JSON từ trình duyệt.

## Giới hạn quan trọng

Đây là **MVP trình diễn chạy trên một thiết bị/trình duyệt**, không phải hệ thống nhiều người dùng. Các vai trò chỉ chuyển giao diện và **không có xác thực hoặc phân quyền phía máy chủ**. Dữ liệu lưu tại LocalStorage và không đồng bộ giữa các thiết bị. Không nhập dữ liệu định danh học sinh thật. Các câu hỏi minh họa cần được giáo viên duyệt lại khi dùng trong kiểm tra chính thức.

Phân tích chuyên môn hiện dùng **hệ quy tắc và dữ liệu phương án nhiễu**, không tích hợp mô hình AI ngoài, không tạo ra câu hỏi mới tự động từ LLM và không khẳng định suy luận được nguyên nhân cá nhân khi chỉ có 1 đáp án.

Để phát hành chính thức cho trường học, cần triển khai backend với tài khoản, phân quyền, bảo vệ dữ liệu học sinh, nhật ký truy cập, quản lý lớp, đồng bộ CSDL và kiểm thử bảo mật. Nếu thêm AI sinh nội dung, cần thành phần xác thực/kiểm duyệt của giáo viên và khóa API nằm ở server nếu sử dụng nhà cung cấp yêu cầu khóa.

## Đưa lên Vercel hoặc Netlify

Nội dung thuần tĩnh, có `index.html`, `assets/` và `vercel.json`. Tạo project static từ thư mục này, build command để trống, output directory là thư mục gốc. Sau deploy, thử đủ vòng: đổi vai trò → tạo đề → học sinh làm bài → chấm bài → lộ trình học.

## Cấu trúc

- `index.html`: giao diện shell.
- `assets/style.css`: CSS responsive.
- `assets/bank.js` / `assets/bank.json`: ngân hàng dữ liệu.
- `assets/engine.js`: thuật toán chấm, chẩn đoán, tổng hợp, cá nhân hóa.
- `assets/app.js`: giao diện và lưu phiên làm bài.
- `tests/engine.test.js`: kiểm thử thuật toán.
- `CHEM_MAP_TUTOR_AI_2_0_Offline.html`: bản một file mở trực tiếp.
