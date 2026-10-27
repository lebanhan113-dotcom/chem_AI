# Báo cáo nâng cấp EduPlan AI 7.14 – Ngày 27/10/2026

- Giữ nguyên dữ liệu 773 câu (112 có khóa nguồn đủ điều kiện chấm, 661 câu tự luyện chưa chấm).
- Mở rộng từ một ứng dụng ôn Đúng/Sai thành hệ thống dạy học số gồm: lớp – học sinh – khóa học – bài giao – đề trộn – bài nộp – kết quả – phân tích.
- Thêm `workflow.py`: lớp, sinh mã học sinh, khóa học, giao bài, giới hạn thời gian, chấm online, in đề cá nhân và chấm phiếu giấy bằng nhập Đ/S, báo cáo CSV; dữ liệu lưu SQLite.
- Thêm `management.js`: màn hình giáo viên/học sinh, bộ tạo đề có chương-bài-mức độ-năng lực, danh sách đề, bảng điểm, tiến độ.
- Bổ sung thanh công cụ 15 nhóm thao tác và trang chủ điều hướng theo 5 mục tiêu sử dụng.
- Kết quả học sinh: hiển thị lại đầy đủ câu hỏi, đáp án em chọn, đáp án nguồn và giải thích 4 ý sau nộp.
- Kiểm tra: tích hợp API và Chromium (giả lập truy cập mạng qua bridge theo hạn chế môi trường); không tràn ngang ở 390 px, không gặp lỗi JS ở các luồng đã kiểm tra.

**Hạn chế minh bạch:** Chưa nhận dạng phiếu giấy từ ảnh; chưa phân quyền/tài khoản/HTTPS chuẩn triển khai Internet, chưa tích hợp repository chính thức; quy tắc tự kiểm định dữ liệu chưa thay thế chuyên gia hóa học; chỉ 112/773 câu có khóa để chấm.

## Bổ sung trong bản 7.14+
- 16 mục thanh công cụ, đủ trên di động; tách giao bài khỏi tạo đề.
- Trung tâm giáo viên: chưa nộp, quá hạn, tỷ lệ nộp và bài cần ôn.
- Học sinh có trang tiến độ riêng.
- Bảng theo dõi từng em có CSV.
- Kiểm tra số câu đủ chấm trước khi tạo đề; lọc mức độ và HH1/HH2/HH3.
- Chấm giấy hỗ trợ dán Đ/S theo dòng; chưa nhận dạng OMR.
- Cơ sở dữ liệu học sinh không đóng kèm bản phát hành.
