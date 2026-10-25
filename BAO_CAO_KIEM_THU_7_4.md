# BÁO CÁO KIỂM THỬ EDUPLAN AI 7.4

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.  
**Phạm vi:** Bổ sung hướng dẫn thao tác theo từng chức năng vào WebApp 7.3; không sửa dữ liệu nguồn.

## Kết quả đã xác minh

| Kiểm tra | Kết quả |
|---|---|
| Cú pháp `js/app.js` và `js/docx-export.js` bằng Node 22 | Đạt |
| 14/14 mục menu có hướng dẫn tương ứng | Đạt |
| Mỗi mục có 5–7 bước và lưu ý riêng | Đạt |
| Thu gọn/mở lại; giữ trạng thái khi đổi tab | Đạt trong mô phỏng Chromium |
| Hướng dẫn vẫn có mặt sau khi chọn bài và bắt đầu luyện 5 câu | Đạt trong mô phỏng Chromium |
| Giao diện 1440×900 và 390×844; không tràn ngang | Đạt trong mô phỏng Chromium |
| Không phát sinh lỗi JavaScript trong các luồng đã thử | Đạt |
| Ngân hàng câu hỏi 809 + 473 + 676 = 1.958 câu | Khớp |
| Sổ lỗi sai 57 chuyên đề | Khớp |
| Bộ dữ liệu, tài liệu và hình ảnh so với bản 7.3 | Không thay đổi theo SHA-256 |
| Tệp ZIP bàn giao không bị hỏng | Đạt |

## Phương pháp và giới hạn

Trong môi trường này, Chromium chặn điều hướng tới `http://localhost` với `ERR_BLOCKED_BY_ADMINISTRATOR`. Do đó, phép thử giao diện thực hiện bằng cách **nạp HTML/CSS/JS trực tiếp vào Chromium và mô phỏng phản hồi `fetch` từ chính các tệp JSON đi kèm**. Đây là phép thử logic giao diện và tương tác trình duyệt, **chưa phải kiểm thử triển khai HTTP/HTTPS từ hosting thật**.

Chưa nghiệm thu: GitHub Pages / Vercel công khai; tài khoản đăng nhập, chấm điểm máy chủ, đồng bộ dữ liệu nhiều thiết bị và thống kê truy cập thực tế. Chúng cần hệ thống máy chủ có phân quyền nếu muốn triển khai sau này.

Không tự thêm khóa đáp án chưa được kiểm duyệt. Trợ lý ChatGPT là liên kết tới dịch vụ ngoài, không phải API AI nội bộ.
