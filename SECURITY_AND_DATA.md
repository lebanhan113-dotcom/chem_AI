# Hướng dẫn quản lý dữ liệu khi EduPlan AI vận hành online

- Gói đầy đủ đi kèm `questions_private.json` có đáp án giáo viên. **Chỉ đưa vào repository PRIVATE**. Không mở công khai repository, không lưu vào thư mục chia sẻ học sinh.
- Bảo đảm `/data` là volume/disk bền vững. Không dùng miễn phí không có persistent disk để lưu thông tin học sinh.
- Giữ mật khẩu quản trị trong biến bí mật trên nền tảng hosting; bắt buộc tối thiểu 16 ký tự. Tuyệt đối không đăng ảnh chụp chứa mật khẩu hoặc mã học sinh.
- Chỉ nhập dữ liệu học sinh cần thiết theo quy định của trường; nên thử bằng tên giả trước khi đưa dữ liệu thật lên mạng. Có chính sách lưu giữ, xóa dữ liệu, cấp quyền và sao lưu định kỳ.
- Học sinh mới được cấp mã ngẫu nhiên dài 20 ký tự HEX. Giáo viên cần phát mã riêng và thu hồi/thay khi bị lộ. Bản hiện tại chưa có nút tự đổi mã; nếu triển khai đại trà cần bổ sung quy trình thay mã và xác thực mạnh hơn.
- 112/773 câu có khóa nguồn đủ điều kiện chấm theo quy tắc kiểm tra cấu trúc; không đồng nghĩa đã thẩm định độc lập kiến thức. Câu thiếu khóa không được chấm tự động.
- Kiến trúc hiện tại dùng SQLite và session trong bộ nhớ. Chỉ chạy **một worker, một replica**; phù hợp thử nghiệm theo lớp/trường nhỏ. Không dùng như nền tảng thi quy mô lớn hoặc ứng dụng lưu hồ sơ nhạy cảm chưa được kiểm toán an toàn thông tin.
- Sao lưu `/data` ngoài nền tảng và thường xuyên khôi phục thử. Nếu đã có dữ liệu từ bản chạy trên máy cá nhân, cần chuyển `edup_education.sqlite3`, `questions_private.json`, `source_import_history.json`, `media/` sang volume riêng trước khi sử dụng chính thức. Không ghi đè dữ liệu đang hoạt động.
- Khi công bố cho học sinh, chỉ chia sẻ tên miền HTTPS của WebApp, không chia sẻ file ZIP giáo viên và repository.
