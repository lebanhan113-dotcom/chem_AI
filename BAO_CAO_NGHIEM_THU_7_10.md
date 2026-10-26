# BÁO CÁO KIỂM THỬ EDUPlan AI 7.10

Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Mục tiêu

Bỏ thanh sidebar/menu Học liệu & công cụ ẩn; đưa tất cả chức năng học tập ra bảng thẻ trực tiếp trên trang, bảo toàn dữ liệu và hành vi của bản 7.9.

## Thay đổi đã thực hiện

- 17 thẻ chức năng luôn xuất hiện trên trang chính, nhóm thành 3 cụm; không còn thanh menu ẩn.
- Các nút mở thẳng màn hình tương ứng và tự cuộn tới nội dung thao tác.
- Nút quay về toàn bộ chức năng từ bất kỳ trang nào.
- Giao diện 4 cột trên desktop, 2 cột trên điện thoại; không yêu cầu cuộn ngang để tìm công cụ.
- Tách riêng CSS `css/launchpad710.css` và script `js/launchpad710.js`; `index.html` khoảng 3,3 KB.
- Giữ nguyên toàn bộ tệp ngân hàng và học liệu bằng đối chiếu SHA-256.

## Kiểm thử đã thực hiện

| Hạng mục | Kết quả |
|---|---|
| Đọc 1.958 câu, 57 chuyên đề lỗi sai, 21 chương, 78 bài và 99 sơ đồ | Đạt trong Chromium |
| Hiển thị đủ 17 thẻ chức năng và mở 17 màn hình tương ứng | Đạt trên desktop và mobile trong Chromium |
| Trạng thái thẻ được chọn / tên trang đang mở | Đạt |
| Không tràn chiều ngang ở 1400 và 390 px | Đạt |
| Lỗi JavaScript ở luồng mở từng công cụ | Không ghi nhận |
| Tạo nhóm 5 câu khác ID, trả lời, lưu và mở lịch sử | Đạt trong Chromium |
| Kiểm tra công thức/dữ liệu Node.js | 24/24 đạt |
| Kiểm thử API chấm Node.js | 7/7 đạt |
| Ngân hàng và học liệu giữ nguyên SHA-256 | Đạt |
| Xác minh phản hồi serverless khi chạy trên Vercel thật | Chưa kiểm thử |
| Tính chính xác khoa học độc lập toàn bộ 1.958 câu | Chưa hoàn thành |

## Giới hạn và cảnh báo

- Bộ mã nguồn có thư mục `api` chứa khóa chấm server-side: chỉ lưu ở repository riêng tư và triển khai API qua Vercel. Không đưa gói này lên GitHub Pages công khai.
- Câu chưa có khóa thẩm định vẫn chỉ được tự giải; không tự tạo đáp án hoặc lời giải.
- Việc lưu kết quả vào nhiều thiết bị/tài khoản và thống kê toàn trường chưa được nghiệm thu thực tế.
- Trình duyệt kiểm thử ngăn truy cập địa chỉ phát triển; việc kiểm tra UI được thực hiện bằng cách nạp HTML/CSS/JS và dữ liệu gốc vào Chromium trong bộ nhớ, nên chưa chứng minh được URL Vercel vận hành.
