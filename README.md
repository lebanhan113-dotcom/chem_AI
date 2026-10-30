# EDU EXAM A4 – Phòng thi trực tuyến (mã nguồn bàn giao)

Phiên bản A4 gồm **WebApp giao diện tiếng Việt**, **bộ đọc đề Word**, **ngân hàng đề và phiên bản**, **Edge Function**, **PostgreSQL migration**, **Storage riêng tư**, và **bài kiểm thử**. Giữ lại bản A3 gốc trong `web/legacy/index.html`.

## Cấu trúc thư mục

```
web/index.html                 – Giao diện đa màn hình
web/app.js                     – Nhập, duyệt, quản lý đề, phòng thi, học sinh, Excel
web/word.js                    – Trích xuất Word DOCX trong trình duyệt
web/api.js                     – Supabase Auth và Edge Function client
web/vendor/jszip.min.js       – JSZip, dùng khi đọc DOCX/xuất XLSX
web/vendor/mathjax.js         – MathJax và mhchem có sẵn
web/legacy/index.html         – Bản A3 ban đầu, lưu để đối chiếu
supabase/config.toml          – API public có xác thực tùy action ở mã nguồn
supabase/migrations/*.sql     – PostgreSQL, RLS, RPC và Storage
supabase/functions/exam-api/  – Backend kiểm tra quyền, chấm, lưu, QR
supabase/functions/exam-api/scoring.mjs – Quy tắc chấm không gửi cho học sinh
docs/                          – Hướng dẫn và dữ liệu gốc chờ duyệt
tests/                         – Bài kiểm thử frontend và scoring
```

## Cách sử dụng bộ đọc Word khi chưa có máy chủ

1. Mở `index.html` đóng gói độc lập hoặc `web/index.html` bằng Chrome/Edge.
2. Chọn **GIÁO VIÊN** → **Mở bộ nhập Word chưa kết nối**.
3. Chọn file `.docx` thật; đợi nhận diện các phần và đáp án. Ở bản mẫu Hóa 10 hiện nhận diện 15 + 2 + 4 câu.
4. Duyệt từng câu và bổ sung các ảnh không hiển thị; nhập điểm và quy tắc chấm.
5. Xuất JSON sao lưu. Các câu chưa giải quyết cảnh báo sẽ **không được phép phát hành online**.

## Cấu hình trực tuyến với Supabase

**Điều kiện:** Có một dự án Supabase do trường/giáo viên sở hữu, quyền quản trị Supabase và hosting tĩnh HTTPS.

1. Tạo Supabase Project trên https://supabase.com/dashboard.
2. Cài Supabase CLI theo hướng dẫn chính thức: https://supabase.com/docs/guides/cli.
3. Trong thư mục gốc của dự án (`PHONG_THI_A4`), chạy:

```sh
supabase login
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
supabase functions deploy exam-api
```

Nếu không dùng CLI cho database, có thể dùng SQL Editor của dự án để chạy toàn bộ tệp `supabase/migrations/202610300001_init.sql`. **Không chạy migration hai lần nếu đã dùng `supabase db push` thành công**.

4. Kiểm tra Edge Function `exam-api` có cấu hình `verify_jwt = false` theo `supabase/config.toml`. API tự kiểm tra token của giáo viên, token bài làm của học sinh, thời hạn và quyền sở hữu phòng trước khi thực hiện thao tác. Việc tắt kiểm tra JWT của nền tảng **không** có nghĩa là bỏ qua xác thực trong mã nguồn.
5. Trong Supabase Auth, tạo tài khoản giáo viên (email + mật khẩu). Để cấp quyền, chạy SQL trong dự án với email thật:

```sql
insert into public.app_profiles(id, role)
select id, 'teacher' from auth.users where email = 'GIAO_VIEN@TEN_TRUONG.VN'
on conflict (id) do update set role = 'teacher';
```

6. Đăng tải **toàn bộ thư mục `web`** lên hosting tĩnh như Netlify, Cloudflare Pages hoặc GitHub Pages, bảo đảm website có HTTPS. Đặt `web` làm thư mục publish và `index.html` làm trang chủ.
7. Trên web đã đăng tải, chọn **KẾT NỐI**. Điền **Project URL** và **publishable key** lấy từ Supabase Dashboard. **Không** dán `service_role`, `secret` hoặc access token Supabase quản trị vào web.
8. Nhấn **KIỂM TRA MÁY CHỦ**. Khi kết nối thành công, đăng nhập giáo viên và nhập Word.

## Quy trình sử dụng giáo viên

Nhập đề Word → xem cảnh báo → duyệt từng câu → xác nhận đáp án và điểm → **LƯU NGÂN HÀNG ĐỀ** → tạo phòng → chia sẻ link hoặc QR → kiểm tra bài làm → chấm tự luận → xuất Excel.

- PHẦN I: đọc màu đỏ tại chữ A/B/C/D. Không tự dự đoán khi không có chữ đỏ.
- PHẦN II: đọc màu đỏ là chỉ báo ban đầu, **luôn phải xác nhận** Đúng/Sai của từng ý và chọn quy tắc chấm.
- PHẦN III: đọc nhãn `Đáp án:`; chỉ chấm bằng quy tắc chấp nhận/sai số giáo viên thiết lập.
- PHẦN IV: tự luận, chờ giáo viên nhập điểm trước khi tạo điểm chính thức.

## Quy trình học sinh

Nhập mã phòng → kiểm tra đề thi → nhập họ tên, lớp → làm bài → tự lưu vào Supabase (kèm bản tạm trên trình duyệt) → nộp bài. Sau khi nộp, học sinh **không thấy điểm, đáp án, lời giải**.

## Bảo mật quan trọng

- Tất cả bảng có RLS và bị thu hồi quyền trực tiếp từ `anon` và `authenticated`; chỉ Edge Function phía máy chủ dùng secret key mới được truy cập.
- API học sinh trả câu hỏi **không kèm đáp án, quy tắc chấm, rubric**.
- Token học sinh là chuỗi ngẫu nhiên 192 bit; backend chỉ lưu **SHA-256** của token.
- Thời gian thi và điểm do backend xác nhận; không tin thời gian hoặc điểm được gửi từ trình duyệt.
- Đáp án gốc và bài làm vẫn cần bảo vệ bằng chính sách truy cập, sao lưu và giới hạn lưu giữ dữ liệu của đơn vị vận hành.
- API cho phép học sinh tham gia bằng họ tên + lớp. Không có chống gian lận danh tính/hạn chế spam tự động; trước thi quy mô lớn cần bổ sung định danh và rate limiting tại gateway.
- Hiện không triển khai cron job riêng. Bài hết hạn được đóng khi có yêu cầu từ học sinh hoặc khi giáo viên mở bảng điểm.

## Giới hạn đã phát hiện với file gốc Hóa 10

File Word `Nguon GK1 Hoa 10-001 - TRONDE - 3P.docx` có 21 câu, trong đó 8 hình WMF (công thức/hình) không thể hiển thị trực tiếp an toàn trên trình duyệt. Bộ đọc tạo **cảnh báo cụ thể**, không thay bằng nội dung ảo. Xem `docs/BAO_CAO_DUYET_DE_GOC.txt`; thay ảnh gốc bằng PNG/JPEG từ tài liệu trước khi duyệt. Điểm của đề gốc không được tự suy ra; cần nhập từ hướng dẫn chấm chính thức.

## Kiểm tra và trạng thái

```sh
node tests/test_scoring.mjs
python tests/test_browser.py
python tests/test_student_mock.py
```

Các bài kiểm tra nội bộ xác nhận: 21 câu của Word gốc; dấu màu đỏ; cảnh báo WMF; chấm MCQ/Đúng–Sai/trả lời ngắn; nộp không hiển thị điểm; tạo `.xlsx` đọc được. **Chưa kiểm thử live Supabase vì không có thông tin dự án của người dùng**; trước khi sử dụng thực tế cần chạy thử end-to-end trên tài khoản Supabase và domain HTTPS.

## Phần còn cần công việc trước khi áp dụng diện rộng

- Hoàn thiện tự chuyển WMF/EMF/OMML sang ảnh/formula bảo toàn nội dung gốc; hiện phải rà soát thủ công.
- Cấu hình hosting HTTPS và tên miền; đặt `ALLOWED_ORIGIN` để hạn chế nguồn gọi API sau khi chọn domain.
- Triển khai xác thực học sinh nếu trường cần chống trùng lượt thi.
- Rate limiting, log kiểm toán, chính sách sao lưu/khôi phục, thông báo hoạt động hệ thống và bảo vệ dữ liệu cá nhân.
- Kiểm thử thi đồng thời trên nhiều máy, mạng chập chờn, nhiều trình duyệt và quyền truy cập chéo.

**Không công bố là đã triển khai trực tuyến hoặc đã kiểm thử nhiều thiết bị khi chưa kết nối backend thật.**
