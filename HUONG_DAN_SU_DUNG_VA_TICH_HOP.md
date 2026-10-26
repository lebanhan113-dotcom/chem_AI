# EduPlan AI 7.14 – Bộ nâng cấp ngân hàng Đúng/Sai, máy chủ chấm điểm

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất  
**Đối tượng:** Giáo viên Hóa học, học sinh Hóa học 10–12 (Chương trình GDPT 2018, Kết nối tri thức).  
**Phạm vi:** Mô-đun WebApp riêng, **chưa ghép trực tiếp** vào repository EduPlan AI 7.14 hiện có hoặc website Vercel/Supabase.

## 1. Chạy trên Windows

1. Cài **Python 3.11+** từ python.org; khi cài bật **Add Python to PATH**.
2. Muốn nhập Word DOCX và giữ cấu trúc tốt nhất, cài thêm **LibreOffice** (lệnh `libreoffice` phải có trong PATH). Nhập CSV hoặc JSON thì không cần LibreOffice.
3. Giải nén thư mục, chạy `CHAY_WEBAPP_WINDOWS.bat`; lần chạy đầu hệ thống tự cài các thư viện Python qua Internet.
4. Mở trình duyệt tại **http://127.0.0.1:8765**.
5. Mật khẩu giáo viên xuất hiện trong cửa sổ máy chủ và được lưu trong `.teacher_password` (tự sinh ở lần khởi động đầu, chỉ giáo viên được biết). Tên đăng nhập: **giaovien**.
6. Giữ cửa sổ máy chủ đang chạy trong lúc sử dụng.

Trên Mac/Linux: `sh CHAY_MAC_LINUX.sh`, cũng truy cập địa chỉ trên. Bản này mặc định chỉ cho phép truy cập từ cùng máy tính; không công khai Internet.

## 2. Hướng dẫn học sinh

- Chọn **Khối → Chương → Bài → Phần II** trên thanh công cụ.
- Chọn **5 / 10 / 15 câu**. Mỗi câu Đúng/Sai có bốn ý a,b,c,d. Mỗi ý chọn Đúng hoặc Sai.
- Chọn **Nộp bài – Xem đáp án và lời giải**. Hệ thống lấy điểm từ máy chủ, hiển thị lại nguyên văn từng câu, từng ý, lựa chọn, khóa theo tài liệu nguồn, lời giải và những ý làm sai.
- Vào **Ôn lỗi sai** để luyện lại những câu bị nhầm. Danh mục lỗi lưu trên trình duyệt hiện hành, không đồng bộ qua máy khác.
- **Câu nguồn tự luyện:** chỉ để tự nhận định với các câu chưa có đáp án hoặc chưa bảo đảm đầy đủ; không đưa ra điểm hoặc tự suy đoán khóa đáp án.

## 3. Hướng dẫn giáo viên – tự động nhập nguồn

1. Trong thanh công cụ vào **Cập nhật nguồn**.
2. Nhập tên đăng nhập và mật khẩu giáo viên.
3. Chọn khối/chương mong muốn; tải một tệp Word `.docx`, JSON hoặc CSV.
4. WebApp tự phân nhóm. Với DOCX có tiêu đề dạng “HÓA HỌC 12 / CHƯƠNG 6”, WebApp ưu tiên nhận diện lại khối/chương từ tiêu đề; các chương chưa có bản đồ bài học sẽ hiển thị bài gợi ý.
5. Máy chủ trích xuất câu và mệnh đề, tạo dấu vân tay nội dung để **phát hiện trùng lặp**, phân loại theo bài/chương, phát hiện câu thiếu khóa/lời giải hoặc hình công thức nhúng chưa xác minh.
6. Câu **có đủ bốn mệnh đề, bốn khóa nguồn, lời giải riêng đủ dài và không có lỗi dữ liệu rõ ràng** được đưa vào chế độ luyện có chấm tự động. Các câu còn lại được **cách ly tự động** khỏi chế độ chấm nhưng vẫn hiện ở kho tự luyện nguồn.
7. Có thể chọn **Xem nguồn cảnh báo** hoặc **Sao lưu JSON giáo viên** sau nhập.

**Rất quan trọng:** “Tự kiểm duyệt” ở phiên bản này nghĩa là kiểm tra cấu trúc, trùng lặp, sự tồn tại của khóa nguồn và lỗi hiển thị; không phải chứng nhận tất cả đáp án đã được một chuyên gia xác nhận là đúng về khoa học. Không tự suy diễn đáp án khi nguồn thiếu. Các câu chưa đạt điều kiện không được sử dụng để chấm.

## 4. Ngân hàng tích hợp

- Số câu lịch sử đã giữ lại: 623 (Hóa 10–12).
- Bốn tài liệu Hóa 12 lần này: 154 lượt, nhận diện 4 câu trùng, bổ sung **150 câu không trùng**.
- Tổng cộng: **773 câu**; khi đóng gói có **112 câu đủ quy tắc nhập có khóa nguồn**, **661 câu ở kho nguồn tự luyện**. Đặc biệt hai tài liệu chương 7 và chương 8 mới không có đáp án nguồn đầy đủ nên không chấm tự động.
- Chỉ **2 trong 150 câu mới** vượt được các điều kiện nhập nguồn có khóa rất chặt (phần còn lại thiếu lời giải riêng, khóa hoặc có hình/công thức nhúng cần xác minh).
- Các tài liệu có công thức dạng MathType/OLE khó khôi phục sẽ có thông báo thay vì hiển thị sai công thức. Nếu cần chính xác tuyệt đối, mở lại tài liệu Word gốc để đối chiếu.

## 5. Bảo mật & tích hợp chính thức

- **Tuyệt đối không** đưa `questions_private.json`, `.teacher_password` hoặc toàn bộ ZIP giáo viên vào thư mục public hoặc nguồn tĩnh Vercel.
- Chỉ có API `/api/submit` trả lời giải sau khi nộp; `/api/catalog`, `/api/questions`, `/api/start` không trả về trường `correct` hoặc `explanations`.
- Endpoint `/api/admin/*` yêu cầu mật khẩu. Bản demo chưa có xác thực học sinh, rate-limit, cơ sở dữ liệu nhiều người dùng hoặc HTTPS; không mở Internet khi chưa bổ sung các chức năng này.
- Nếu ghép vào EduPlan chính thức, di chuyển bộ `server.py` logic và khóa đáp án vào backend có phân quyền; dùng migration JSON để không ghi đè dữ liệu có sẵn. Không đồng bộ trực tiếp vào Supabase vì chưa có quyền repository/schema của hệ thống chính thức.

## 6. Định dạng ngân hàng nhập từ CSV

CSV bắt buộc có trường `stemHtml`, `statements` (bốn ý ngăn bằng `||`). Để chấm được, thêm `correct` (bốn chữ Đ/S ngăn bằng `;`) và `explanations` (bốn giải thích ngăn bằng `||`); có thể thêm `lesson`, `lessonName`, `part=II`. Với JSON, dùng mảng `questions` gồm các đối tượng tương tự; `correct` là mảng bốn giá trị `true/false`.

## 7. Kiểm thử cục bộ

Đã thử: nạp ngân hàng, lọc chương/bài, tạo lượt 5 câu, nhận câu hỏi không kèm khóa đáp án, nộp để nhận lại khóa và lời giải từng ý, không cho nộp lại cùng một phiên, cô lập admin bằng mật khẩu, tải lại nguồn DOCX nhận 34 lượt trùng và 0 câu mới; đã kiểm tra bố cục và không tràn ngang trên Chromium 1440px và 390px (với dữ liệu API giả lập trong trình duyệt do chính sách môi trường kiểm thử chặn truy cập localhost từ Chromium).
