# EDUPLAN AI 7.5 – SƠ ĐỒ TƯ DUY 21 CHƯƠNG, 78 BÀI KNTT

**Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất**

## Chức năng mới

- Thêm thanh công cụ **Sơ đồ tư duy KNTT** giữa Chương & bài và Kho câu hỏi.
- Hiển thị **sơ đồ tổng quan từng chương** và **sơ đồ chi tiết từng bài** Hóa 10–12.
- Mỗi bài có 4 nhánh nội dung/ghi nhớ, chọn nhánh để mở mô tả bên dưới.
- Từ sơ đồ chương nhấn từng nhánh → chọn **Xem sơ đồ bài**.
- Từ sơ đồ bài bấm **Luyện bài đang học**, **Ôn lỗi sai**.
- Thu/phóng sơ đồ bằng nút **+/−**, kéo ngang trên điện thoại.
- Tải sơ đồ ra **Word DOCX** có ảnh nhúng và ghi chú, hoặc lưu **PNG/SVG**.
- Sơ đồ chỉ tóm tắt nội dung, không thay thế SGK. Các công thức/điều kiện cần đối chiếu trước khi sử dụng chính thức.

## Hướng dẫn từng bước

1. Chọn **Sơ đồ tư duy KNTT** trên thanh công cụ.
2. Chọn **Hóa 10/11/12 → chương** cần học.
3. Chọn **Sơ đồ toàn chương** để xem các bài liên hệ với nhau.
4. Nhấn nhánh của bài → **Xem sơ đồ Bài…** để mở bản chi tiết.
5. Trong **Sơ đồ từng bài**, chọn nhánh kiến thức để xem ý chính và ghi nhớ.
6. Bấm **Luyện bài đang học / Ôn lỗi sai** để thực hành trực tiếp từ ngân hàng 1.958 câu và 57 chuyên đề lỗi sai.
7. Nếu muốn lưu, bấm **Tải sơ đồ Word .docx**, **Tải ảnh PNG** hoặc **Tải sơ đồ SVG**.

## Triển khai GitHub Pages / Vercel

- Giải nén ZIP và tải toàn bộ nội dung thư mục lên repository, **index.html phải ở thư mục gốc**.
- Bắt buộc giữ các thư mục `css/`, `js/`, `data/`, `assets/`, `references/`.
- GitHub Pages: Settings → Pages → Deploy from a branch → main / (root).
- Vercel: nhập repository và chọn **Other / Static Site**; không cần bước build cho website tĩnh.
- **Không cần GEMINI_API_KEY** để tải dữ liệu, xem sơ đồ, tự luyện hoặc xuất Word.
- Khi thử trên máy, chạy `python -m http.server 8000` ở thư mục gốc và mở `http://localhost:8000`. Mở đơn lẻ `index.html` theo `file://` có thể bị CORS chặn tải JSON.

## Nguồn nội dung

Danh mục chương/bài giữ nguyên từ bộ dữ liệu KNTT đã tích hợp. Các nhánh là nội dung hệ thống hóa kiến thức Hóa học theo bài, không lấy đáp án từ dữ liệu ngân hàng. Cần rà soát chuyên môn khi dùng cho kiểm tra chính thức.


---

# EDUPLAN AI 7.4 – SỔ ÔN LỖI SAI THƯỜNG GẶP & WEBAPP HÓA HỌC THPT

**Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất**

## NÂNG CẤP 7.4 – HƯỚNG DẪN 14 THANH CÔNG CỤ

- Bổ sung khung **Hướng dẫn từng bước** ngay dưới tiêu đề của từng trang chức năng (14/14 mục menu).
- Khung tự mở lần đầu, nhấn tiêu đề để **thu gọn/mở lại**; lựa chọn được giữ tại `localStorage` theo từng thanh công cụ.
- Mỗi trang có từ 5–7 bước cụ thể, bao gồm đường đi chọn khối/chương/bài, trả lời trực tiếp, lưu tiến độ, xuất DOCX khi có hỗ trợ và các lưu ý về bảo mật đáp án.
- Trên điện thoại khung hướng dẫn tự co giãn; các thao tác cũ tiếp tục dùng cùng dữ liệu ngân hàng.
- **Xem toàn bộ hướng dẫn** tại `HUONG_DAN_14_THANH_CONG_CU_7_4.md`.
- **Xem báo cáo kiểm thử** tại `BAO_CAO_KIEM_THU_7_4.md`.
- Không thay đổi file ngân hàng câu hỏi, mục lục, dữ liệu lỗi sai, hình ảnh hoặc tài liệu nguồn so với bản 7.3 (đã kiểm tra mã SHA-256).

## 1. Nội dung nâng cấp

Đây là bản nâng cấp **tiếp nối EduPlan AI 7.3 học sinh**. Tệp chạy chính **`index.html`** rất nhỏ, CSS trong `css/app.css`, code tương tác trong `js/app.js` và xuất Word trong `js/docx-export.js`.

- Giữ nguyên **1.958 câu hỏi nguồn**, không chỉnh sửa nội dung ngân hàng cũ (Hóa 10: 809; Hóa 11: 473; Hóa 12: 676).
- Giữ danh mục **21 chương – 78 bài KNTT Hóa học 10, 11, 12**.
- Bổ sung **57 chuyên đề lỗi sai** từ **11 tài liệu `.doc`** thầy đã cung cấp; lưu ở `data/error_notebook.json`, tham chiếu theo khối/chương/bài KNTT.
- Số chuyên đề liên kết theo khối: Hóa 10 có 18, Hóa 11 có 17, Hóa 12 có 32 **liên kết**; một chuyên đề có thể liên kết nhiều lớp/bài nên tổng liên kết khác 57.
- `references/` chứa **11 tài liệu nguồn được chuyển sang DOCX** để mở đối chiếu công thức, bảng và MathType/OLE.
- Thanh công cụ mới **Sổ ôn lỗi sai thường gặp**: chọn lớp → chương → bài → xem quy tắc, ví dụ, lời giải nguồn, phân tích lỗi sai và bài thử thách; đánh dấu **Đã hiểu/Cần ôn thêm**.
- Từ chuyên đề có nút **Luyện 5 câu theo bài** và **Làm bài tương tác**; khi đang luyện có nút trở lại **Ôn lỗi sai liên quan**.
- Xuất **Sổ ôn theo bài / đủ 57 chuyên đề** thành **`.docx` thực sự**, Times New Roman, không cần API key.
- Các tính năng 7.2 khác vẫn ở các mục cũ: luyện từng câu, nhóm 5/10/15, phiếu học tập, tạo đề/trộn đề, kết quả, công cụ Hóa học, gọi tên ngẫu nhiên, tài liệu, mở ChatGPT.

## 2. Cách chạy trên GitHub Pages hoặc Vercel

**GitHub Pages:** Giải nén ZIP, tải **toàn bộ nội dung trong thư mục** lên nhánh `main`, đảm bảo `index.html` ở thư mục gốc cùng `css/`, `js/`, `data/`, `assets/`, `references/`; vào **Settings → Pages → Deploy from a branch → main / (root)**. Sau khi GitHub xuất bản, mở đường dẫn Pages của repository.

**Vercel:** Tạo dự án từ GitHub, chọn dự án website tĩnh. `index.html` ở thư mục gốc; không cần lệnh build cho bản học sinh. Giữ `vercel.json`, `data/`, `assets/`, `references/`.

**Chạy trên máy tính để thử:** mở Terminal tại thư mục chứa `index.html`, chạy `python -m http.server 8000`, mở `http://localhost:8000` trên trình duyệt. Mở tệp `index.html` trực tiếp bằng `file://` có thể lỗi nạp JSON do chính sách trình duyệt; nên dùng server HTTP.

## 3. Hướng dẫn học sinh

1. Nhấn **Sổ ôn lỗi sai thường gặp** trong thanh menu.
2. Chọn **Hóa 10/11/12 → chương → bài** đúng theo SGK KNTT.
3. Bấm mở các phần **Nhận diện lỗi – Ví dụ – Hướng dẫn giải – Phân tích lỗi sai – Thử thách**.
4. Chọn **Cần ôn thêm** hoặc **Đã hiểu**. Trạng thái lưu **trên thiết bị này**.
5. Bấm **Luyện 5 câu theo bài** để chuyển sang màn hình trả lời từng câu ngay trên web.
6. Chọn tải **Word theo bài** hoặc **Word đủ 57 chuyên đề** khi cần tự học/in.
7. Với công thức hiển thị `[pic]`, mở **Tài liệu gốc** (DOCX) để xem ký hiệu MathType/OLE; không suy đoán nội dung thiếu.

## 4. Nguyên tắc chính xác và bảo mật

**Chuyên đề lỗi sai được trích từ tài liệu cũ, không đồng nghĩa đã được kiểm chứng từng phép tính.** Tên bài KNTT là ánh xạ theo chủ đề kiến thức, không phải số chương trùng khít với tài liệu lỗi sai. Một số công thức MathType/OLE chưa đọc được trong dữ liệu văn bản và cần xem bản Word gốc.

**Không tự tạo hay sửa đáp án ngân hàng cũ.** Bản học sinh chỉ chứa đề và câu trả lời đã lưu, không công bố khóa đề kiểm tra bí mật hoặc tự chấm điểm câu chưa được giáo viên thẩm định. Các ví dụ có lời giải trong Sổ là học liệu tham khảo, không dùng để chấm trực tiếp ngân hàng cũ.

Bản HTML tĩnh lưu lịch sử/đánh dấu ở **localStorage của trình duyệt trên từng thiết bị**, **không có tài khoản, chấm điểm chính thức, đồng bộ dữ liệu nhiều thiết bị hoặc báo cáo truy cập toàn hệ thống**. Các tính năng đó cần cơ sở dữ liệu và máy chủ có phân quyền; gói này **chưa triển khai lên tài khoản Vercel/GitHub của thầy**.

**Bản quyền:** 11 tài liệu Word gốc và các trích đoạn có thể có quyền tác giả. Chỉ đăng công khai khi thầy có quyền sử dụng/phân phối; nếu chưa, chỉ triển khai trong môi trường được phép hoặc gỡ `references/` và hạn chế hiển thị nội dung nguồn theo quyền sử dụng.

## 5. Các tệp quan trọng

- `index.html` – trang đầu WebApp, đặt ở gốc repository.
- `js/app.js` – 14+ thanh công cụ có Sổ ôn lỗi sai và liên kết luyện tập.
- `js/docx-export.js` – xuất DOCX câu hỏi/bài làm/sổ lỗi sai trên trình duyệt.
- `data/error_notebook.json` – 57 chuyên đề trích nguồn, liên kết lớp/chương/bài.
- `data/error_source_audit.json` – kiểm kê các file nguồn.
- `data/hoa10.json`, `hoa11.json`, `hoa12.json` – giữ nguyên 1.958 câu từ v7.2.
- `references/so_on_loi_nguon_00.docx` đến `10.docx` – bản DOCX tham khảo của các file cũ.
- `BAO_CAO_KIEM_THU_7_3.md` – kết quả và giới hạn kiểm thử.

*Ngày thực hiện: 25/10/2026.*
