# BÁO CÁO NÂNG CẤP & KIỂM THỬ EDUPLAN AI 7.3

**Tác giả:** Lê Bá Nhẫn – Trường THPT Hòn Đất. **Ngày:** 25/10/2026.

## Đã hoàn thành và kiểm thử

| Hạng mục | Trạng thái / căn cứ |
|---|---|
| Giữ 1.958 câu nguồn, 78 bài KNTT | ĐẠT: byte-for-byte 3 JSON câu hỏi giống hệt v7.2; 809/473/676 câu |
| Trích xuất 11 DOC nguồn | ĐẠT: 57 mục LỖI SAI, ID riêng; 11 tài liệu nguồn DOCX có thể mở |
| Ánh xạ theo bài KNTT | ĐẠT CẤU TRÚC: mỗi chuyên đề có ít nhất 1 bài chính xác tồn tại trong curriculum.json; đây là ánh xạ nội dung, không phải xác minh độc lập mọi trường hợp |
| Giao diện Sổ lỗi sai | ĐẠT: menu → chọn Hóa 10/chương/bài → hiện đúng chuyên đề, mở nội dung |
| Đánh dấu đã hiểu/cần ôn | ĐẠT: DOM phản ánh thay đổi, lưu cục bộ bằng localStorage |
| Chuyển từ sổ sang luyện 5 câu | ĐẠT: lọc bài và dùng chung ngân hàng đã có; không tạo câu mới |
| Xuất DOCX theo bài | ĐẠT: Chromium tải file, python-docx mở; 2 trang thử nghiệm dựng sạch |
| Xuất toàn bộ 57 chuyên đề DOCX | ĐẠT: ZIP DOCX hợp lệ, đủ 57 mã chuyên đề; 56 trang được dựng để QA |
| Giao diện 1400px / 390px | ĐẠT TRONG LUỒNG THỬ: không phát sinh JS pageerror, không tràn ngang |
| Bản build/đường dẫn website thực tế trên GitHub Pages/Vercel | CHƯA: chưa có quyền tài khoản/hạ tầng để xuất bản, chưa xác nhận HTTP thực tế |
| Kết nối Supabase, thống kê người dùng toàn trường | CHƯA: đây là website tĩnh, không có cơ sở dữ liệu online |
| Độ chính xác toàn bộ lời giải và MathType trong 11 tài liệu | CHƯA: phần mềm chỉ bảo toàn nguồn và đưa cảnh báo, không tự khẳng định đã sửa đúng hết |

## Giới hạn phải thông báo

1. Một số phương trình, biểu thức hoặc hình MathType/OLE trong 11 tệp `.doc` chuyển qua văn bản thành `[pic]`; **đáp án và phép tính có thể bị thiếu**, cần bấm **Mở tài liệu gốc** để đối chiếu bản DOCX chuyển đổi.
2. Số 57 là **số chuyên đề lỗi sai theo heading nguồn**, không phải số câu hỏi mới được tạo; ngân hàng vẫn 1.958 câu. Tên chương trong tài liệu cũ **không trùng** tên chương SGK KNTT.
3. Mỗi chuyên đề có mã duy nhất kể cả khi tài liệu gốc lặp số: nhóm Kiềm–Kiềm thổ ghi “Lỗi sai 15” thay cho thứ tự kỳ vọng; nhóm Nhôm có một heading thiếu số.
4. Không gán khóa lời giải trích từ các tài liệu lỗi sai cho câu hỏi trong ngân hàng nếu chưa đối chiếu ID, dữ kiện và phiên bản câu.
5. Kiểm thử Chromium dùng **HTML/JS/JSON được nạp trực tiếp trong môi trường mô phỏng** vì trình duyệt kiểm thử hạn chế truy cập HTTP nội bộ; cần thử lại trên website thực sau khi deploy.

**Nghiệm thu đề xuất:** ĐẠT cho bản tương tác ngoại tuyến/tĩnh được kiểm thử; CHƯA NGHIỆM THU hệ thống online có đăng nhập, chấm điểm tự động và thống kê đa thiết bị.
