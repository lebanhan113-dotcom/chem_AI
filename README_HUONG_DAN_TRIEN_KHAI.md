# CHEM-MAP TUTOR AI – WEB ONLINE (bản demo tĩnh)

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## 1. Xuất bản nhanh qua Netlify Drop (không cần lập trình)

1. Giải nén `CHEM_MAP_TUTOR_AI_WEB_ONLINE_READY.zip` vào một thư mục.
2. Mở https://app.netlify.com/drop trong trình duyệt; đăng nhập để duy trì và quản lý website.
3. Kéo THƯ MỤC chứa `index.html` vào vùng thả trên trang Netlify Drop (hoặc dùng tùy chọn tải ZIP nếu có).
4. Đợi trang xác nhận triển khai, sao chép đường dẫn HTTPS có đuôi `netlify.app`.
5. Mở đường dẫn trên điện thoại và máy tính, thử chọn Hóa 10–12, chọn bài, làm bài và nộp bài.
6. Nhận quyền sở hữu và lưu URL trong tài khoản Netlify để còn cập nhật được.

Nguồn hướng dẫn chính thức: https://docs.netlify.com/start/quickstarts/netlify-drop-quickstart/

## 2. Triển khai trên Vercel (qua GitHub)

1. Tạo repository GitHub (nên là private nếu còn đang hiệu đính nội dung).
2. Tải các tệp `index.html`, `vercel.json`, `robots.txt` lên THƯ MỤC GỐC repository.
3. Vào https://vercel.com/new → Import Git Repository.
4. Chọn Framework Preset: **Other**; Root Directory: `./`.
5. Build Command: để trống (không chạy build); Output Directory: để trống.
6. Deploy; xác nhận đường dẫn HTTPS được Vercel tạo ra và thử trên điện thoại.

Nguồn hướng dẫn chính thức: https://vercel.com/docs/projects/deploy-from-cli

## 3. Quan trọng: phân biệt bản demo và hệ thống chính thức

- Đây là bản WebApp HTML tĩnh, **không có backend, không có đăng nhập nhiều tài khoản, không có cơ sở dữ liệu tập trung**.
- Học sinh có thể truy cập từ nhiều nơi qua HTTPS, nhưng lịch sử và thống kê của từng người chỉ lưu ở trình duyệt của họ; giáo viên **không** thấy báo cáo toàn trường.
- Ngân hàng 1.113 câu ở phiên bản kế thừa **chưa được giáo viên kiểm duyệt toàn bộ**; chỉ dùng để thử nghiệm, không dùng để kiểm tra lấy điểm chính thức.
- Không nhập thông tin học sinh thật hoặc dữ liệu cá nhân nhạy cảm khi chưa có phê duyệt và chính sách bảo vệ dữ liệu phù hợp.
- Các tệp `robots.txt` và thẻ `noindex` đề nghị công cụ tìm kiếm không lập chỉ mục, nhưng **không** bảo vệ nội dung khỏi người có đường dẫn. Muốn giới hạn truy cập, phải sử dụng chức năng xác thực của hosting hoặc backend.

## 4. Tệp trong gói

- `index.html`: trang WebApp chính, một file tự chứa HTML/CSS/JavaScript và dữ liệu mẫu.
- `vercel.json`: cấu hình bảo mật tiêu đề HTTP cho Vercel.
- `netlify.toml`: cấu hình site tĩnh, tiêu đề HTTP cho Netlify.
- `robots.txt`: đề nghị không lập chỉ mục demo.
- `README_HUONG_DAN_TRIEN_KHAI.md`: tài liệu này.

## 5. Nâng cấp sử dụng trong nhà trường

Để quản lý lớp, theo dõi số học sinh và thống kê truy cập xuyên thiết bị, chuyển phần máy chủ V7.2.1 sang hạ tầng có PostgreSQL/Supabase hoặc máy chủ Node.js với cơ sở dữ liệu bền vững, thiết kế phân quyền và bảo vệ dữ liệu trước khi mở rộng. **Không** đưa nguyên file backend SQLite thử nghiệm lên hosting serverless và mặc định rằng dữ liệu sẽ được lưu lâu dài.
