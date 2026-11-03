# PHÒNG THI TRỰC TUYẾN THPT HÒN ĐẤT — V11.6
## Đồng bộ GitHub, Vercel và Supabase có kiểm chứng

**Tác giả giải pháp:** Giáo viên Lê Bá Nhẫn – Trường THPT Hòn Đất (Tỉnh An Giang).

### Tệp trong gói

- `index.html`: cổng học sinh **công khai**, không nhúng đề và đáp án riêng. Được tải lên GitHub qua chức năng phát hành.
- `quan_tri_giao_vien.html`: ứng dụng quản trị **riêng tư**. Không tải tệp này lên website công khai.
- `supabase/migrations/202611030001_release_sync.sql`: ghi trạng thái đồng bộ phiên bản trên máy chủ.
- `supabase/functions/release-sync/index.ts`: Edge Function thay mặt tài khoản quản trị đẩy GitHub và kiểm tra Vercel.
- `supabase/config.toml`: yêu cầu JWT khi gọi Edge Function.

**Lưu ý quan trọng:** Gói này là mã có thể cấu hình, **không phải** là một bản đã liên kết với tài khoản GitHub/Vercel/Supabase thật. Mỗi nền tảng chỉ báo **“Đồng bộ Thành Công”** sau khi máy chủ xác nhận. Không bao giờ đặt GitHub token, Vercel token hoặc Supabase secret/service-role key vào HTML công khai hoặc gửi trong chat.

## Bước 1 — Chuẩn bị ba dịch vụ (thực hiện 1 lần)

1. Mở https://github.com/ → tạo/chọn repository chứa `index.html` ở thư mục gốc, nhánh chính ví dụ `main`.
2. Mở https://vercel.com/ → Add New Project → Import repository GitHub nói trên → Production Branch `main`. Đảm bảo các lần push lên `main` tự tạo **Production deployment**.
3. Mở https://supabase.com/dashboard → chọn dự án đã triển khai phòng thi V11.5 và bảng `app_admins`.
4. Tài khoản giáo viên phải được thêm vào `public.app_admins` (bằng UID Supabase Auth), **không dùng mã giao diện `123123` làm quyền máy chủ**.
5. Có tên miền HTTPS của Vercel, ví dụ `https://phong-thi-xxx.vercel.app`. Đây phải là trang public production của chính repository đó.

## Bước 2 — Nâng cấp Supabase

1. Trong **Supabase → SQL Editor**, chạy `supabase/migrations/202611030001_release_sync.sql` **sau** SQL phòng thi V11 hiện có.
2. Kiểm tra `public.app_release_sync` đã tạo, RLS được bật và tài khoản `anon` không có quyền đọc/ghi.
3. Cài Supabase CLI (theo tài liệu Supabase), tại thư mục dự án chứa `supabase/` chạy:

```bash
supabase login
supabase link --project-ref YOUR_PROJECT_REF
supabase functions deploy release-sync
```

4. Trong **Supabase → Edge Functions → Secrets**, thiết lập các biến môi trường **ở phía máy chủ**:

| Biến | Ý nghĩa |
|---|---|
| `GITHUB_TOKEN` | Fine-grained PAT/GitHub App token có quyền **Contents: Read and write** với **một repository này**. |
| `GITHUB_OWNER` | Tên chủ repository. |
| `GITHUB_REPO` | Tên repository, không có `.git`. |
| `GITHUB_BRANCH` | `main` (hoặc đúng Production Branch đã chọn). |
| `VERCEL_TOKEN` | Vercel Access Token để **đọc trạng thái deployment**. |
| `VERCEL_PROJECT_ID` | Project ID tại Vercel → Project Settings. |
| `VERCEL_TEAM_ID` | Chỉ cần nếu Vercel project thuộc team. |
| `VERCEL_PRODUCTION_URL` | URL HTTPS production đã hoạt động. |
| `ALLOWED_ORIGIN` | Origin của trang quản trị được phép gọi, nếu sử dụng website quản trị riêng HTTPS. |

Các biến `SUPABASE_URL` và `SUPABASE_SERVICE_ROLE_KEY` thường do Supabase cung cấp sẵn cho Edge Functions (nếu dùng hệ khóa legacy); tuyệt đối không đưa chúng vào client. Nếu project sử dụng mô hình khóa mới không cung cấp `SUPABASE_SERVICE_ROLE_KEY`, cần cập nhật Edge Function theo cơ chế server secret của dự án trước khi deploy.

**Lưu ý:** Không tải `quan_tri_giao_vien.html` lên repository công khai. Để giáo viên tải file trong máy, dùng HTML tải về; nếu hosting quản trị riêng thì đặt sau lớp đăng nhập thực.

## Bước 3 — Phát hành phiên bản mới từ giao diện

1. Mở `quan_tri_giao_vien.html` trên máy giáo viên.
2. Đăng nhập giao diện bằng passcode `123123` (mã giao diện, **không bảo vệ database**).
3. Vào **Đồng bộ trực tuyến**, nhập **Supabase Project URL + publishable key**, nhấn **LƯU KẾT NỐI**. Kiểm tra RLS, đăng nhập Supabase Auth bằng tài khoản quản trị thật.
4. Vào **GitHub · Vercel · Supabase** ở menu trái.
5. Nhập phiên bản mới, ví dụ `V11.6.1` (không trùng phiên bản đã phát hành).
6. Chọn tệp `index.html` **học sinh** từ gói này. Ứng dụng sẽ từ chối tệp thiếu `PUBLIC_STUDENT_ONLY=true`.
7. Nhấn **ĐỒNG BỘ & PHÁT HÀNH PHIÊN BẢN MỚI** và xác nhận.
8. Trạng thái sẽ chuyển lần lượt:
   - **GitHub:** “Đồng bộ Thành Công” nếu GitHub xác nhận commit SHA.
   - **Supabase:** “Đồng bộ Thành Công” nếu máy chủ lưu được bản ghi phát hành.
   - **Vercel:** “Đồng bộ Thành Công” chỉ khi API Vercel báo production deployment **READY** của chính commit đó **và** website production thực tế trả về đúng release marker.
9. Khi đủ cả ba điều kiện, phiên bản mới được kích hoạt; bản cũ không còn là phiên bản đang phát hành.

**Không thể gọi việc bấm nút là “đã đồng bộ”**. Nếu có lỗi hoặc mất mạng, kiểm tra trạng thái và thông báo; KHÔNG tự khẳng định thành công.

## Bước 4 — Xử lý phiên bản cũ

Sau khi xác minh phiên bản mới, Supabase chuyển nhãn **hiện hành** sang bản mới và vô hiệu hóa trạng thái hiện hành của bản ứng dụng trước. Việc phát hành lên production của Vercel cũng trỏ tên miền đến bản mới.

Để giữ an toàn, tính năng **không xóa** lịch sử commit GitHub, deployment Vercel dùng cho rollback, phiên bản đề thi đã giao, kết quả và bài làm học sinh. Xóa lịch sử GitHub thường đòi hỏi rewrite/force-push và có thể làm hỏng đồng bộ; xóa deployment Vercel quá sớm có thể mất khả năng rollback. Muốn dọn deployment cũ, vào Vercel → Project → **Settings → Deployment Retention** và đặt chính sách lưu giữ phù hợp. **Không** xóa bảng `exam_submissions` hoặc kho đề đã dùng để chấm bài.

## Bước 5 — Kiểm thử nghiệm thu thật

- Mở website Vercel production bằng trình duyệt ẩn danh, xem nhãn phiên bản vừa phát hành.
- Vào mục phát hành: cả ba trạng thái phải ghi chính xác **“Đồng bộ Thành Công”**.
- Trên điện thoại học sinh, chỉ thấy đề đã được giáo viên duyệt và phát hành từ Supabase.
- Nộp bài thử, kiểm tra bài xuất hiện trong tài khoản quản trị Supabase Auth trên máy giáo viên.
- Tắt đáp án: học sinh không thể tra cứu đáp án qua API. Bật đáp án: tra cứu được bằng mã bài và thông tin thí sinh.
- Mở phần Logs của Edge Function nếu trạng thái còn “Đang chờ xác nhận”; kiểm tra cấu hình GitHub/Vercel và Production Branch.

## Lỗi thường gặp

| Hiện tượng | Kiểm tra |
|---|---|
| GitHub báo 401/403 | Token hết hạn, sai quyền Contents, sai Owner/Repo. |
| GitHub báo 409/422 | SHA cũ hoặc nhánh đã thay đổi; tạo phiên bản mới và thử lại. |
| Vercel cứ chờ | Chưa liên kết GitHub, sai `VERCEL_PROJECT_ID`/`VERCEL_TOKEN`, build lỗi hoặc URL production chưa trả marker mới. |
| Supabase 401 | Phiên Supabase Auth hết hạn hoặc Edge Function chưa deploy. |
| Supabase 403 | User chưa được thêm vào `app_admins`. |
| Không có đề học sinh | Chưa phát hành đề lên Supabase hoặc sai URL/key công khai. |
| Xuất hiện nút “ĐỒNG BỘ” bị khóa | Chưa lưu cấu hình Supabase, chưa đăng nhập Supabase Auth. |

## Các liên kết chính thức

- GitHub: https://github.com/
- Vercel: https://vercel.com/
- Supabase: https://supabase.com/
- GitHub Contents API: https://docs.github.com/en/rest/repos/contents
- Vercel Git Integration: https://vercel.com/docs/git
- Supabase Edge Functions: https://supabase.com/docs/guides/functions

**Kết luận:** V11.6 hỗ trợ đồng bộ ba dịch vụ theo một quy trình có xác thực và kiểm chứng. Cho đến khi đã cài đặt quyền và các secret trên dự án thật, kết quả chính xác là **“Chưa kết nối / Đang chờ xác nhận”**.
