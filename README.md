# CHEM-MAP TUTOR AI V4.1 – Bản chạy & kiến trúc tiến tới sản phẩm thật

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Ba cách sử dụng

1. **Mở chạy ngay, không cần cài:** tải `CHEM_MAP_TUTOR_AI_V4_1_CHAY_NGAY.html` và mở bằng Chrome hoặc Edge; CSS, JS, ngân hàng câu hỏi đã gói trong 1 file. Dữ liệu chỉ nằm trên trình duyệt, góc giáo viên chưa xác thực. Không dùng dữ liệu HS thật.
2. **Website tĩnh Vercel:** giải nén `CHEM_MAP_TUTOR_AI_V4_1_VERCEL_STATIC.zip`, đưa các tệp ở thư mục gốc lên GitHub, vào `vercel.com/new` → Import → Framework Other → Deploy. Website này **là demo tĩnh**, không đồng bộ tài khoản, không có backend và đáp án có thể xem trong source trình duyệt.
3. **Máy chủ thử nghiệm có tài khoản:** giải nén `CHEM_MAP_TUTOR_AI_V4_1_FULLSTACK_SOURCE.zip`, làm theo `server/START_HERE.md`. Tải trang từ `http://127.0.0.1:8080/`, có login, dữ liệu SQLite, ngân hàng câu hỏi ở máy chủ, chấm trên server và phân quyền cơ bản. Chưa phù hợp đưa internet công khai.

## Kết quả V4.1

- Nguồn tham khảo: OpenStax Chemistry 2e, PhET Chemistry, ChemCollective Virtual Labs, Royal Society of Chemistry. Tất cả 122 câu bổ sung là **độc lập tự biên soạn**, không sao chép các đề ngoài, metadata liên kết tham khảo. Không sử dụng mô phỏng/ảnh nguồn khi chưa rõ giấy phép.
- 672 câu từ V3 + 122 câu mới = **794 bản ghi**; 72 bài, mỗi bài ít nhất 6 câu; gồm câu gốc và biến thể tham số. Không đánh đồng số bản ghi với số dạng bài độc lập.
- 72 MCQ mới, 20 đúng/sai, 20 trả lời ngắn và 10 tự luận, mức độ NB/TH/VD/VDC và HH1–HH3. File `new_questions_review.csv` giúp tổ chuyên môn thẩm định.
- Offline WebApp: luyện 5/10/15 câu khi đủ số lượng, làm bài Form 2025, xem lời giải, phân loại lỗi sai, bản đồ năng lực, lịch sử, import CSV/JSON, luyện lại cùng câu và thử **luyện câu khác** trong cùng bài/ năng lực (không mặc nhiên là tương đương độ khó).
- Server pilot: xác thực phiên bằng HttpOnly cookie, role đơn giản, chấm server-side, không gửi đáp án trước nộp, lưu kết quả SQLite, giáo viên duyệt câu & tạo user demo; đã kiểm thử HTTP chức năng.

## Chất lượng và giới hạn

Các câu mới ở trạng thái `sample` / `reviewStatus=pending_teacher`; chưa có biên bản thẩm định hai giáo viên. Đơn vị, giá trị, lời giải tính toán được kiểm tra mã hóa nhưng phải rà lại từng câu, nhất là câu vận dụng cao. Các câu tự luận **không tự cho điểm**. Các bài 10–15 câu cần ngân hàng đủ lớn theo từng bộ lọc; phải báo thiếu nếu không đủ.

Trình duyệt tự động tại môi trường tạo dự án báo chặn truy cập file / localhost; bộ kiểm thử Node, HTTP API, schema và giao diện tĩnh đã được kiểm tra qua mã. Cần mở kiểm thử trực tiếp bằng Chrome/Edge trên thiết bị trường trước khi dùng thật.

## Bước tiếp theo có thể triển khai

1. Kiểm duyệt 794 bản ghi và bổ sung độc lập theo 4 dạng, mục tiêu ≥15 câu phù hợp ở từng bài, mỗi mức HH2/HH3 có minh chứng đánh giá.
2. Đưa **demo tĩnh** lên Vercel để kiểm tra giao diện/khả năng truy cập công khai (không nhập thông tin học sinh thật).
3. Nâng máy chủ thử nghiệm từ SQLite sang PostgreSQL/Supabase + Auth, phân quyền theo trường/lớp và kiểm soát đáp án server-side, audit/backup.
4. Tích hợp giao bài – chấm tự luận qua giáo viên – báo cáo tiến bộ theo bài và năng lực; thí điểm dùng dữ liệu mã hóa/ẩn danh, có phê duyệt nhà trường.
5. Kiểm tra hiệu quả pre-test/post-test với đề tương đương đã hiệu chỉnh độ khó; lập minh chứng 5 tiêu chí và hồ sơ giải pháp.

## Nguồn chủ đề nghiên cứu

- https://openstax.org/books/chemistry-2e/pages/12-1-chemical-reaction-rates
- https://openstax.org/books/chemistry-2e/pages/14-1-bronsted-lowry-acids-and-bases
- https://chemcollective.org/vlabs
- https://phet.colorado.edu/en/simulations/browse?subjects=chemistry
- https://edu.rsc.org/resources/practical/experiments

Sử dụng đường liên kết nguồn để đối chiếu khái niệm; kiểm tra giấy phép trước khi tái phân phối nội dung của bên thứ ba.
