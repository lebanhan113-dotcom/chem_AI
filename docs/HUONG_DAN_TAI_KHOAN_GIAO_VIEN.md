# HƯỚNG DẪN TỰ ĐĂNG KÝ TÀI KHOẢN GIÁO VIÊN – WEBAPP A4 VERCEL

## Chức năng mới

- Giáo viên có thể tạo tài khoản bằng email và mật khẩu trên website Vercel.
- Email được xác nhận bởi Supabase Auth. Chỉ email đã được **quản trị viên phê duyệt qua lời mời** mới tự nhận quyền `teacher`.
- Tài khoản chưa được mời luôn ở trạng thái `pending`, KHÔNG có quyền truy cập ngân hàng đề hoặc điểm của người khác.
- Giáo viên có quyền `teacher` tự nhập Word, duyệt, lưu ngân hàng đề, lập phòng, chấm bài, xuất Excel. API giới hạn dữ liệu theo `owner_uid`, không phải do frontend tự lọc.
- Quản trị viên có tab **MỜI GIÁO VIÊN** để cấp lời mời 30 ngày, xem trạng thái, sao chép liên kết đăng ký. Danh sách lời mời không gửi email; Supabase gửi email xác nhận đăng ký khi giáo viên đăng ký.
- Có nút **Quên mật khẩu?** gửi email đặt lại mật khẩu.

## 1. Cập nhật cơ sở dữ liệu Supabase

Dùng SQL Editor để chạy các migration THEO THỨ TỰ:

1. `supabase/migrations/202610300001_init.sql` – chỉ chạy nếu chưa từng chạy, để tạo các bảng cơ bản.
2. `supabase/migrations/202610310002_teacher_registration.sql` – chạy một lần để tạo bảng lời mời và quy tắc tự cấp quyền sau xác minh email.

**Nếu đã dùng Supabase CLI `db push` và migration A4 cơ bản đã chạy, không chạy lại migration đó bằng SQL Editor.** Để cập nhật, chạy CLI `npx supabase db push` khi đã link dự án, hoặc chạy **chỉ migration mới** qua SQL Editor, chọn một trong hai cách cho cùng một thay đổi. Tránh lặp migration trên hệ thống đang chạy.

## 2. Tạo tài khoản quản trị đầu tiên (một lần)

Vào Supabase Dashboard → Authentication → Users → tạo tài khoản quản trị bằng email do thầy/cô sở hữu và xác nhận email. Sau khi tài khoản được xác nhận, mở SQL Editor và chạy đoạn bên dưới với email thật (thay CHINH_XAC_EMAIL):

```sql
insert into public.app_profiles(id,role)
select id,'admin'
from auth.users
where lower(email)=lower('CHINH_XAC_EMAIL@example.com')
  and email_confirmed_at is not null
on conflict (id) do update set role='admin';
```

Kiểm tra:

```sql
select u.email,p.role from auth.users u
join public.app_profiles p on p.id=u.id
where lower(u.email)=lower('CHINH_XAC_EMAIL@example.com');
```

Việc tạo tài khoản **admin lần đầu** phải do chủ dự án thực hiện trong Supabase Dashboard/SQL Editor để không ai có thể tự nhận quyền cao nhất từ website công khai. Không để email hoặc mật khẩu admin cố định trong JavaScript.

## 3. Triển khai lại Edge Function

Trong thư mục gốc mã nguồn A4 (nơi có `supabase/`), chạy:

```powershell
npx supabase login
npx supabase link --project-ref YOUR_PROJECT_REF
npx supabase functions deploy exam-api
```

API bổ sung `auth.status`, `admin.inviteTeacher`, `admin.teacherInvites`. Chỉ người mang role `admin` được cấp lời mời. Các API giáo viên có sẵn vẫn kiểm tra token và quyền sở hữu bài thi.

## 4. Triển khai giao diện lên Vercel

Đưa NỘI DUNG thư mục `web/` (hoặc file ZIP `WEBAPP_A4_VERCEL_GIAO_VIEN_DEPLOY.zip`) lên repository GitHub dành riêng cho Vercel.

- Framework: **Other**
- Root Directory: `./` (nếu repo chỉ có giao diện)
- Build Command: để trống
- Output Directory: `.`
- Vercel cấp HTTPS URL `https://ten-du-an.vercel.app`

Nếu học sinh và giáo viên cần tự kết nối Supabase, mở **Kết nối** → nhập Project URL và publishable key → tải `config.js` → thay `config.js` trên repository và redeploy. Không đưa service_role hay sb_secret lên Vercel.

## 5. Thiết lập email xác nhận

Trong Supabase Dashboard → Authentication:

1. **Providers → Email:** bật email/password và **Confirm email** để giáo viên thực sự xác minh quyền sở hữu email trước khi cấp role.
2. **URL Configuration:** đặt **Site URL** là domain Vercel HTTPS; thêm domain này vào danh sách **Redirect URLs** (ví dụ `https://ten-du-an.vercel.app/**`). Dùng domain thực tế, không dùng tên ví dụ.
3. Với nhiều giáo viên, thiết lập SMTP riêng phù hợp. Dịch vụ email mặc định của Supabase có giới hạn và không phải giải pháp gửi email số lượng lớn lâu dài.

## 6. Quy trình sử dụng hằng ngày

**Quản trị viên:**

1. Vào WebApp → Giáo viên → đăng nhập bằng tài khoản admin.
2. Vào tab **Mời giáo viên** → nhập email giáo viên → bấm **CẤP LỜI MỜI**.
3. Bấm **SAO CHÉP LINK ĐĂNG KÝ** và gửi link cho giáo viên. Không có email lời mời tự động trong phiên bản này.

**Giáo viên được mời:**

1. Mở link đăng ký, chọn **TẠO TÀI KHOẢN GIÁO VIÊN**.
2. Điền tên, email được mời và mật khẩu mới (ít nhất 10 ký tự).
3. Kiểm tra email và nhấn liên kết xác minh của Supabase.
4. Quay về trang WebApp; đăng nhập. Nếu email đã xác nhận và lời mời còn hiệu lực, vai trò `teacher` sẽ được gán tự động.
5. Chọn **Ngân hàng đề → Nhập & duyệt Word**, sau đó tạo đề và phòng thi. Mỗi giáo viên chỉ xem được tài nguyên của chính mình.

**Giáo viên chưa được mời:** Tạo tài khoản Supabase vẫn được, nhưng không có quyền teacher; trang hiển thị **Đang chờ cấp quyền**. Nhờ quản trị viên mời đúng email đang sử dụng; nếu tài khoản đã xác minh trước lời mời, API sẽ tự cấp quyền khi quản trị viên cấp lời mời.

## 7. Kiểm thử trước khi dùng chính thức

- A đăng ký chưa được mời → trạng thái pending, không truy cập đề và bảng điểm.
- Admin mời email B → B đăng ký và xác minh email → B đăng nhập có quyền teacher.
- B chỉ thấy đề của B, không truy cập đề, phòng thi và bài làm của A hoặc giáo viên C.
- B yêu cầu khôi phục mật khẩu → nhận email và đặt mật khẩu mới.
- Học sinh không thấy đáp án/điểm; vẫn được bảo vệ bởi API `exam-api` phía máy chủ.

**Chưa cấu hình tài khoản Supabase/Vercel thật thay thầy/cô** vì không có quyền đăng nhập dự án; mã nguồn hoàn chỉnh đã được xuất để triển khai. Sau khi kết nối, cần kiểm thử lại với tài khoản thật và xác nhận tính chính xác về phân quyền.
