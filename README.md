# EDU GAME STUDIO AI – WebApp tạo trò chơi giáo dục

**Tác giả giải pháp:** Giáo viên: Lê Bá Nhẫn – Trường THPT Hòn Đất (An Giang)  
**Phiên bản bản dựng:** 1.0 (bản WebApp hoạt động, AI có thể kết nối tùy chọn)

## 1. Cách sử dụng nhanh – không cần lập trình

**Cách A: Mở trực tiếp bằng Chrome/Edge.** Giải nén gói ZIP rồi nhấp đúp `index.html`. Ứng dụng có giao diện tiếng Việt, có thể mở bài học mẫu và tạo/tải trò chơi HTML. Trong cách này, chức năng phân tích **cục bộ** chỉ đọc những định dạng câu hỏi và quan hệ mà giáo viên cung cấp; **không** tự gọi Gemini. Khả năng lưu trữ khi mở file trực tiếp tùy chính sách bảo mật của trình duyệt. Nếu trình duyệt chặn lưu trữ, dùng Cách B và luôn xuất bản sao JSON.

**Cách B: Chạy qua server cục bộ (khuyến nghị để lưu dự án ổn định).** Cài Node.js 20 trở lên. Trong thư mục đã giải nén, chạy `node server.mjs` hoặc nhấp `START_WINDOWS.bat` trên Windows, rồi truy cập `http://localhost:3000` bằng Chrome/Edge. Không cần cài thêm thư viện npm. Dữ liệu lưu bằng IndexedDB tại trình duyệt, có thể xuất/nhập bản sao JSON ở mục **Cài đặt & sao lưu**.

**Cách C: Kích hoạt Gemini AI thật.** Trên Windows PowerShell, trong thư mục này chạy:

```powershell
$env:GEMINI_API_KEY="API_KEY_CUA_BAN"
node server.mjs
```

Trên macOS/Linux:

```bash
GEMINI_API_KEY="API_KEY_CUA_BAN" node server.mjs
```

Sau đó mở `http://localhost:3000`, vào **Biên soạn bài học** và chọn **Phân tích bằng Gemini**. Khóa API chỉ nằm ở biến môi trường của máy chủ. Không nhập khóa API vào tệp HTML game. Có thể đổi model qua `GEMINI_MODEL` (mặc định `gemini-2.5-flash`). Kết quả AI cần giáo viên duyệt, không nên coi là chính xác tuyệt đối.

## 2. Quy trình cho giáo viên

1. Chọn **Bài học của tôi** > **Tạo bài học**, nhập nội dung, tên, môn, lớp.
2. Hoặc chọn **Nạp bài học mẫu** để có sẵn ví dụ Hóa học 10 với câu hỏi và dữ liệu ghép/phân loại.
3. Chọn **Phân tích cục bộ** (không AI) hoặc **Phân tích bằng Gemini** (nếu đã cấu hình server), rồi kiểm tra ngân hàng kiến thức và nhiệm vụ.
4. Vào **Ngân hàng học tập** để bổ sung hoặc sửa câu hỏi, cặp ghép, phân loại; xem Activity Bank được dựng từ các ngân hàng.
5. Chọn **Thư viện 8 game**, chọn loại game và tạo một **Game Instance**.
6. Ở **Game Instance**, dùng các nút **Chơi**, **Sửa**, **Nhân bản**, **Xóa** và **Tải HTML**.
7. Mở tệp HTML đã tải bằng trình duyệt. Mỗi tệp chỉ có một trò chơi và không cần Gemini hoặc kết nối Internet để chơi.
8. Định kỳ vào **Cài đặt & sao lưu** để tải bản sao dự án dạng JSON.

## 3. Định dạng đầu vào cho chế độ phân tích cục bộ

Chế độ này không phải AI; nó chỉ đọc thông tin đã được giáo viên cung cấp có cấu trúc rõ ràng:

```text
Số hiệu nguyên tử Z bằng số proton trong hạt nhân.

Câu 1. Nguyên tử có Z = 17 thuộc nguyên tố nào?
A. Sodium
B. Chlorine
C. Magnesium
D. Neon
Đáp án: B
Giải thích: Z = 17 là chlorine, kí hiệu Cl.

Na = Sodium
Cl = Chlorine
O = Oxygen

Na | Kim loại
Mg | Kim loại
Cl | Phi kim
O | Phi kim
```

Câu hỏi dùng cho gameshow, vòng quay, bắn bóng và đua xe. Dòng `=` tạo cặp ghép/lật thẻ. Dòng `|` tạo dữ liệu phân loại. Cần ít nhất hai câu hỏi hoặc hai cặp ghép, và ít nhất ba thẻ thuộc từ hai nhóm phân loại.

Tệp TXT, MD, CSV có thể đọc trực tiếp. Khi chạy server, DOCX được trích văn bản bằng bộ đọc ZIP tích hợp; PDF dạng text được trích qua công cụ `pdftotext` nếu máy có cài. PDF scan/ảnh không được hỗ trợ OCR tự động.

## 4. Danh sách game và điều khiển

| Trò chơi | Gameplay thực tế | Dữ liệu cần có |
|---|---|---|
| Thử thách triệu phú | Thang điểm, quyền 50:50, bỏ qua, dừng | Câu hỏi |
| Rung chuông kiến thức | Các vòng thi, loại, quyền cứu trợ | Câu hỏi |
| Vòng quay kiến thức | Canvas wheel quay có giảm tốc, câu hỏi ngẫu nhiên | Câu hỏi |
| Lật ô bí mật | Lật thẻ 3D, ghi nhớ và ghép quan hệ | Cặp ghép |
| Bắn bóng kiến thức | Canvas, tâm ngắm, đạn, bóng chuyển động, va chạm | Câu hỏi |
| Đua xe kiến thức | Canvas pseudo-3D, chuyển làn bằng mũi tên, cổng đáp án | Câu hỏi |
| Ghép đôi | Chọn hai thẻ có quan hệ phù hợp | Cặp ghép |
| Phân loại | Kéo hoặc chạm thẻ và đưa vào vùng đúng | Đối tượng + nhóm |

## 5. Cấu trúc mã nguồn

- `index.html`: WebApp độc lập có thể mở trực tiếp; chứa toàn bộ JavaScript/CSS cần cho giao diện.
- `app.js` / `app.css`: Mã nguồn ứng dụng soạn bài, lưu dữ liệu, quản lý Game Instance và xuất HTML.
- `game.js` / `game.css`: Game Runtime tự chứa cho tám gameplay, dùng chung bộ điểm, phản hồi, trạng thái và sự kiện.
- `assemble.py`: Kết hợp các tệp nguồn thành một `index.html`.
- `server.mjs`: Server Node.js tùy chọn, proxy Gemini API, đọc DOCX/PDF dạng text.
- `examples/`: Tám game mẫu Hóa học 10 dưới dạng HTML độc lập.

Khi chỉnh sửa `app.js`, `game.js`, `app.css` hoặc `game.css`, chạy `python assemble.py` (hoặc `python3 assemble.py`) để tạo lại HTML phát hành. Server đọc tệp HTML mới khi người dùng reload.

## 6. Phạm vi và giới hạn đã biết

- WebApp đã có tám gameplay tương tác, Preview, Instance riêng, nút chỉnh sửa dữ liệu/cấu hình, nhân bản, xóa, Export HTML và sao lưu JSON.
- **Gemini là tùy chọn**, không tự hoạt động khi chỉ mở HTML không cấu hình server. Chế độ phân tích cục bộ chỉ đọc dữ liệu có cấu trúc, không suy luận sâu từ văn bản tự do.
- Game bắn bóng, đua xe đã có cơ chế Canvas riêng nhưng là sản phẩm giáo dục gọn nhẹ, không phải game engine 3D đầy đủ. Đua xe sử dụng pseudo-3D.
- Công cụ chỉnh sửa cho phép cập nhật dữ liệu nhiệm vụ và một số cấu hình, nhưng chưa có trình biên tập scene kéo thả hoặc hệ thống nhiều người chơi online.
- Lưu dự án là **local-first** trong trình duyệt; chưa có đồng bộ đa thiết bị hoặc đăng nhập. Cần sao lưu JSON định kỳ.
- Export mỗi game thành HTML tự chứa đã được kiểm thử bằng headless Chromium trong môi trường dựng nội dung. Việc mở trực tiếp bằng `file://` trên mọi hệ điều hành/trình duyệt chưa được kiểm chứng toàn bộ; hãy thử trên máy sử dụng thực tế.
- Tệp HTML offline có chứa đáp án đã chuyển thành Game Data, không nên coi đây là giải pháp bảo mật đề thi chính thức.
- Không có quảng cáo, thư viện CDN hoặc phông chữ bên ngoài bắt buộc trong các game xuất ra.

## 7. Kiểm thử

Đã kiểm tra tám Gameplay Runtime/Preview và tám bản HTML độc lập qua trình duyệt Chromium ở môi trường kiểm thử (không có lỗi JavaScript trong các luồng đã chạy). Các chức năng được kiểm thử bao gồm tạo Instance, mở Preview, bắt đầu game, thao tác bước đầu và xuất HTML riêng. Khả năng lưu trữ thực qua reload trên một website được triển khai cần thử thêm ở máy người dùng vì môi trường trình duyệt kiểm thử hạn chế truy cập nguồn `localhost/file://`.

**Hỗ trợ kỹ thuật:** Khi báo lỗi, ghi rõ tên game, bản trình duyệt, thao tác, tệp HTML có liên quan và ảnh chụp nếu có. Tuyệt đối không gửi API key.
