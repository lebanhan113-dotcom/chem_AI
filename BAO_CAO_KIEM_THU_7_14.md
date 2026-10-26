# Báo cáo nâng cấp EduPlan AI 7.14

**Đã hoàn thành trong mã nguồn**

- Giữ toàn bộ dữ liệu 7.13: 322 câu đang công bố, 21 chương/78 bài KNTT, 57 chuyên đề lỗi sai, 99 sơ đồ tư duy.
- Thêm thẻ cập nhật nguồn câu hỏi và thẻ kho đang sử dụng ngay trên trang chính, không phải tìm qua menu ẩn.
- Cung cấp công cụ giáo viên nhập DOCX/CSV/JSON; gợi ý phân loại, chỉnh từng câu theo khối, chương, bài, phần, mức độ; cảnh báo câu trùng và công thức/hình bị thiếu; lưu bản nháp và xuất JSON riêng tư.
- Viết SQL Supabase, API cập nhật bằng khóa quản trị, API công khai chỉ trả nội dung, đồng bộ chung tới các mô-đun tự luyện và API chấm sau nộp.
- Thử nghiệm Chromium trực tiếp bằng cách nạp HTML/CSS/JS và dữ liệu: 1440 và 390 px, 322 câu/21 chương, không lỗi JS hoặc tràn ngang trong các luồng thử; nhập DOCX 21 câu chờ kiểm duyệt.
- Bộ kiểm thử hiện hành: `test_chem.js` 24/24, `test_grade77.cjs` 7/7, `test_713.cjs` đạt, `test_714.cjs` đạt, `test_714_mock.cjs` 5/5 ca có giả lập Supabase.

**Chưa nghiệm thu / giới hạn thực tế**

- Chưa kết nối được với Supabase hay tên miền Vercel thật của thầy. Trình duyệt kiểm thử chặn `localhost`, thử HTML/JS qua môi trường nạp trực tiếp.
- Không có chức năng chuyển đổi mọi đối tượng Equation/MathType/OLE/ảnh Word thành dữ liệu tương tác hoàn toàn tự động. Những câu như vậy cần giáo viên đọc Word gốc, gõ lại dữ kiện và đối chiếu.
- Không tuyên bố đã xác minh toàn bộ đáp án khoa học. Bộ quy tắc chỉ kiểm tra cấu trúc; việc giáo viên duyệt mới xác nhận chuyên môn.
- Chưa có quản lý quyền giáo viên theo tài khoản cá nhân; chỉ mã quản trị môi trường. Chưa lưu kết quả làm bài tập trung toàn trường.
- Trên GitHub Pages tĩnh không chạy API ghi/chấm; cần Vercel và Supabase để đồng bộ online.

**Bảo mật:** Không gửi đáp án trong GET `/api/public-bank`. Tệp JSON chờ thẩm định và mã dịch vụ Supabase luôn phải lưu riêng tư. Chỉ công bố câu có xác nhận giáo viên.
