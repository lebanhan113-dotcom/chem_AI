# EDU EXAM – PHÒNG THI TRỰC TUYẾN
### Chạy trên GitHub + Vercel, không sử dụng Supabase
Tác giả giải pháp: **Lê Bá Nhẫn – Trường THPT Hòn Đất**

## A. HIỂU ĐÚNG KIẾN TRÚC

- **GitHub**: lưu mã nguồn, theo dõi phiên bản. GitHub KHÔNG tự lưu dữ liệu bài thi của học sinh.
- **Vercel Hosting**: hiển thị website `index.html`, `app.js`, bộ đọc Word và MathJax.
- **Vercel Functions**: tập tin `api/bridge.js` xử lý đăng nhập, quyền giáo viên, đề, phòng thi, làm bài và chấm điểm trên máy chủ.
- **Vercel Blob – Private Storage**: lưu tài khoản giáo viên, ngân hàng đề, đáp án và bài làm. Không dùng Supabase, không dùng `localStorage` làm kho kết quả tập trung.

> Dữ liệu có tính riêng tư chỉ lưu trong kho Blob **Private**. Tuyệt đối không chọn Public.

## B. TRIỂN KHAI 5 BƯỚC – KHÔNG CẦN POWERSHELL

### Bước 1. Tạo GitHub repository
1. Mở https://github.com/new.
2. Đặt tên ví dụ `phong-thi-ai-vercel`.
3. Chọn **Private**; tạo repository.
4. Nhấn **Add file → Upload files** rồi tải toàn bộ các file/thư mục trong ZIP (đặt ở thư mục gốc repository): `index.html`, `app.js`, `word.js`, `api/`, `lib/`, `vendor/`, `package.json`, `vercel.json`.
5. Nhấn **Commit changes**. Không đưa `.env`, mật khẩu hay khóa dịch vụ lên GitHub.

### Bước 2. Import vào Vercel
1. Mở https://vercel.com/new.
2. Chọn **Import Git Repository**, tìm repo trên, bấm Import.
3. Framework Preset: **Other**; Root Directory: `./` (gốc repository), không phải thư mục `web`.
4. Giữ build command ở chế độ mặc định. Vercel sẽ đọc `package.json`, cài thư viện `@vercel/blob` và nhận `/api/bridge` là API Node.js.
5. Nhấn **Deploy**. Địa chỉ `https://...vercel.app` đã mở được giao diện, nhưng API có thể báo chưa cấu hình đến khi hoàn thành bước 3 và 4.

### Bước 3. Tạo kho lưu trữ Vercel Private Blob
1. Trong Vercel, mở **Project → Storage**.
2. Chọn **Create Database / Add Storage → Blob**.
3. Đặt tên ví dụ `phong-thi-private`.
4. Chọn **Private** (không phải Public).
5. Kết nối Blob store vào đúng project Vercel. Vercel có thể cung cấp `BLOB_READ_WRITE_TOKEN` hoặc `BLOB_STORE_ID` qua cơ chế xác thực OIDC theo phiên bản.
6. Lưu và cập nhật deployment theo hướng dẫn trên Vercel.

### Bước 4. Cấu hình tài khoản quản trị
Trong **Vercel → Project → Settings → Environment Variables**, thêm ba biến sau (dùng cho Production):

| Tên biến | Giá trị |
|---|---|
| `ADMIN_EMAIL` | Email quản trị viên của thầy/cô |
| `ADMIN_PASSWORD` | **Mật khẩu MỚI**, mạnh, riêng tư; đừng dùng mật khẩu từng đưa vào chat |
| `SESSION_SECRET` | Chuỗi ngẫu nhiên dài ít nhất 32 ký tự, khác mật khẩu |

- Không tạo `config.js` của Supabase; không cần `Project URL`, `anon key`, `exam-api` Supabase.
- Không đặt giá trị thật vào README, GitHub, `index.html`, hoặc `.env.example`.
- Khi thay đổi môi trường, vào **Deployments → Redeploy** để phiên bản mới nhận các biến.

### Bước 5. Kiểm tra
1. Mở `https://TEN-DU-AN.vercel.app`.
2. Trang chủ phải ghi `API Vercel: Đã cấu hình`.
3. Chọn **GIÁO VIÊN** → đăng nhập email và mật khẩu tại Bước 4.
4. Chọn **Quản lý giáo viên**, nhập email giáo viên và mật khẩu tạm (ít nhất 10 ký tự).
5. Chọn **Nhập & duyệt Word** → tải `.docx` → kiểm tra 100% câu và đáp án, nhập biểu điểm, xử lý ảnh/công thức chưa đọc được.
6. Lưu đề vào ngân hàng đề, phát hành khi đã duyệt toàn bộ.
7. Tạo phòng thi và sao chép link cho học sinh, kiểm thử trên điện thoại khác.
8. Vào **Bảng điểm** để xem bài làm và xuất CSV mở được trong Excel.

## C. QUẢN TRỊ VIÊN VÀ GIÁO VIÊN
- `admin`: được đăng nhập khi email và mật khẩu khớp với `ADMIN_EMAIL`, `ADMIN_PASSWORD` trên máy chủ Vercel; được tạo / khóa / đặt lại mật khẩu giáo viên.
- `teacher`: do admin tạo, mật khẩu chỉ lưu dưới dạng `scrypt` có salt ở Blob Private; chỉ quản lý đề và phòng của mình. Giáo viên có thể tự đổi mật khẩu.
- **Không có chức năng đăng ký giáo viên công khai** để tránh cấp quyền tùy tiện.
- Mật khẩu admin không được nhúng vào client code. Để thay đổi, sửa `ADMIN_PASSWORD` trong Vercel và Redeploy.

## D. DỮ LIỆU ĐỀ THI VÀ ĐÁP ÁN
- Phân loại PHẦN I (MCQ), PHẦN II (Đúng–Sai), PHẦN III (Trả lời ngắn), PHẦN IV (Tự luận nếu có).
- Đáp án tô đỏ ở phần I/II; phần III dùng `Đáp án:` trên màn hình giáo viên.
- Không tự tạo câu hỏi giả. Câu có WMF/EMF/OMML không đọc chính xác sẽ có cảnh báo; giáo viên phải đối chiếu và bổ sung đúng ảnh/công thức gốc.
- Không tự chia điểm khi đề chưa có biểu điểm; giáo viên bắt buộc duyệt rồi mới phát hành.
- API học sinh không trả đáp án hoặc rubric; chỉ giáo viên được xem điểm và chấm tự luận.

## E. GIỚI HẠN QUAN TRỌNG TRƯỚC KHI THI CHÍNH THỨC
1. Vercel Blob là kho lưu tệp chứ không phải cơ sở dữ liệu giao dịch, không có ràng buộc giao dịch mạnh khi nhiều thiết bị đồng thời cập nhật một bài làm. Hiện phù hợp thử nghiệm hoặc phòng thi quy mô nhỏ; **chưa được chứng nhận cho kỳ thi chính thức**.
2. Học sinh đang vào phòng bằng mã + họ tên + lớp; chưa xác minh danh tính đầy đủ và chưa chống tạo nhiều lượt làm từ nhiều thiết bị.
3. Thiết lập lưu liên tục cần Internet ổn định; khi mất mạng, câu trả lời chỉ được lưu tạm trên trình duyệt đến khi đồng bộ trở lại.
4. Không có hệ thống reset mật khẩu giáo viên qua email. Quản trị viên đặt lại mật khẩu trực tiếp trong trang Quản lý giáo viên.
5. API có giới hạn kích thước JSON và ảnh; nếu Word chứa ảnh quá lớn, cần kiểm tra/tối ưu tệp nguồn và đối chiếu lại công thức trước khi tải lên.
6. Không có chức năng giới hạn tốc độ đăng nhập và chống dò mật khẩu theo IP ở phiên bản này. Trước khi vận hành chính thức cần bổ sung rate-limiting và xác thực mạnh hơn.
7. Cần sao lưu định kỳ ngân hàng đề/bảng điểm, kiểm thử nhiều thiết bị, chấm điểm, mất mạng, nộp trùng và khả năng phục hồi.

## F. KHI GẶP LỖI

| Thông báo | Giải pháp |
|---|---|
| Trang chủ báo API chưa cấu hình | Kiểm tra 3 biến quản trị và Private Blob, rồi Redeploy |
| API 404 | Đảm bảo `api/bridge.js` ở đúng gốc repository, Root Directory `./` |
| Không đăng nhập được | Phải dùng mật khẩu mới trong `ADMIN_PASSWORD` của Vercel, **không phải mật khẩu Supabase cũ** |
| Không lưu đề | Kiểm tra Storage: Private Blob và giới hạn dữ liệu/ảnh |
| Word thiếu công thức | Kiểm tra cảnh báo OMML/WMF, bổ sung đúng ảnh công thức từ nguồn |
| Nộp bài lỗi | Kiểm tra Internet, API Logs trong Vercel và lưu tạm bài làm trên trình duyệt |

## G. KIỂM TRA MÃ NGUỒN
- `tests/core.test.mjs` là bài kiểm tra thuật toán và kiểm tra không lộ đáp án.
- Chạy `npm test` trên môi trường có Node.js khi cần kiểm thử kỹ thuật; giáo viên không bắt buộc cài Node.js để triển khai qua GitHub/Vercel.
- Mã nguồn không chứa dữ liệu đề giả trong ngân hàng đề; chỉ có các fixture kiểm thử thuật toán độc lập.
