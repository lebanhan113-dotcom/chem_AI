# THIẾT LẬP QUẢN TRỊ VIÊN ĐẦU TIÊN

**Tài khoản:** `lebanhan113@gmail.com`  
**Quyền:** `admin` (quản trị viên, mời giáo viên, quản lý đề thuộc tài khoản).  
**Mật khẩu:** do chủ dự án nhập trực tiếp vào Supabase Auth hoặc vào công cụ thiết lập một lần, **không nằm trong file này hoặc mã frontend**.

## Cần chuẩn bị

- Đã tạo dự án Supabase của chính mình.
- Đã triển khai migrations `202610300001_init.sql` và `202610310002_teacher_registration.sql` (theo thứ tự). `app_profiles` cần tồn tại.
- Website Vercel đã dùng bản WebApp A4 giáo viên mới nhất và `config.js` đã trỏ đúng dự án.

## Cách 1: Dễ nhất, thao tác trong Supabase Dashboard

1. Mở https://supabase.com/dashboard và chọn dự án của mình.
2. Vào **Authentication → Users → Add user**. Nếu chưa có tài khoản, tạo tài khoản với email chính xác `lebanhan113@gmail.com` và mật khẩu riêng của mình; thực hiện xác minh email. Nếu tài khoản đã tồn tại, không tạo trùng và không vô tình đặt lại mật khẩu.
3. Vào **SQL Editor → New query**, mở file `setup/CAP_QUYEN_ADMIN_THU_CONG.sql`, sao chép toàn bộ và bấm **Run**.
4. Kết quả truy vấn cuối phải cho `role = admin` của email trên.
5. Mở website Vercel → **GIÁO VIÊN → ĐĂNG NHẬP**. Đăng nhập bằng email và mật khẩu được lưu bởi Supabase Auth.
6. Kiểm tra Dashboard hiển thị **Quản trị viên** và có tab **Mời giáo viên**.

## Cách 2: Công cụ thiết lập một lần (máy chủ dự án, không chạy trên Vercel)

1. Cài Node.js 20+ tại https://nodejs.org .
2. Mở PowerShell trong thư mục `PHONG_THI_A4_ADMIN_RELEASE`.
3. Chạy `node setup/admin-provision.mjs`.
4. Nhập **Project URL**, sau đó nhập **Supabase secret key (sb_secret_)** từ **Project Settings → API Keys**. Khóa được nhập ẩn; không đưa vào Vercel, GitHub hoặc phòng chat.
5. Nhập mật khẩu mà thầy/cô chọn, nhập lại, rồi xác nhận `YES`. Không đưa mật khẩu vào dòng lệnh hoặc tệp `.env` được chia sẻ.
6. Công cụ tạo tài khoản trong Supabase Auth nếu chưa có; nếu có tài khoản, mặc định **không thay đổi mật khẩu cũ** trừ khi thầy/cô xác nhận tại bước hỏi.
7. Công cụ cấp role `admin` và đối chiếu kết quả trong `app_profiles`.

> Trường hợp tạo mới bằng tài khoản chủ dự án có secret key, công cụ xác nhận email của tài khoản do chủ dự án trực tiếp cấp. Nếu email chưa được xác minh và tài khoản đã tồn tại, công cụ dừng để tránh cấp quyền ngoài ý muốn.

## An toàn

- Chỉ chủ dự án Supabase được sử dụng SQL Editor hoặc secret key. **Không** tải thư mục `setup`, file SQL, hoặc `sb_secret_` lên Vercel.
- Email quản trị viên không phải là mật khẩu. Không thêm bất kỳ 'admin password' vào HTML hoặc `config.js`.
- Mật khẩu từng được chia sẻ trong hội thoại; **nên đổi sang mật khẩu mới, duy nhất** sau khi đăng nhập.
- Bật MFA/2FA cho tài khoản vận hành khi đã cấu hình đầy đủ.
- Mỗi giáo viên mới được quản trị viên mời và chỉ được quyền `teacher`, không tự cấp quyền `admin`.
- Chưa thể khẳng định tài khoản đã tồn tại trên Supabase trước khi chủ dự án thực hiện bước thiết lập và kiểm tra `role = admin`.
