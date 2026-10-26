# EduPlan AI 7.9 – Hóa học THPT KNTT, luyện tập và Form 2025

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Mục đích

Học sinh học kiến thức, làm trực tiếp câu hỏi theo khối/chương/bài, luyện theo nhóm 5/10/15, làm bài kiểm tra và xem lại **nguyên câu hỏi, các phương án/4 ý Đúng-Sai, bài làm và đáp án/lời giải đã kiểm chứng sau nộp**. Ngân hàng chung gồm 1.958 câu gốc Hóa 10–12 (21 chương, 78 bài), 57 chuyên đề lỗi sai, 99 sơ đồ tư duy.

## Cách triển khai (một bộ WebApp)

**Dùng Vercel + GitHub repository PRIVATE**, vì `api/grade.js` chứa 377 khóa đáp án đã được gắn cờ đối chiếu trong phiên bản trước. Không đăng kho mã nguồn này công khai. Giải nén và tải tất cả tệp/thư mục lên repo riêng tư; giữ `index.html`, `vercel.json`, `api`, `js`, `css`, `data`, `assets` và `references` đúng cấu trúc. Trên Vercel nhập dự án Git, loại Other/No framework khi được hỏi; không cần `GEMINI_API_KEY`. Xác minh tại URL HTTPS của chính dự án sau khi triển khai. `index.html` **không chạy riêng lẻ nếu không có thư mục dữ liệu và JavaScript**.

**Không dùng GitHub Pages công khai cho nguyên bộ ZIP này**: máy chủ chấm điểm là API Vercel và mã chứa khóa đáp án phải nằm trong repo riêng tư. Nếu tự lưu gói tĩnh không có API, học sinh vẫn làm bài và xuất DOCX nhưng **không có đáp án đã kiểm chứng sau nộp**.

## Form 2025

- **Chính thức môn Hóa học từ năm 2025**: Phần I – 18 câu nhiều phương án, Phần II – 4 câu đúng/sai mỗi câu bốn ý a,b,c,d, Phần III – 6 câu trả lời ngắn. Thời gian 50 phút. Căn cứ: Quyết định 764/QĐ-BGDĐT ngày 08/03/2024 và thông tin Bộ GD&ĐT.
- **Mở rộng dành cho trường**: thêm 4 câu tự luận; đây **không phải cấu trúc thi tốt nghiệp chính thức**.
- Bộ lọc: lớp 10–12 → chương → bài. WebApp chỉ lấy đủ câu đúng dạng trong phạm vi; nếu thiếu thì thông báo rõ, không tự lấp bằng câu ngoài bài/chương.
- Câu Đúng/Sai được tách thành bốn ý để chọn riêng. Câu có dữ liệu gốc không đủ rõ bị loại khỏi bộ tạo đề chuẩn.
- **Bấm Nộp bài**: lưu bản ghi tại trình duyệt, gửi các lựa chọn lên `/api/grade`, xem lại *toàn bộ câu hỏi* và phương án. Máy chủ chỉ trả đáp án/lời giải có khóa được gắn cờ, những câu khác hiện `Chờ kiểm duyệt`.
- Tải Word thật `.docx` từ màn hình làm bài; sau nộp có thể tải bài làm và lời giải được cung cấp bởi máy chủ.

## Các phân hệ cũ tiếp tục dùng ngân hàng chung

Trang chủ → Chọn bài → Luyện 5/10/15 → Kiểm tra → Kết quả → Học liệu & công cụ; Sơ đồ tư duy, Sổ ôn lỗi sai, Kho câu hỏi, Bài tập tương tác và phiếu học tập vẫn giữ và có khung câu hỏi làm ngay. Sửa lỗi trọng yếu của 7.8: trùng tên `chem()` dẫn tới hiển thị *Công cụ Hóa học* thay cho câu hỏi. Bản 7.9 đổi tên giao diện công cụ thành `chemToolPage()` để `chem(text)` định dạng công thức và câu hỏi đúng chức năng.

## Điều kiện quan trọng về đáp án và độ tin cậy

Ngân hàng 1.958 câu không có nghĩa 1.958 câu đã có đáp án đúng và giải thích chính thức. Dữ liệu server hiện có **377 khóa gắn cờ đủ điều kiện từ các đợt rà soát cũ**: 345 trắc nghiệm nhiều phương án, 32 trả lời ngắn; **chưa có khóa Đúng/Sai bốn ý hoặc tự luận trong API**. Những khóa này **chưa được kiểm tra khoa học độc lập toàn bộ trong bản nâng cấp này**. Không dùng bộ đề tạo ngẫu nhiên để thi chính thức khi chưa có giáo viên thẩm định từng câu, đặc biệt câu MathType/OLE/hình còn thiếu công thức.

API chấm hiện mang tính **tự học**, chưa có phiên kiểm tra máy chủ, tài khoản xác thực, cơ chế chống gian lận hoặc chuẩn hóa điểm /10 theo toàn bộ thang phần I–III. Việc bấm Nộp bài không phải bảo mật thi chính thức: bất kỳ người dùng nào có thể gửi yêu cầu tới API khi website mở công khai. Nếu dùng làm kiểm tra chính thức, cần thêm xác thực, phát hành đề, thời hạn, kiểm soát công bố đáp án và lưu kết quả tập trung trong Supabase.

Hiện lịch sử học tập **chỉ lưu localStorage** trên từng thiết bị, chưa đồng bộ giữa các thiết bị và chưa có số lượt truy cập thật.

## Hướng dẫn sử dụng cho học sinh

1. Mở WebApp HTTPS → chọn **Form 2025**, chọn khối và phạm vi chương/bài.
2. Chọn Form chính thức hoặc mở rộng; xem bảng đếm số câu mỗi phần.
3. Bấm **Bắt đầu làm đề**; làm trực tiếp A–D, đủ bốn ý Đúng/Sai, nhập trả lời ngắn (và tự luận nếu chọn mở rộng).
4. Bấm **Nộp bài và xem lời giải**; xem lại nguyên nội dung từng câu. Câu đã kiểm chứng có đáp án và lời giải nguồn, câu chưa đủ điều kiện hiển thị `Chờ kiểm duyệt`.
5. Khi cần in/lưu, chọn **Tải bài làm và lời giải .docx**.
6. Các chức năng khác vẫn nằm trong **Luyện tập** và **Học liệu & công cụ**, có liên kết làm trực tiếp theo từng bài.

## Cấu trúc mã nguồn

- `index.html`: tệp khởi chạy, nhẹ, HTML/CSS/JS tách riêng.
- `js/app.js`: điều hướng, các chức năng gốc; đã khắc phục xung đột hàm hiển thị công thức.
- `js/integration78.js`: khung làm bài trong từng học liệu; trả lại nguyên đề khi xem đáp án.
- `js/form2025.js`: bộ tạo đề Form 2025, đủ ba phần hoặc mở rộng bốn phần, làm trực tiếp và xem đáp án sau nộp.
- `js/docx-export.js`: tải file Word `.docx` thực, phân phần I–IV và ghi lời giải theo phản hồi kiểm chứng.
- `css/form2025.css`: giao diện form trên PC và di động.
- `data/*`: 1.958 câu **không chứa khóa đáp án**, danh mục, sơ đồ và học liệu.
- `api/grade.js`: API Vercel có **377 khóa đáp án phía server**; không phân phối cho học sinh.
- `tests/`: kiểm thử dữ liệu/công thức và xử lý máy chủ.

## Phạm vi nghiệm thu

Đã kiểm tra tự động dữ liệu, mã nguồn, mô phỏng Chromium không có network localhost, bản Word và responsive 1400/390 px. **Chưa có kiểm thử thực tế trên tên miền Vercel của người dùng**, chưa nghiệm thu đa thiết bị/Supabase và chưa duyệt chuyên môn toàn bộ 1.958 câu.
