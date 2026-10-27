# BẮT ĐẦU VỚI EDUPlan AI 7.14 – QUẢN LÝ SỐ

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất

1. Cài Python 3.11+.
2. Trên Windows chạy `CHAY_WEBAPP_WINDOWS.bat`; với Mac/Linux chạy `sh CHAY_MAC_LINUX.sh`.
3. Mở `http://127.0.0.1:8765`.
4. Mở tab **Trung tâm giáo viên**, đăng nhập tài khoản `giaovien` bằng mật khẩu máy chủ tự sinh, tạo lớp và mã học sinh.
5. Mở **Khóa học** tạo khóa học (không bắt buộc).
6. Mở **Tạo / Trộn đề**, chọn lớp, khối, chương, bài, mức độ, năng lực, số câu; giao bài.
7. Học sinh dùng mã riêng tại **Thi / Làm bài online**, nộp bài; xem câu hỏi, đáp án đúng và lời giải sau nộp.
8. Xem **Thống kê & phân tích** và xuất CSV điểm lớp.
9. Muốn kiểm tra trên giấy: **Chấm phiếu giấy** để in đề riêng theo học sinh, in phiếu Đ/S rồi nhập kết quả vào hệ thống để chấm. Không có quét ảnh OMR tự động.
10. Muốn bổ sung nguồn: **Cập nhật ngân hàng** để nhập DOCX/CSV/JSON; có kiểm tra và cách ly câu chưa đủ điều kiện.

Xem `HUONG_DAN_SU_DUNG_VA_TICH_HOP.md` để đọc đầy đủ 16 công cụ, bảo mật, dữ liệu và phạm vi kiểm thử.

**Cảnh báo:** Bản này có 773 câu nguồn nhưng chỉ 112 câu có khóa nguồn đủ điều kiện chấm. Không đăng toàn bộ thư mục giáo viên hoặc `questions_private.json` lên Vercel public. Chưa tích hợp vào repository website chính thức.


**Bản 7.14+** có tệp `HUONG_DAN_7_14_PLUS_QUAN_LY_SO.md` trình bày đủ 16 mục và các API theo dõi học tập mới.
