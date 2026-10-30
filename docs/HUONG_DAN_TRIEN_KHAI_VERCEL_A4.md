# HƯỚNG DẪN TRIỂN KHAI WEBAPP PHÒNG THI A4 TRÊN VERCEL

## 1. Sơ đồ hoạt động
Vercel cung cấp giao diện HTML/JS trên HTTPS. Supabase quản lý Authentication, PostgreSQL, Storage và Edge Function `exam-api`. Không có đáp án gốc trong thư mục giao diện phát hành.

## 2. Tệp cần dùng
- Đơn giản nhất: giải nén `WEBAPP_A4_VERCEL_DEPLOY.zip`, nội dung gồm `index.html`, `app.js`, `api.js`, `word.js`, `config.js`, `vendor/`, `vercel.json`.
- Nếu triển khai từ gói đầy đủ qua GitHub: thư mục root của Vercel phải là `web/`. Tránh chọn root của cả mã nguồn có `supabase/`, `docs/` và `archive/`.
- `vercel.json` được tạo với `framework: null`, không build, output là `.`; không có rewrite vì đường dẫn vào phòng dùng query `?room=`.

## 3. Cách 1 – GitHub + Vercel (khuyến nghị)
1. Truy cập https://github.com, đăng nhập, chọn New repository. Đặt ví dụ `phong-thi-a4-web`; chọn Private nếu phù hợp chính sách của trường.
2. Upload các tệp và thư mục nằm BÊN TRONG `VERCEL_DEPLOY` vào ngay thư mục gốc repo, sao cho GitHub hiển thị `index.html`, `app.js`, `api.js`, `word.js`, `config.js`, `vendor/`, `vercel.json`. Không upload tệp ZIP nguyên vẹn để dùng như website.
3. Vào https://vercel.com/new, đăng nhập, chọn Add New > Project (hoặc Import Project), kết nối GitHub và Import repo vừa tạo.
4. Framework Preset: `Other`. Root Directory: `./` nếu repo chỉ chứa frontend. Build Command: trống. Output Directory: `.` nếu được yêu cầu; `vercel.json` đã đặt cấu hình. Không cần Environment Variables cho Supabase publishable key ở bước triển khai tĩnh vì WebApp cho nhập sau.
5. Chọn Deploy, đợi Vercel thông báo hoàn thành. Vào địa chỉ `https://<ten-du-an>.vercel.app`. Tên chỉ là ví dụ; dùng URL thật Vercel cấp.
6. Trước buổi thi: mở WebApp -> KẾT NỐI -> nhập URL và publishable key -> nhấn TẢI config.js CHO VERCEL. Thay tệp config.js trong GitHub repo rồi chờ Vercel triển khai bản mới. Nếu không làm bước này, học sinh phải tự nhập URL/Key trên từng thiết bị.
7. Khi sửa frontend trên GitHub, Vercel có thể tự deploy bản mới từ commit đã kết nối.

## 4. Cách 2 – Vercel CLI không cần GitHub
1. Cài Node.js LTS trên Windows. Giải nén `VERCEL_DEPLOY` thành thư mục.
2. Mở File Explorer, mở thư mục `VERCEL_DEPLOY`, gõ `powershell` trên thanh địa chỉ, Enter.
3. Chạy `npx vercel@latest login`, hoàn tất đăng nhập theo hướng dẫn.
4. Chạy `npx vercel@latest --prod`. Chọn phạm vi tài khoản/tổ chức, tạo project mới và xác nhận thư mục hiện tại.
5. Sau khi hoàn thành, CLI cung cấp URL triển khai. Không cần chạy `server.py`, Python hoặc localhost.

## 5. Kết nối với Supabase
Vercel KHÔNG thay thế backend Supabase của A4. Trước đó cần tạo Project Supabase, chạy SQL migration từ `supabase/migrations/202610300001_init.sql`, triển khai Edge Function `exam-api`, tạo tài khoản Auth và cấp `teacher` trong bảng `app_profiles`.
1. Mở trang WebApp trên URL Vercel.
2. Chọn KẾT NỐI, điền Project URL dạng `https://project-ref.supabase.co` và Publishable key `sb_publishable_...` (hoặc anon key tương thích).
3. Nhấn LƯU CẤU HÌNH rồi KIỂM TRA MÁY CHỦ. Việc lưu này ở trình duyệt hiện tại, không tự đồng bộ cấu hình sang các thiết bị khác.
4. Nếu health báo lỗi: vào Supabase Dashboard > Edge Functions > `exam-api` > Logs, kiểm tra deploy, cấu hình JWT/CORS và URL.
5. Sau khi có domain Vercel chính thức, cấu hình Supabase Edge Function secret `ALLOWED_ORIGIN` trùng origin chính xác, ví dụ `https://ten-du-an.vercel.app`. Khi đổi sang tên miền riêng, phải cập nhật giá trị phù hợp. CORS không thay thế xác thực, rate limit hay phân quyền.

## 6. Kiểm tra buổi thi
- Máy giáo viên: Đăng nhập, nạp Word, kiểm tra 21 câu Hóa 10 (15+2+4), xử lý ảnh WMF, nhập biểu điểm, duyệt, lưu ngân hàng, tạo phòng.
- Máy học sinh: mở `https://ten-du-an.vercel.app/?room=MA_PHONG` hoặc mã QR, nhập họ tên và lớp, làm bài, nộp bài. Không được hiện đáp án hay điểm.
- Máy giáo viên: kiểm tra bài nộp, chấm tự luận nếu có, xuất Excel; kiểm tra gửi bài khi mạng chập chờn.

## 7. Lỗi thường gặp
- Vercel 404: kiểm tra Vercel > Project Settings > Build and Deployment > Root Directory `./` hoặc `web`, Output Directory `.`, và `index.html` có trong thư mục deploy.
- Thiếu CSS/JS, không bấm được nút: phải upload cả `vendor`, `app.js`, `api.js`, `word.js`, không chỉ mỗi `index.html`. Kiểm tra Developer Tools > Network / Console.
- Nút KIỂM TRA MÁY CHỦ lỗi: frontend đã có HTTPS nhưng `exam-api` chưa triển khai hoặc Supabase URL/Key sai.
- Đăng nhập được nhưng không lưu đề: kiểm tra quyền `teacher`, migration và Storage của Supabase.
- Học sinh không có link QR: phải tạo phòng từ website HTTPS đã được triển khai, không dùng file HTML mở bằng `file://`.
- Nhiều người không thấy cùng bài làm: chưa triển khai backend thật hoặc frontend đang trỏ đến các dự án Supabase khác nhau.

## 8. Giới hạn và an toàn
Không đưa `service_role`, `sb_secret`, mật khẩu DB, tệp `.env`, `docs` chứa đề/đáp án hay `supabase` lên Vercel dưới dạng tệp công khai.
Các đề chưa duyệt không được phát hành. Bộ đề gốc có tám hình WMF cần xử lý; các quy tắc chấm vẫn phải xác nhận. Việc tải lên Vercel không tự đảm bảo năng lực chống gian lận, xác thực học sinh, kết nối đa thiết bị hoặc mức độ an toàn của một kỳ thi quan trọng. Cần kiểm thử live sau khi kết nối Supabase thật.

## Tham khảo chính thức
- https://vercel.com/docs/deployments
- https://vercel.com/docs/builds/configure-a-build
- https://vercel.com/docs/project-configuration/vercel-json
- https://supabase.com/docs/guides/functions/deploy
