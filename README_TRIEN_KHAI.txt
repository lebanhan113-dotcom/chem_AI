PHÒNG THI TRỰC TUYẾN – THPT HÒN ĐẤT – V11.6.0
Tác giả giải pháp: Giáo viên Lê Bá Nhẫn – Trường THPT Hòn Đất (An Giang)

1. TRƯỚC KHI ĐĂNG LÊN WEBSITE
- Cấu hình Supabase Project URL và publishable/anon key cho index.html bằng công cụ cau_hinh_supabase.html trong thư mục gốc của bộ bàn giao.
- Không đưa Supabase service_role/secret key, GitHub token hay Vercel token vào HTML.
- Kiểm tra RLS, đăng nhập tài khoản quản trị và phát hành đề đã duyệt trên Supabase.

2. CHẠY TRÊN GITHUB PAGES
- Tạo repository trên github.com; tải lên index.html và .nojekyll từ thư mục website_public (không tải các tệp ngoài thư mục này).
- Repository → Settings → Pages → Deploy from a branch → main / (root) → Save.
- Truy cập địa chỉ https://<tài-khoản>.github.io/<repository>/.

3. CHẠY TRÊN VERCEL
- Vào vercel.com → Add New → Project → Import repository GitHub chứa riêng thư mục website_public.
- Chọn Framework Preset: Other; Output Directory để trống; triển khai Production.
- Nếu repository gốc chứa nhiều thư mục, đặt Root Directory thành website_public.

4. KIỂM THỬ THẬT (BẮT BUỘC)
- Mở website bằng trình duyệt ẩn danh/điện thoại; chỉ các đề đã được phát hành mới hiện.
- Học sinh bắt đầu và nộp một bài thử; xác nhận máy chủ trả thành công.
- Trên một máy khác, giáo viên đăng nhập quản trị Supabase Auth và xem được bài vừa nộp.
- Khi giáo viên TẮT đáp án, học sinh không được xem lời giải qua API; khi BẬT, học sinh tra cứu lại được theo quy định.
- Xác minh số lượt truy cập, số người dự thi và phiên bản hiện hành.

5. LƯU Ý
- index.html là cổng HỌC SINH công khai, không chứa đáp án đã nhập.
- Tệp quan_tri_giao_vien.html đặt tại quan_tri_rieng; KHÔNG tải lên GitHub Pages/Vercel công khai.
- Trong gói bàn giao, cấu hình Supabase để trống. Chưa thể thu bài qua Internet khi chưa cấu hình hệ thống thật.
- Mã giao diện giáo viên 123123 KHÔNG thay thế cơ chế xác thực Supabase Auth.
