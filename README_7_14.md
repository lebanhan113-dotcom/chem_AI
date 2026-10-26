# EDUPlan AI 7.14 – Cập nhật ngân hàng câu hỏi có kiểm duyệt

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất  
**Phạm vi:** Hóa học 10, 11, 12 – bộ sách Kết nối tri thức với cuộc sống – Chương trình GDPT 2018.

## 1. Những gì đã bổ sung

- Giữ **322 câu học sinh** đã có ở phiên bản 7.13, **21 chương / 78 bài** KNTT, 57 chuyên đề lỗi sai, 99 sơ đồ tư duy và các chức năng tự luyện, phiếu, tạo đề, Form 2025, xuất DOCX cũ.
- Trên trang chủ có thẻ riêng **Cập nhật nguồn ngân hàng câu hỏi – DOCX/CSV/JSON**, và thẻ **Ngân hàng đang sử dụng**. Các chức năng khác và 21 chương tiếp tục hiển thị trực tiếp.
- Công cụ dành cho giáo viên: `teacher-tools/index.html`. Đọc tệp `.docx`, `.csv`, `.json`; đề xuất chương theo tên tệp dạng `11.2`/`12.5`, cho lọc khối/phần, chỉnh chương–bài–mức độ, phương án và khóa, xem lỗi, xác nhận kiểm duyệt và xuất JSON dự phòng.
- Tệp DOCX được trích xuất **văn bản**, không thể khôi phục mọi Equation/MathType/OLE, sơ đồ hay hình. Những câu phụ thuộc các đối tượng này phải được giáo viên nhập lại dữ kiện trước khi duyệt. Không dùng OCR, không suy đoán khóa.
- Supabase lưu câu đã duyệt riêng với trường `content` công khai và `answer`, `explanation` trên máy chủ. Các phần luyện tập, kiểm tra, phiếu, ngân hàng và Form 2025 đọc thêm các câu mới sau khi website tải lại, **không nhân bản ngân hàng riêng cho từng tính năng**.
- Máy chủ chặn người không có khóa quản trị, chặn câu thiếu trường/khóa/lời giải/chưa xác nhận; không ghi đè câu cũ, không gửi đáp án trong API đọc công khai. API chấm câu mới tra khóa ở phía máy chủ **sau khi học sinh nộp**.

## 2. Thực hiện từng bước trên máy giáo viên

1. Mở WebApp trên Vercel → thẻ **Cập nhật nguồn ngân hàng câu hỏi** → **Mở công cụ cập nhật nguồn câu hỏi**.
2. Bấm **Chọn tệp**, có thể chọn nhiều tệp `.docx`, `.csv`, `.json` (tối đa 18 MB/tệp, 2.000 câu/tệp). Nếu nguồn DOCX được đặt tên `2026 - 2027. 11.2 ...docx`, hệ thống gợi ý Hóa 11, Chương 2; cần kiểm tra lại theo SGK.
3. Bộ lọc **Khối / Phần / Tìm kiếm** giúp chọn câu cần sửa. Bấm từng câu, xem tên bài, mức độ, dạng, nội dung, bốn phương án hoặc bốn ý Đ/S, lời giải và nguồn.
4. Đối chiếu với Word gốc, **sửa thủ công** mọi công thức/chỉ số/điều kiện/hình bị thiếu. Nếu đã nhập lại được đầy đủ dữ kiện MathType/hình, đánh dấu tùy chọn đã khôi phục đầy đủ; nếu chưa làm được thì để câu chờ duyệt.
5. Điền **đáp án và lời giải** đã kiểm chứng, sau đó tích chọn **Tôi đã đối chiếu...** và bấm **Lưu câu đã chỉnh sửa**. Câu trùng hoặc thiếu trường tiếp tục báo cảnh báo.
6. Bấm **Tải JSON chờ thẩm định** để sao lưu riêng tư. Tệp này có thể chứa khóa đáp án, **không đăng lên GitHub Pages công khai**.
7. Khi Supabase + Vercel đã cấu hình, nhập khóa quản trị máy chủ (không được lưu trong mã nguồn) rồi chọn **Đồng bộ**. Máy chủ chỉ nhận những câu đạt kiểm tra dữ liệu; thầy chịu trách nhiệm xác nhận tính chính xác khoa học.
8. Tải lại trang học sinh → **Kho câu hỏi / Luyện từng câu / Bài tập tương tác / Kiểm tra / Tạo đề / Phiếu học tập / Form 2025** → chọn khối–chương–bài–phần để sử dụng câu đã công bố. Chức năng trả đáp án đúng phụ thuộc máy chủ chấm.

## 3. Triển khai online – không cần GEMINI_API_KEY

1. Tạo **repository GitHub PRIVATE**, đưa toàn bộ thư mục WebApp, có `index.html` ở gốc. Không tải các ZIP chứa nguồn chờ thẩm định vào repository dùng để xuất bản.
2. Nhập repo vào **Vercel** (Node.js Serverless Functions tại `api/*.js`).
3. Tạo dự án Supabase. Mở **SQL Editor**, chạy `sql/supabase_question_additions.sql` (lệnh tạo bảng không xóa bảng cũ). Giữ Supabase RLS bật và không cho phép `anon` đọc khóa.
4. Vào **Vercel → Project Settings → Environment Variables** và thêm ba biến **chỉ phía máy chủ**:
   - `SUPABASE_URL` = URL project Supabase.
   - `SUPABASE_SERVICE_ROLE_KEY` = khóa service role Supabase **bí mật** (không đặt trong JavaScript phía trình duyệt, không dùng tên biến NEXT_PUBLIC_).
   - `EDUPLAN_ADMIN_TOKEN` = chuỗi bí mật ngẫu nhiên ít nhất 20 ký tự, nên từ 32 ký tự trở lên; chỉ giáo viên quản trị biết.
5. Redeploy Vercel. Kiểm tra trang chủ, `GET /api/public-bank?offset=0` (chỉ có `content`, không đáp án), `POST /api/admin-bank` phải trả **401** nếu thiếu mã quản trị; sau đó thử nhập một câu đã kiểm tra và chấm qua `POST /api/grade`.
6. **Không cần nhập GEMINI_API_KEY.** Lọc bài, nhập câu, lựa chọn, lưu, chấm tự động cho khóa đã duyệt không phụ thuộc Gemini. Chức năng AI tạo thêm lời giải/câu hỏi tự động không được kích hoạt khi chưa có dịch vụ AI phù hợp.

## 4. Quy tắc an toàn và giới hạn

- **Không tự duyệt**: DOCX nhập thành bản nháp; câu trùng, thiếu A–D, thiếu ý Đ/S, thiếu nguồn, thiếu khóa hoặc lời giải sẽ bị chặn. Chỉ chuyên môn giáo viên có thể xác định một lời giải là chính xác về khoa học.
- Không tự sửa công thức khó nhận diện; đặc biệt công thức, ảnh, bảng/MathType phải đọc lại Word nguồn. Với DOCX chỉ có thể khôi phục **văn bản** và giữ cảnh báo cho đối tượng bị mất.
- Bản nháp trước khi gửi được lưu trong `localStorage` **chỉ trên thiết bị giáo viên**, không đồng bộ. Hãy xuất JSON dự phòng thường xuyên và không dùng tài khoản quản trị trên máy công cộng.
- Không có Supabase hay biến môi trường ở Vercel, trang học sinh vẫn dùng **322 câu gốc**, công cụ nhập chỉ lưu nháp và xuất JSON, **không thể tự cập nhật ngân hàng cho các máy khác**.
- Cơ chế mã quản trị là bí mật chung của công cụ quản trị, **chưa có hệ thống vai trò và nhật ký thay đổi theo từng giáo viên**. Việc chấm sau nộp hiện dùng để tự luyện, **không có giám sát thi, chống gian lận hoặc lưu kết quả toàn trường**.
- `teacher-tools/index.html` có thể mở ở URL nhưng không thể ghi vào cơ sở dữ liệu nếu thiếu token. Không công bố hoặc chia sẻ mã quản trị.
- Giao diện đã kiểm tra qua nạp HTML/CSS/JS vào Chromium ở độ rộng 1440 px và 390 px; môi trường hiện chặn điều hướng `localhost`, **chưa nghiệm thu từ URL Vercel thật**. Cơ sở dữ liệu và API đã thử bằng mô phỏng, chưa bằng tài khoản Supabase của trường.

## 5. Kiểm thử

Các lệnh:

```bash
node tests/test_chem.js
node tests/test_grade77.cjs
node tests/test_713.cjs
node tests/test_714.cjs
node tests/test_714_mock.cjs
```

- Bản WebApp 7.13 nguyên gốc giữ 322 câu và không chứa khóa đáp án trong `data/hoa10.json` đến `hoa12.json`.
- Kiểm tra server: từ chối không có quyền, không trả khóa ở GET, chặn câu thiếu dữ liệu, bỏ qua câu trùng và chấm sau khi nộp bằng khóa máy chủ.
- Trình duyệt Chromium nạp 322 câu, hiển thị 21 chương và các thẻ chức năng; thử nhập một DOCX Hóa 11 nguồn có **21 câu** vào khu vực chờ, không tự phê duyệt; màn hình không tràn ngang trong phép thử.
- Các bài kiểm thử lịch sử mang chỉ tiêu 217 câu của phiên bản 7.11 và 7.12 được đặt trong `tests/historical/`, không sử dụng làm nghiệm thu hiện tại.
