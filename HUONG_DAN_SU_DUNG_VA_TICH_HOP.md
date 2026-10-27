# EDUPlan AI 7.14 – HỆ THỐNG GIAO BÀI, KIỂM TRA, CHẤM ĐIỂM VÀ QUẢN LÝ HỌC TẬP

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất  
**Phiên bản:** Mã nguồn nâng cấp phục vụ Hóa học 10, 11, 12 – GDPT 2018 – Kết nối tri thức  
**Phạm vi:** WebApp độc lập triển khai trên máy giáo viên, không thay thế trực tiếp mã nguồn website EduPlan AI đang hoạt động trên Vercel/GitHub.

## 1. Trọng tâm và nhóm công việc

1. **Giảm thao tác thủ công:** Giáo viên tạo lớp, thêm học sinh, tạo khóa học, tạo/trộn đề và giao bài theo một quy trình.
2. **Kiểm tra thuận tiện:** Học sinh sử dụng mã truy cập riêng để nhận đề, làm bài và nộp bài trực tuyến; giáo viên in đề theo mã học sinh và chấm bài giấy bằng cách nhập lựa chọn.
3. **Ngân hàng câu hỏi:** Tích hợp 773 câu Đúng/Sai, phân loại theo khối/chương/bài/mức độ và năng lực HH1–HH3 (dữ liệu phân loại nguồn còn mang tính gợi ý); cập nhật DOCX/CSV/JSON, chống trùng và phân luồng độ tin cậy.
4. **Theo dõi tiến độ:** Lưu lớp, khóa học, bài giao, số lần hoàn thành và điểm số trong SQLite.
5. **Điều chỉnh dạy học:** Tổng hợp điểm trung bình, mức độ hoàn thành, câu thường sai và xuất điểm CSV.

## 2. Danh mục thanh công cụ

| Mục | Đối tượng | Nội dung |
|---|---|---|
| Tổng quan | Giáo viên + học sinh | Thống kê số câu, lối tắt các chức năng |
| Thi / Làm bài online | Học sinh | Đăng nhập mã học sinh, nhận đề, làm và nộp bài |
| Luyện theo bài | Học sinh | Luyện nhanh 5/10/15 câu theo phạm vi lớp/chương/bài |
| Ngân hàng câu hỏi | Giáo viên + học sinh | Tìm, lọc danh mục có chấm / nguồn chưa chấm |
| Tự luyện nguồn | Học sinh | Luyện những câu thiếu khóa, không tự gán đáp án |
| Ôn lỗi sai | Học sinh | Luyện lại các câu sai đã lưu trong trình duyệt |
| Tiến độ cá nhân | Học sinh | Các khóa học, bài giao, trạng thái và điểm |
| Lớp & học sinh | Giáo viên | Tạo lớp, nhập học sinh, cấp mã truy cập |
| Khóa học | Giáo viên | Tạo khóa ôn tập theo từng lớp |
| Tạo / Trộn đề | Giáo viên | Chọn lớp, chương, bài, mức độ, HH1/HH2/HH3, số câu, thời hạn |
| Giao bài | Giáo viên | Danh mục đề đã giao, số lượt đã nộp |
| Chấm phiếu giấy | Giáo viên | In đề riêng, in phiếu, nhập Đ/S để tự chấm và lưu điểm |
| Thống kê & phân tích | Giáo viên | Điểm, học sinh, câu thường sai, xuất CSV |
| Cập nhật ngân hàng | Giáo viên | Nhập DOCX, JSON, CSV và tự kiểm tra nguồn |
| Hướng dẫn | Tất cả | Quy trình của học sinh và giáo viên |

## 3. Khởi động trên Windows

1. Cài **Python 3.11 trở lên** và chọn **Add Python to PATH** khi cài đặt.
2. Giải nén toàn bộ ZIP vào thư mục riêng, tránh đặt trong thư mục công khai của website.
3. Chạy `CHAY_WEBAPP_WINDOWS.bat`. Lần đầu cần Internet để tải thư viện Python trong `requirements.txt`.
4. Truy cập `http://127.0.0.1:8765` trên cùng máy tính.
5. Mật khẩu quản trị được **sinh ngẫu nhiên** và hiện trong cửa sổ máy chủ, lưu tại `.teacher_password`; tài khoản giáo viên là `giaovien`.
6. Nếu nhập tài liệu Word DOCX, cần cài thêm LibreOffice hoặc thiết lập biến môi trường `SOFFICE_PATH` đến `soffice.exe`. CSV/JSON không yêu cầu LibreOffice.
7. Trên Mac/Linux: `sh CHAY_MAC_LINUX.sh`.

**Không cần nhập GEMINI_API_KEY.** WebApp có thể dùng trên máy giáo viên không cấu hình API AI. “Tự kiểm định” hiện là thuật toán kiểm tra dữ liệu nguồn, không phải dịch vụ AI chứng nhận độ chính xác tuyệt đối về nội dung Hóa học.

## 4. Quy trình giáo viên từ đầu đến cuối

1. Mở **Lớp & học sinh** → nhập mật khẩu → chọn **Tạo lớp**, ví dụ `11A1` khối 11.
2. Chọn lớp → nhập từng tên học sinh trên một dòng → nhấn **Tạo mã đăng nhập học sinh**. Gửi **mỗi mã riêng cho đúng học sinh**.
3. Vào **Khóa học**, chọn lớp, đặt tên khóa học ví dụ `Ôn tập giữa kì I`.
4. Vào **Tạo / Trộn đề**: chọn lớp, tên đề, hình thức `homework / quiz / exam / review`, khối, chương/bài, mức độ, năng lực, số câu 1–30, giới hạn phút và hạn nộp nếu cần. Khóa học là tùy chọn.
5. Nhấn **Tạo & giao đề**. Hệ thống chỉ chọn các câu có 4 khóa và lời giải nguồn đủ điều kiện; nếu phạm vi thiếu câu, ứng dụng yêu cầu giảm số câu hoặc mở rộng chương/bài.
6. Học sinh truy cập **Thi / Làm bài online**, nhập mã và chọn đề. Câu trong cùng một đề được **trộn thứ tự theo mã học sinh**; một học sinh chỉ được nộp một lần cho mỗi bài.
7. Khi nộp, máy chủ tính số ý đúng, điểm %, trả về **toàn bộ câu hỏi, từng đáp án học sinh chọn, đáp án nguồn, giải thích từng ý**. Kết quả được lưu trong SQLite.
8. Giáo viên vào **Thống kê & phân tích** để xem tiến độ, điểm trung bình, những câu thường sai; tải CSV điểm lớp.

## 5. Tổ chức kiểm tra trên giấy

- Vào **Chấm phiếu giấy** → chọn **đề đã giao** và **học sinh**.
- Nhấn **In đề theo mã học sinh** để in nguyên văn bộ câu hỏi trộn đúng cho em đó. Có thể in **phiếu Đúng/Sai** trắng theo số câu.
- Sau khi học sinh nộp phiếu, chọn **Nhập đáp án giấy / Xem thứ tự câu**, nhập bốn ý Đ/S từng câu rồi chọn **Chấm & lưu điểm**.
- Điểm giấy được đưa vào cùng bảng thống kê với bài nộp online.
- **Bản này KHÔNG hỗ trợ tự nhận dạng phiếu tô OMR/OCR từ ảnh máy ảnh hoặc máy quét.** Chức năng đã làm là chấm tự động dựa trên đáp án giáo viên nhập từ phiếu giấy.

## 6. Cập nhật ngân hàng và độ tin cậy

- Ngân hàng tích hợp **773 câu Đúng/Sai không trùng**: **112 câu có khóa nguồn đủ điều kiện chấm**, **661 câu nguồn chưa đủ điều kiện chấm**, vẫn dùng để học sinh tự rèn luyện.
- Câu mới được lọc nội dung trùng, gán chương/bài/khối gợi ý, kiểm tra 4 mệnh đề, 4 khóa, giải thích, tình trạng hình/công thức và cảnh báo nguồn.
- Câu thiếu hoặc có biểu hiện không nhất quán được **cách ly khỏi chế độ chấm**, không tự bịa khóa đáp án.
- Với dữ liệu nguồn có hình hoặc MathType/OLE, cần đối chiếu trước khi sử dụng trong bài kiểm tra chính thức.
- Chỉ **2 câu Hóa 12** hiện có khóa nguồn vượt qua bộ tiêu chí rất chặt của bản trước; phần lớn câu Hóa 12 vẫn nằm ở kho tự luyện. Để tổ chức đề nhiều câu cho lớp 12 cần tiếp tục nạp nguồn có khóa, lời giải chuẩn, không lỗi hình/công thức.
- Lọc mức độ/năng lực đang dựa trên trường `levelSuggested` và `competencySuggested` của nguồn, chưa phải phân loại đã kiểm chứng hoàn toàn bằng chuyên gia.

## 7. Tệp quan trọng cần giữ khi cập nhật

- `questions_private.json` – Ngân hàng câu hỏi và khóa đáp án, **chỉ lưu riêng ở máy chủ giáo viên**.
- `media/` – Hình, sơ đồ, biểu đồ, công thức ảnh từ nguồn.
- `source_import_history.json` – Lịch sử nhận diện tệp đã nhập (chống nhân bản khi nạp lại).
- `edup_education.sqlite3` – Dữ liệu lớp, học sinh, khóa học, bài giao, điểm và tiến độ (tự tạo ở lần chạy đầu).
- `.teacher_password` – Mật khẩu giáo viên (tự tạo lần đầu, phải sao lưu riêng tư).

**Sao lưu ít nhất hằng tuần** cả 5 mục trên (trong đó `media/` là thư mục). Khi nâng cấp từ bản cũ bằng gói vá, chỉ thay mã nguồn được chỉ rõ, không xóa/ghi đè dữ liệu.

## 8. Lưu ý bảo mật và triển khai chính thức

- Bản chạy mặc định ở `127.0.0.1`, chỉ truy cập trên cùng máy; **chưa triển khai lên Vercel, Supabase hoặc repository EduPlan AI chính thức**.
- Khóa đáp án trong `questions_private.json` và API giáo viên không được đưa vào thư mục public hoặc JavaScript phía học sinh.
- Mã truy cập học sinh của bản mẫu có tính xác thực đơn giản để thử nghiệm nội bộ; **chưa có tài khoản chuẩn SSO, TLS/HTTPS, phân quyền nhiều trường, nhật ký audit và chống dò mật khẩu ở mức sản xuất**. Không đưa dữ liệu thật của học sinh lên Internet trước khi bổ sung những yêu cầu này và có quy trình bảo vệ dữ liệu cá nhân.
- Bản cập nhật **không tự chứng nhận độ chính xác khoa học** của mọi đáp án, đặc biệt với câu thiếu hình/công thức và tài liệu chưa có khóa.

## 9. Kiểm thử đã thực hiện

- API: 773 câu được giữ, không xuất khóa trước khi nộp, tạo lớp/học sinh/khóa học/đề, nộp bài một lần, xem lại kết quả, in đề theo học sinh, chấm phiếu giấy bằng đáp án nhập, phân tích và xuất CSV.
- Giao diện: Kiểm tra trong Chromium bằng nguồn HTML và API giả lập cục bộ, chức năng đăng nhập, chuyển màn hình, tạo đề, mở bài, chọn và nộp đáp án, hiện lời giải; màn hình 1440 px và 390 px không tràn ngang, không xuất hiện lỗi JavaScript trong các luồng đã kiểm thử.

---

Tác giả giải pháp: **Lê Bá Nhẫn – Trường THPT Hòn Đất**.
