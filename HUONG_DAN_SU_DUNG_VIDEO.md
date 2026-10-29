# HƯỚNG DẪN SỬ DỤNG EDUVIDEO FLOW AI V4.2

**Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất**

## I. Mở ứng dụng

1. Giải nén đầy đủ `EDUVIDEO_FLOW_AI_V4_2_HUONG_DAN_VIDEO.zip`, giữ nguyên thư mục `static/tutorials`.
2. Nháy đúp **`index.html` ở thư mục gốc** để xem giao diện, video và hướng dẫn bằng văn bản ngoại tuyến.
3. Nếu muốn sản xuất video bằng Gemini, Nano Banana và Veo 3.1: cấu hình `.env`, khởi chạy backend bằng `START_WINDOWS.bat` hoặc `START_MAC_LINUX.sh`, sau đó mở `http://localhost:8000/index.html`.
4. Nhấn tab **Hướng dẫn sử dụng**, chọn **12 dạng video dạy học**, **8 bước sản xuất**, hoặc **Tổng quan**.
5. Chọn hướng dẫn bên trái, nhấn Play trong trình phát, đọc từng bước ngay bên dưới. Có thể nhấn **Tải video hướng dẫn MP4** để lưu clip.
6. Ở màn hình **Tạo video**, nhấn **Xem hướng dẫn dạng video này** để mở đúng video theo dạng đã chọn.
7. Ở màn hình **Video cuối**, xem **Cách sử dụng sản phẩm** tương ứng với video vừa tạo.

**Ghi chú:** 21 video hướng dẫn đi kèm là clip minh họa bằng chữ (mỗi clip khoảng 16 giây), không phải video ghi hình trực tiếp thao tác trong WebApp; không có lời đọc. Đây là video MP4 thực tế có thể phát và tải về ngoại tuyến.

## II. Hướng dẫn theo từng dạng sản phẩm nội dung (12 loại)

### Khởi động bài học
**Mục tiêu:** Gây tò mò trong những phút đầu tiết học

**Video hướng dẫn:** `static/tutorials/01_khoi-ong-bai-hoc.mp4`

1. **Chuẩn bị nội dung:** Chọn Khởi động bài học; nhập câu hỏi hoặc tình huống gây tò mò, chưa tiết lộ đáp án.
2. **Tạo và kiểm tra sản phẩm:** Chọn 8–24 giây, phong cách phù hợp; tạo video rồi kiểm tra câu hỏi mở đầu và hình ảnh.
3. **Sử dụng trong tiết học:** Phát video ở đầu tiết; tạm dừng để học sinh dự đoán, sau đó dẫn vào chủ đề.
**Lưu ý:** Giữ câu hỏi ngắn, tránh tiết lộ kết luận ngay trên màn hình.

### Giới thiệu bài học
**Mục tiêu:** Định hướng cho học sinh về nội dung sắp học

**Video hướng dẫn:** `static/tutorials/02_gioi-thieu-bai-hoc.mp4`

1. **Chuẩn bị nội dung:** Nhập mục tiêu, tình huống và khái niệm nền của bài mới.
2. **Tạo và kiểm tra sản phẩm:** Chọn Giới thiệu bài học, 16–32 giây; duyệt mạch mở đầu – mục tiêu – chủ đề.
3. **Sử dụng trong tiết học:** Phát trước khi vào bài; yêu cầu học sinh nêu điều mình sẽ tìm hiểu.
**Lưu ý:** Chỉ nêu các mục tiêu chính, không nhồi quá nhiều kiến thức.

### Đặt vấn đề
**Mục tiêu:** Tạo mâu thuẫn nhận thức để khơi gợi thảo luận

**Video hướng dẫn:** `static/tutorials/03_at-van-e.mp4`

1. **Chuẩn bị nội dung:** Nhập một vấn đề thực tế hoặc hiện tượng cần giải thích; nêu rõ câu hỏi trung tâm.
2. **Tạo và kiểm tra sản phẩm:** Chọn Đặt vấn đề; kiểm tra cảnh cuối phải mở ra câu hỏi chưa được giải ngay.
3. **Sử dụng trong tiết học:** Cho học sinh thảo luận cặp đôi hoặc nhóm trước khi khám phá lời giải.
**Lưu ý:** Tình huống phải có cơ sở khoa học, tránh dữ kiện gây hiểu lầm.

### Giải thích khái niệm
**Mục tiêu:** Biến khái niệm trừu tượng thành hình ảnh dễ hiểu

**Video hướng dẫn:** `static/tutorials/04_giai-thich-khai-niem.mp4`

1. **Chuẩn bị nội dung:** Nhập định nghĩa chính xác, ví dụ và dấu hiệu nhận biết.
2. **Tạo và kiểm tra sản phẩm:** Chọn Giải thích khái niệm; kiểm tra mô phỏng, thuật ngữ và lời thoại.
3. **Sử dụng trong tiết học:** Phát video; yêu cầu học sinh tự diễn đạt khái niệm và đưa ví dụ mới.
**Lưu ý:** Hiển thị công thức hoặc ký hiệu khoa học bằng lớp chữ chính xác.

### Trình bày kiến thức
**Mục tiêu:** Tóm tắt các ý cốt lõi theo thứ tự logic

**Video hướng dẫn:** `static/tutorials/05_trinh-bay-kien-thuc.mp4`

1. **Chuẩn bị nội dung:** Nhập các luận điểm hoặc quy tắc theo thứ tự và ví dụ minh họa.
2. **Tạo và kiểm tra sản phẩm:** Chọn Trình bày kiến thức; dùng 24–64 giây, duyệt từng cảnh và ý chuyển tiếp.
3. **Sử dụng trong tiết học:** Phát theo đoạn; tạm dừng để học sinh lập sơ đồ hoặc ghi ý chính.
**Lưu ý:** Mỗi cảnh tập trung một ý kiến thức, không vượt thời lượng lời thoại.

### Minh họa tình huống
**Mục tiêu:** Cho học sinh quan sát một tình huống cụ thể

**Video hướng dẫn:** `static/tutorials/06_minh-hoa-tinh-huong.mp4`

1. **Chuẩn bị nội dung:** Nêu nhân vật, hoàn cảnh, quyết định và hậu quả trong tình huống.
2. **Tạo và kiểm tra sản phẩm:** Chọn Minh họa tình huống; kiểm tra Character/Environment Bible và hội thoại.
3. **Sử dụng trong tiết học:** Phát video; hỏi học sinh nhân vật nên xử lý thế nào và vì sao.
**Lưu ý:** Giữ nhân vật nhất quán, tránh tình huống định kiến hoặc phản cảm.

### Kể chuyện giáo dục
**Mục tiêu:** Dạy học thông qua câu chuyện có thông điệp

**Video hướng dẫn:** `static/tutorials/07_ke-chuyen-giao-duc.mp4`

1. **Chuẩn bị nội dung:** Nhập bối cảnh, nhân vật, xung đột, diễn biến và bài học rút ra.
2. **Tạo và kiểm tra sản phẩm:** Chọn Kể chuyện giáo dục; duyệt lời thoại tự nhiên và tính liên tục các cảnh.
3. **Sử dụng trong tiết học:** Phát toàn bộ truyện; yêu cầu học sinh phân tích hành động và thông điệp.
**Lưu ý:** Nội dung phù hợp độ tuổi; nhân vật, trang phục không thay đổi tùy tiện.

### Mô phỏng hiện tượng
**Mục tiêu:** Quan sát các quá trình khó hoặc nguy hiểm khi làm thật

**Video hướng dẫn:** `static/tutorials/08_mo-phong-hien-tuong.mp4`

1. **Chuẩn bị nội dung:** Nhập hiện tượng, điều kiện, diễn biến và kết luận khoa học có căn cứ.
2. **Tạo và kiểm tra sản phẩm:** Chọn Mô phỏng hiện tượng, phong cách Khoa học – mô phỏng; kiểm tra màu, chất, động tác.
3. **Sử dụng trong tiết học:** Phát chậm hoặc theo cảnh; yêu cầu học sinh mô tả quan sát rồi giải thích.
**Lưu ý:** Mô phỏng phải đúng khoa học; không dùng AI thay thế hướng dẫn an toàn thí nghiệm.

### Câu hỏi khám phá
**Mục tiêu:** Mở đầu chu trình tìm tòi và dự đoán

**Video hướng dẫn:** `static/tutorials/09_cau-hoi-kham-pha.mp4`

1. **Chuẩn bị nội dung:** Nhập câu hỏi mở, dữ kiện và những giả thuyết học sinh có thể nêu.
2. **Tạo và kiểm tra sản phẩm:** Chọn Câu hỏi khám phá; kiểm tra video đưa đủ dữ kiện nhưng không làm lộ đáp án.
3. **Sử dụng trong tiết học:** Phát video và dừng ở câu hỏi; cho học sinh ghi dự đoán, chia sẻ chứng cứ.
**Lưu ý:** Ưu tiên câu hỏi có thể giải thích bằng kiến thức của lớp đã chọn.

### Luyện tập
**Mục tiêu:** Giúp học sinh áp dụng kiến thức vừa học

**Video hướng dẫn:** `static/tutorials/10_luyen-tap.mp4`

1. **Chuẩn bị nội dung:** Nhập câu hỏi, yêu cầu thao tác và đáp án kèm giải thích để giáo viên kiểm duyệt.
2. **Tạo và kiểm tra sản phẩm:** Chọn Luyện tập; để khoảng dừng hợp lý sau khi nêu đề; kiểm tra kết quả.
3. **Sử dụng trong tiết học:** Phát câu hỏi, tạm dừng cho học sinh làm rồi mới hiện phần giải thích.
**Lưu ý:** Không hiển thị đáp án quá sớm; đáp án cần được giáo viên kiểm tra.

### Vận dụng
**Mục tiêu:** Kết nối kiến thức với tình huống thực tiễn

**Video hướng dẫn:** `static/tutorials/11_van-dung.mp4`

1. **Chuẩn bị nội dung:** Nhập một nhiệm vụ thực tiễn, dữ liệu liên quan và yêu cầu giải quyết.
2. **Tạo và kiểm tra sản phẩm:** Chọn Vận dụng; dùng 24–64 giây và kiểm tra tính hợp lý của dữ kiện.
3. **Sử dụng trong tiết học:** Phát tình huống; giao học sinh thảo luận phương án và giải thích lựa chọn.
**Lưu ý:** Gắn thực tế, tránh tự bịa dữ kiện sản xuất hoặc kết quả nghiên cứu.

### Tổng kết bài học
**Mục tiêu:** Hệ thống hóa kiến thức cuối tiết

**Video hướng dẫn:** `static/tutorials/12_tong-ket-bai-hoc.mp4`

1. **Chuẩn bị nội dung:** Nhập các kiến thức trọng tâm, liên hệ và một câu hỏi tự kiểm tra.
2. **Tạo và kiểm tra sản phẩm:** Chọn Tổng kết bài học; dùng 16–40 giây, trình bày 2–4 ý chính.
3. **Sử dụng trong tiết học:** Phát cuối tiết; học sinh tự nhắc lại 3 ý và ghi điều còn thắc mắc.
**Lưu ý:** Ngắn, chính xác, ưu tiên liên kết giữa các khái niệm.

## III. Hướng dẫn theo từng giai đoạn sản xuất (8 bước)

### Phân tích bài học
**Video:** `static/tutorials/13_phan-tich-bai-hoc.mp4`

1. Mở Sản xuất sau khi nhấn Tạo video; xem tiến trình Phân tích bài học.
2. Đọc mục tiêu, kiến thức trọng tâm và cảnh báo; đối chiếu với tài liệu gốc.
3. Nếu có lỗi kiến thức, sửa nội dung đầu vào rồi chạy lại phần phụ thuộc.
**Lưu ý:** Không tiếp tục biên kịch nếu đầu vào chưa được xác thực.

### Tạo kịch bản
**Video:** `static/tutorials/14_tao-kich-ban.mp4`

1. Mở Sản xuất → Kịch bản tổng thể sau khi phân tích hoàn thành.
2. Kiểm tra mở đầu, diễn biến, kết thúc; lời thoại đúng chuyên môn và thời lượng.
3. Nếu kịch bản chưa đạt, chỉnh nguồn hoặc kịch bản rồi tạo lại phần bị ảnh hưởng.
**Lưu ý:** Không sửa sai kịch bản bằng cách sửa riêng prompt video.

### Chia cảnh
**Video:** `static/tutorials/15_chia-canh.mp4`

1. Xem số cảnh bằng thời lượng tổng chia 8 giây; xem mục tiêu mỗi cảnh.
2. Đối chiếu Character Bible, Environment Bible, Start State và End State.
3. Chỉ chấp nhận dữ liệu khi cảnh tiếp theo nối logic và nhân vật không đổi.
**Lưu ý:** Thay đổi Bible cần kiểm tra lại các cảnh đang sử dụng.

### Tạo câu lệnh
**Video:** `static/tutorials/16_tao-cau-lenh.mp4`

1. Mở Các cảnh; xem Image Prompt và Video Prompt của từng cảnh.
2. Đối chiếu cảnh, nhân vật, đạo cụ, bối cảnh, lời thoại và góc máy.
3. Nếu sửa prompt, lưu lại; tạo lại chỉ những tài nguyên phụ thuộc của cảnh đó.
**Lưu ý:** Không để lời thoại hoặc ảnh tham chiếu thuộc Scene khác.

### Tạo hình ảnh
**Video:** `static/tutorials/17_tao-hinh-anh.mp4`

1. Trong Các cảnh, xem ảnh do Nano Banana tạo sau khi có prompt hợp lệ.
2. Kiểm tra 16:9, nhân vật, trang phục, phông nền và tính khoa học.
3. Nếu ảnh sai, chọn Tạo lại hình ảnh riêng cảnh; chấp nhận ảnh đúng.
**Lưu ý:** Tạo lại ảnh có thể làm video cũ của cảnh hết hiệu lực.

### Tạo video
**Video:** `static/tutorials/18_tao-video.mp4`

1. Mở Các cảnh, theo dõi trạng thái tạo video của từng Scene ID.
2. Xem clip, kiểm tra hành động, âm thanh, lời thoại, điểm đầu và cuối.
3. Chọn Tạo lại video nếu chưa đạt; nhấn Chấp nhận cảnh khi clip đã hợp lệ.
**Lưu ý:** Không chấp nhận clip chỉ vì đã có mã tác vụ render.

### Ghép video
**Video:** `static/tutorials/19_ghep-video.mp4`

1. Kiểm tra tất cả cảnh đã có clip hợp lệ và được chấp nhận.
2. Nhấn Ghép video → Xuất MP4; theo dõi trạng thái ghép và âm thanh.
3. Nếu ghép lỗi, thử lại bước ghép từ clip đã có, không tạo lại toàn bộ cảnh.
**Lưu ý:** Nút ghép phải khóa khi thiếu dù chỉ một cảnh được chấp nhận.

### Hoàn thành
**Video:** `static/tutorials/20_hoan-thanh.mp4`

1. Mở Video cuối sau khi xuất MP4 thành công.
2. Phát thử, kiểm tra tiếng, hình, phụ đề tùy chọn và thời lượng.
3. Nhấn Tải MP4; lưu vào giáo án, trình chiếu hoặc kho học liệu của trường.
**Lưu ý:** Nếu sửa một cảnh, giữ lại bản MP4 cũ trong lịch sử phiên bản.

## IV. Kiểm tra và xử lý sự cố

- Nếu video hướng dẫn không phát: kiểm tra tệp `static/tutorials/*.mp4` có còn nằm đúng thư mục và không đổi tên. Mở trang trong thư mục giải nén đầy đủ, không chỉ sao chép riêng `index.html`.
- Nếu không thể tạo video bài giảng: kiểm tra backend, quyền truy cập AI và cấu hình an toàn; 21 video hướng dẫn không phụ thuộc các dịch vụ AI.
- Nếu một cảnh video bài giảng lỗi: vào **Các cảnh**, sửa đúng cảnh, nhấn **Tạo lại ảnh** hoặc **Tạo lại video** và kiểm duyệt lại cảnh đó.
- Nếu nút Ghép video chưa mở: tất cả cảnh phải có video hợp lệ và được chấp nhận.
- Việc sử dụng sản phẩm trong lớp học phải tuân thủ kiểm tra chuyên môn của giáo viên; nội dung AI không thay thế kiểm định kiến thức.
