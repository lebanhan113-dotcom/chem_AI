# EDUPlan AI 7.14+ — BẢN TẬP TRUNG QUẢN LÝ DẠY HỌC SỐ

**Tác giả:** Lê Bá Nhẫn – Trường THPT Hòn Đất  
**Bản cập nhật:** 27/10/2026  
**Mục tiêu:** tạo/trộn đề → giao bài → học sinh làm bài → chấm và giải thích → theo dõi cá nhân → điều chỉnh dạy học.

## Cài đặt

- Windows: cài Python 3.11+, giải nén ZIP, chạy `CHAY_WEBAPP_WINDOWS.bat`, mở `http://127.0.0.1:8765/`.
- Mac/Linux: `python -m pip install -r requirements.txt && sh CHAY_MAC_LINUX.sh`.
- Không yêu cầu `GEMINI_API_KEY`. Để nhập DOCX cần cài LibreOffice (`soffice`).
- Giáo viên đăng nhập tên `giaovien` ở **Trung tâm giáo viên**; mật khẩu nằm trong cửa sổ máy chủ hoặc tệp `.teacher_password` được sinh lúc chạy đầu tiên. Không gửi mật khẩu cho học sinh.
- Học sinh dùng mã riêng do giáo viên cấp, vào **Thi / Làm bài online**.

## Thanh công cụ — giữ đủ 16 mục

1. Tổng quan: truy cập nhanh năm mục tiêu.
2. Trung tâm giáo viên: tổng lớp, số bài giao, tỷ lệ nộp, kết quả, bài cần ôn.
3. Thi / Làm bài online: vào lớp bằng mã học sinh, nhận và nộp đề.
4. Luyện theo bài: chọn 5/10/15 câu có khóa đáp án.
5. Ngân hàng câu hỏi: lớp → chương → bài → phần → mức độ → HH1/HH2/HH3.
6. Tự luyện nguồn: câu chưa đủ khóa, không tự chấm.
7. Ôn lỗi sai: luyện lại câu cá nhân làm sai.
8. Tiến độ & điểm của em: bài đã/chưa nộp, điểm và xem lại lời giải.
9. Lớp & học sinh: tạo lớp, cấp mã riêng, quản lý danh sách.
10. Khóa học: tạo khóa gắn với lớp.
11. Tạo / Trộn đề: lọc bài/mức độ/năng lực, KIỂM TRA SỐ CÂU khả dụng, tạo đề phân theo học sinh.
12. Giao bài & Theo dõi: danh sách đề, tỷ lệ nộp, chi tiết trạng thái từng em, xuất CSV.
13. Chấm phiếu giấy: in đề học sinh, phiếu trả lời, nhập nhanh Đ/S và chấm trên máy chủ. **Chưa quét ảnh OMR.**
14. Thống kê & phân tích: điểm từng học sinh, câu thường sai, xuất bảng điểm CSV.
15. Cập nhật ngân hàng: DOCX/CSV/JSON, lọc trùng, tự kiểm định có ngưỡng, tách câu không đủ chứng cứ.
16. Hướng dẫn: sử dụng cơ bản.

## Các thay đổi kỹ thuật chính

- API mới `GET /api/workflow/teacher/overview` trả tổng hợp bài nộp, lượt chưa nộp, các bài quá hạn, ưu tiên ôn tập thực tế.
- API mới `GET /api/workflow/teacher/assignment/{id}/matrix` trả trạng thái từng học sinh; `GET /api/workflow/teacher/assignment/{id}/matrix.csv` tải báo cáo.
- API mới `GET /api/workflow/teacher/availability` cho biết số câu đủ khóa để tạo đề trước khi giao.
- Bộ lọc `GET /api/questions` bổ sung `level` và `competency`.
- Tách **Tạo / Trộn đề** với **Giao bài & Theo dõi**. Không còn hai tab giống hệt nhau.
- Tiến độ cá nhân được trình bày riêng, có nhật ký điểm và liên kết đọc lời giải sau nộp.
- Thanh công cụ 16 mục đều hiển thị ở màn hình nhỏ, không cần kéo ngang để tìm chức năng.
- Chấm phiếu giấy hỗ trợ dán nhiều dòng Đ/S theo số câu để giảm nhập tay (chỉ sau khi giáo viên đối chiếu phiếu giấy).
- Khóa Đúng/Sai không nằm trong API câu hỏi học sinh; lời giải chỉ trả về sau nộp bài.

## Dữ liệu và giới hạn

- Ngân hàng gốc giữ **773 câu**; theo quy tắc kiểm định nguồn hiện tại có **112 câu** đủ điều kiện chấm và **661 câu** chỉ tự luyện không chấm. Hóa 12 chỉ có 2 câu đủ chấm tự động theo điều kiện nghiêm ngặt; không thể tạo đề 5 câu chấm điểm Hóa 12 từ nguồn hiện tại.
- Phân loại/chống trùng và kiểm tra đáp án nguồn **không phải bảo đảm tuyệt đối về đúng/sai chuyên môn Hóa học**. Không tự tạo khóa hoặc lời giải khi không có đủ căn cứ.
- Ứng dụng được kiểm thử **cục bộ** và dùng SQLite; **chưa** triển khai trực tiếp lên Vercel/Supabase và **chưa** được gia cố bảo mật để mở Internet công khai.
- Chấm giấy: **nhập Đ/S từ phiếu**; không có nhận dạng ảnh phiếu tô OMR.
- Bản này không chứa dữ liệu học sinh thử nghiệm trong cơ sở dữ liệu. SQLite được tạo trống lúc khởi động; hãy sao lưu `edup_education.sqlite3` sau khi sử dụng thực tế.
- Dữ liệu đáp án giáo viên nằm trong `questions_private.json`. **Không đăng ZIP giáo viên lên trang công khai; không sao chép khóa đáp án vào thư mục public.**

## Cập nhật vào cài đặt cũ

Sao lưu toàn bộ thư mục trước khi ghi đè. Nếu đã sử dụng bản cũ và muốn giữ dữ liệu học sinh, câu hỏi, tệp nguồn, chỉ dùng gói `GOI_VA_CODE` và thay đúng sáu tệp: `index.html`, `app.css`, `app.js`, `management.js`, `server.py`, `workflow.py`. **Giữ nguyên** `questions_private.json`, `source_import_history.json`, `edup_education.sqlite3`, `.teacher_password`, `media/`. Các bảng mới không làm mất các bảng cũ; vẫn nên sao lưu trước khi nâng cấp.

## Kiểm thử

- Python: API tạo lớp, danh sách học sinh, sẵn có câu, đề trộn, làm bài, chấm, bảng theo dõi, CSV, cảnh báo chưa nộp, truy cập không có quyền.
- Chromium: trang chủ, đăng nhập, điều hướng, bảng theo dõi, tạo đề, bộ lọc ngân hàng trên 1440px và 390px; không gặp lỗi JavaScript ở các luồng đã thử, không tràn ngang ở 390px.
- **Chưa kiểm thử** triển khai nhiều người dùng đồng thời qua Internet hoặc tích hợp với repository Vercel.
