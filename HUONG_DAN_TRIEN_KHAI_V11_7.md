# PHÒNG THI TRỰC TUYẾN THPT HÒN ĐẤT – V11.7.0
**Tác giả giải pháp:** Giáo viên Lê Bá Nhẫn – Trường THPT Hòn Đất (Tỉnh An Giang)

## 1. Tệp mở WebApp
- **index.html** là trang học sinh được đăng công khai lên GitHub Pages hoặc Vercel. Truy cập `https://ten-mien/` hoặc `https://ten-mien/index.html`.
- **index.thml** là lỗi gõ tên tệp: GitHub Pages/Vercel mặc định nhận **index.html**, không nhận `index.thml` làm trang chủ.
- **quan_tri_giao_vien.html** là trang giáo viên lưu riêng, không đăng lên repository công khai, vì có chứa đề/đáp án nguồn.
- **supabase/migrations/** chứa SQL ghi phiên bản, nhật ký lưu trữ và dọn danh sách các bản phát hành cũ.
- **supabase/functions/release-sync/index.ts** là Edge Function xử lý đồng bộ ba nền tảng ở phía máy chủ.

**Trạng thái khi mới tải:** các HTML chưa điền Project URL/key và chưa gắn với tài khoản của trường. Chưa thể thu bài thật hay thực hiện đồng bộ thực tế ngay lập tức.

## 2. Đưa WebApp công khai lên GitHub Pages hoặc Vercel
1. Mở https://github.com/; tạo repository mới hoặc chọn repository của trường, ví dụ `phong-thi-hon-dat`.
2. Tải riêng `index.html` của thư mục `public_webapp/` lên thư mục gốc repository, nhánh `main`.
3. Với GitHub Pages: repository > Settings > Pages > Build and deployment > Deploy from a branch > `main` / `(root)` > Save.
4. Với Vercel: mở https://vercel.com/ > Add New > Project > Import repository GitHub trên > chọn production branch `main` > Deploy.
5. Thử mở website bằng trình duyệt ẩn danh. Nếu chưa kết nối Supabase, trang sẽ thông báo chưa có đề; **đây là hành vi an toàn** để tránh nhận bài giả.

## 3. Cấu hình Supabase để thu bài và duyệt đề
1. Vào https://supabase.com/dashboard, tạo/chọn dự án và chạy bộ SQL ban đầu `supabase_setup_v11.sql` từ gói dự án trước (nếu chưa chạy). Trong thư mục này, SQL phần phát hành không thay thế SQL ban đầu của phòng thi.
2. Kiểm tra bảng `public.app_admins`, `exams_public`, `exams_private`, bảng `exam_submissions` và các RPC bảo vệ đáp án đã hoạt động; bật RLS và thử bằng tài khoản không có quyền.
3. Vào **SQL Editor**, chạy theo đúng thứ tự:
   - `supabase/migrations/202611030001_release_sync.sql`
   - `supabase/migrations/202611030002_release_cleanup.sql`
4. Vào Authentication > Users, tạo tài khoản giáo viên; gán đúng UUID tài khoản vào `public.app_admins` theo lược đồ ban đầu.
5. Mở **quan_tri_giao_vien.html** ở máy giáo viên > đăng nhập bằng mã giao diện `123123` > Đồng bộ trực tuyến > nhập Supabase Project URL + publishable key > LƯU KẾT NỐI > đăng nhập Supabase Auth bằng tài khoản quản trị.
6. Nhập và duyệt đề Word/PDF, thiết lập điểm, phát hành các đề đủ điều kiện; sau đó kiểm tra chúng có mặt trong `exams_public` và hiển thị trên website học sinh.

> `123123` chỉ mở giao diện HTML; không phải mật khẩu bảo vệ database. Không được công khai secret/service-role key, GitHub token hoặc Vercel token trong HTML, GitHub hay cuộc trò chuyện.

## 4. Cài chức năng đồng bộ GitHub – Vercel – Supabase
1. Cài Supabase CLI (theo https://supabase.com/docs/guides/local-development/cli/getting-started), mở thư mục có `supabase/` và chạy:

```
supabase login
supabase link --project-ref MA_DU_AN_CUA_TRUONG
supabase functions deploy release-sync
```

2. Vào Supabase Dashboard > Edge Functions > Secrets, tạo **các khóa máy chủ** (không lưu trong HTML):
   - `GITHUB_TOKEN`: token chỉ có quyền Contents: Read and write với đúng repository của trường.
   - `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH` (ví dụ `main`).
   - `VERCEL_TOKEN`, `VERCEL_PROJECT_ID`, `VERCEL_PRODUCTION_URL` (URL thật `https://...vercel.app`), `VERCEL_TEAM_ID` nếu dùng team.
   - `SUPABASE_SERVICE_ROLE_KEY` nếu dự án đang dùng hệ khóa legacy và không có sẵn; không được đưa khóa này cho học sinh.
   - `ALLOWED_ORIGIN` nếu quản trị đang chạy từ một origin HTTPS cố định; khi quản trị mở qua file://, không nên cấu hình cứng origin đó nếu chưa kiểm thử CORS.
3. Trong Vercel, liên kết repository GitHub và production branch với đúng `GITHUB_BRANCH` đã khai báo.
4. Mở quản trị > **GitHub · Vercel · Supabase** > nhập số phiên bản mới, ví dụ `V11.7.1` > chọn **index.html** học sinh (không được chọn tệp quản trị) > nhấn **ĐỒNG BỘ & PHÁT HÀNH**.
5. Hệ thống sẽ lần lượt xác minh:
   - GitHub: API xác nhận đã ghi commit SHA của file mới.
   - Supabase: bản ghi phiên bản mới được lưu thành công trong database.
   - Vercel: production deployment READY với đúng commit SHA **và** website đang chạy trả đúng thẻ `hd-release-version`.
6. Mỗi thẻ dịch vụ chỉ hiện đúng chuỗi **“Đồng bộ Thành Công”** nếu dịch vụ đó đã được xác nhận; bản phát hành mới chỉ thành hiện hành sau khi cả ba điều kiện cùng thỏa mãn.
7. Nút **KIỂM TRA TRẠNG THÁI** có thể dùng khi mất kết nối hoặc trang bị đóng trong lúc chờ Vercel build.

## 5. Xử lý phiên bản cũ – không làm mất bài thi
Khi phiên bản mới được kích hoạt thành công:
- `app_release_sync` chỉ còn **một phiên bản đang phát hành**; các bản ghi phát hành cũ chuyển vào bảng lưu trữ riêng `app_release_sync_archive`, không xuất hiện trong danh sách phiên bản đang phát hành.
- GitHub `main` chứa file HTML mới nhất; Vercel tên miền production phục vụ bản mới.
- **Không xóa** các commit Git trước, deployment cần rollback, bài làm/điểm của học sinh hoặc phiên bản đề đã được sử dụng. Đó là dữ liệu cần bảo toàn.
- Muốn xóa tệp deployment Vercel cũ, chọn chính sách **Deployment Retention** trong Vercel > Project > Settings > Security theo yêu cầu lưu trữ; dịch vụ có quy tắc bảo vệ deployment hiện hành. Không thực hiện xóa không thể khôi phục đồng loạt từ nút phát hành.

## 6. Checklist nghiệm thu thực tế
- [ ] Mở website Vercel production bằng chế độ ẩn danh; màn hình hiển thị version đã phát hành.
- [ ] Giao diện giáo viên cho biết GitHub, Vercel và Supabase đều **Đồng bộ Thành Công**; kiểm tra commit SHA và bản ghi máy chủ.
- [ ] Website học sinh chỉ hiển thị đề đã được giáo viên duyệt và phát hành.
- [ ] Trên điện thoại khác, học sinh bắt đầu thi, nộp bài, máy chủ xác nhận; bài vừa nộp xuất hiện trong tài khoản quản trị.
- [ ] Khi TẮT đáp án, API không trả điểm, đáp án hoặc lời giải dù học sinh xem nguồn HTML.
- [ ] Khi BẬT đáp án, học sinh tra cứu lại được đúng bài bằng thông tin và mã bài.
- [ ] Lượt truy cập, số học sinh tham gia và bảng điểm Excel được kiểm tra với dữ liệu thử nghiệm.
- [ ] Khôi phục được hệ thống bằng bản phát hành đã lưu nếu có lỗi.

**Lưu ý:** Bộ mã này chưa được liên kết trực tiếp với tài khoản thật của trường trong phiên ChatGPT. Các trạng thái đồng bộ thực tế phải được kiểm tra tại dự án GitHub/Vercel/Supabase do nhà trường quản lý.
