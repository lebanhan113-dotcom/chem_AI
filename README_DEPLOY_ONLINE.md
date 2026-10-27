# EduPlan AI 7.14+ – triển khai WebApp online

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất  
**Phiên bản:** ONLINE READY – FastAPI + SQLite + Docker + persistent volume.

## Nền tảng đề nghị: Render Web Service có persistent disk

**Vì sao không tải mỗi thư mục HTML lên Vercel?** Ứng dụng phải có backend Python để tự chấm Đúng/Sai, giữ kín đáp án và quản lý dữ liệu học sinh. Bộ này triển khai trọn cả backend + frontend cùng một tên miền HTTPS.

### Thao tác từng bước

1. Giải nén ZIP. Tạo **repository GitHub Private** (bắt buộc, vì `questions_private.json` chứa khóa đáp án của giáo viên), tải toàn bộ thư mục này vào gốc repository. KHÔNG dùng repository Public.
2. Vào https://dashboard.render.com/ → **New → Blueprint** → Connect GitHub → chọn repository private vừa tạo. Render sẽ đọc `render.yaml`.
3. Chọn triển khai dịch vụ với `plan: starter` và ổ lưu trữ bền vững **1 GB** gắn tại `/data` (gói có tính phí; kiểm tra bảng giá Render trước khi xác nhận).
4. Khi Render hỏi biến môi trường `EDUPLAN_ADMIN_PASSWORD`, đặt mật khẩu mạnh **tối thiểu 16 ký tự**. KHÔNG ghi mật khẩu vào repo hoặc gửi trong nhóm học sinh. `EDUPLAN_DATA_DIR=/data`, `EDUPLAN_ENV=production` đã được cấu hình.
5. Bấm **Apply/Deploy**. Sau khi trạng thái là Live, mở địa chỉ dạng `https://eduplan-ai-714-online.onrender.com` do Render cấp (tên cuối cùng có thể khác).
6. Trên trang WebApp: **Lớp & học sinh** → đăng nhập `giaovien` và mật khẩu đã đặt → tạo lớp → cấp mã truy cập cho học sinh → tạo/trộn đề → giao bài → xem điểm và câu sai.
7. Kiểm tra ngay URL `https://<ten-webapp>/healthz` trả `status: ok` và `persistent_data: true`.

### Tài khoản và dữ liệu
- Giáo viên: `giaovien` + mật khẩu từ biến môi trường.
- Học sinh: mã riêng từng em do giáo viên cấp (mã mới 80 bit), không cần tài khoản bên ngoài.
- Ngân hàng nguồn 773 câu Đúng/Sai chứa khóa **chỉ lưu phía backend**. 112 câu trước đây đủ điều kiện chấm tự động theo quy tắc cấu trúc; các câu khác vẫn tự luyện không chấm. Chỉ dùng các khóa nguồn đã được kiểm tra chuyên môn trước các kỳ kiểm tra chính thức.
- Kết quả, lớp, mã học sinh, ngân hàng bổ sung, lịch sử nhập nguồn và ảnh mới nằm trong `/data` → qua redeploy không bị ghi đè.
- Cần sao lưu định kỳ dữ liệu `/data` (SQLite/JSON) sang nơi an toàn được quản lý bởi trường. Persistent disk không thay thế backup.

### Railway (phương án thay thế)
1. Vào https://railway.com → tạo Project từ **private GitHub repository** cùng bộ mã nguồn.
2. Add **Volume**, mount tại `/data`. Điền biến `EDUPLAN_DATA_DIR=/data`, `EDUPLAN_ENV=production` và `EDUPLAN_ADMIN_PASSWORD=<mật khẩu mạnh>` trong cài đặt Railway.
3. Trong Networking → **Generate Domain**. Ứng dụng tự nghe trên `PORT` do Railway cấp, HTTPS do nền tảng cung cấp.
4. Không tạo hơn một replica vì SQLite + phiên làm bài đang dùng bộ nhớ của một tiến trình.

### Nếu dùng VPS/ Docker tự quản
```sh
docker build -t eduplan714 .
docker run -d --restart unless-stopped --name eduplan714 -p 10000:10000 -v eduplan714_data:/data -e EDUPLAN_DATA_DIR=/data -e EDUPLAN_ENV=production -e EDUPLAN_ADMIN_PASSWORD='THAY_BANG_MAT_KHAU_BAO_MAT_16_KY_TU' eduplan714
```
Trên VPS thật hãy đặt reverse proxy HTTPS, sao lưu volume, giới hạn quyền quản trị; KHÔNG dùng HTTP không mã hóa khi xử lý dữ liệu học sinh.

### Hạn chế và an toàn khi đưa vào trường học
- Kiến trúc phù hợp triển khai **một tiến trình** và quy mô lớp/thử nghiệm. Nếu nhiều trường cùng dùng, cần PostgreSQL, lưu trữ object, phiên phân tán và xác thực/ phân quyền mạnh hơn.
- Thi online hiện không có hệ thống chống gian lận toàn diện; không coi là nền tảng thi chuẩn hóa bảo mật cao.
- Basic Authentication của giáo viên được bảo vệ bằng HTTPS ở hosting; cần bật firewall/WAF và đổi mật khẩu định kỳ. Không chia sẻ mã học sinh.
- Tệp `questions_private.json` **không được đưa lên public GitHub, public bucket hay thư mục static**; sản phẩm vẫn an toàn vì backend chỉ cung cấp câu hỏi qua API được lọc khóa.
- Tự kiểm định nguồn chỉ xác minh cấu trúc, không xác minh khoa học tuyệt đối. Không tự phát hành các đáp án nghi vấn.
- Lần truy cập đầu sau deploy có thể mất ít phút để khởi tạo và sao chép hình/ câu hỏi vào `/data`.
- Giá/giới hạn của nhà cung cấp có thể thay đổi. Cần kiểm tra trước khi thanh toán.

### Cách chạy thử trên máy trước khi đưa lên hosting
```sh
python -m pip install -r requirements.txt
EDUPLAN_ADMIN_PASSWORD='MatKhauManhChoNhanVien123' EDUPLAN_ENV=production EDUPLAN_DATA_DIR=/tmp/eduplan_data uvicorn server:app --host 127.0.0.1 --port 8765
```
Truy cập http://127.0.0.1:8765/ (chỉ local, không phải link online). Tài liệu gốc nằm trong cùng ZIP.
