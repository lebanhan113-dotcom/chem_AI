# EDUPlan AI 7.13 – Hóa học THPT KNTT

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Nội dung bản bàn giao

- Giao diện: 17 thẻ chức năng gốc hiển thị ngoài menu, cộng thêm một thẻ nổi bật **Ngân hàng 7 đề Hóa học 10**. Nhấn thẻ để mở màn hình ngay, không có menu trung gian.
- Ngân hàng trực tuyến có 217 câu: 154 câu Hóa 10, 63 câu Hóa 11, chưa có câu Hóa 12 vượt bộ lọc công bố hiện tại. Trong 217 câu có 42 câu trắc nghiệm mới được rà soát và gán chương/bài/mức độ theo nguồn 2026–2027.
- Đã nhập 145/145 câu từ 7 đề nguồn theo 4 phần: I – 84 câu A–D; II – 14 câu Đúng/Sai bốn ý; III – 28 câu trả lời ngắn; IV – 19 câu tự luận. **103 câu chưa hoàn tất thẩm định được lưu trong ZIP riêng tư; không có trong gói WebApp phát hành.**
- Có 21 chương, 78 bài KNTT, 57 chuyên đề lỗi sai, 99 sơ đồ tư duy.
- Có thể chọn khối → chương → bài → phần → mức độ rồi tự luyện / làm bài và tải Word `.docx` thực sự.

## Triển khai Vercel có chấm bài

1. Giải nén ZIP WebApp. Tạo một repository **Private** trên GitHub, đưa toàn bộ nội dung thư mục vào gốc repository. **Không chỉ tải riêng `index.html`**.
2. Nhập repository vào Vercel và triển khai với thiết lập mặc định cho dự án gồm trang tĩnh và thư mục `/api`. Không yêu cầu `GEMINI_API_KEY`.
3. Kiểm tra `/` hiện trang chủ; `/data/hoa10.json` tải được nhưng **không chứa khóa đáp án**; `/api/grade` chấp nhận POST và trả đáp án sau khi nộp với câu trong danh sách máy chủ.
4. Trên trình duyệt: mở **Ngân hàng 7 đề Hóa 10 → Chọn chương → Chọn bài → Luyện ngay**. Chọn đáp án, xác nhận, nộp và kiểm tra phần đáp án/lời giải. Tải bản DOCX nếu cần.
5. Thử trên điện thoại và máy tính với bài/chương có đủ câu; với lớp 12 hoặc phần II/III/IV chưa có câu công bố, ứng dụng phải báo thiếu, không tự chèn câu chưa kiểm duyệt.

**Bảo mật:** Gói Vercel chứa khóa đáp án ở `api/grade.js`. Repository phải ở trạng thái Private. Không triển khai toàn bộ ZIP này như website tĩnh công khai trên GitHub Pages; không tải thêm gói kho thẩm định riêng tư vào repo của WebApp.

**Hạn chế:** API hiện là dịch vụ phản hồi tự luyện, chưa có xác thực học sinh, chống gian lận, giám thị hoặc lưu bài làm tập trung. Bài làm/lịch sử hiện ở trình duyệt trên thiết bị. Để dùng kiểm tra chính thức cần phát triển đăng nhập + cơ sở dữ liệu và thử nghiệm bảo mật. Chưa triển khai và nghiệm thu trên tên miền Vercel thực tế trong môi trường này.

## Các nguồn mới và chất lượng dữ liệu

Bảy nguồn DOCX: Cấu tạo nguyên tử; Bảng tuần hoàn; Liên kết hóa học; Phản ứng oxi hóa–khử; Năng lượng hóa học; Tốc độ phản ứng; Nguyên tố nhóm halogen (mỗi nguồn đề 1, năm học 2026–2027).

Đã phát hiện trường hợp câu trùng, thiếu ký hiệu nhiệt hóa học do MathType, đáp án nguồn hoặc lời giải có mâu thuẫn, ví dụ tự luận MgCO₃ + HCl trong nguồn ghi sai sản phẩm. Câu nghi vấn không được xuất bản tự động. **42 câu công bố mới đã được đối chiếu thủ công đáp án/đề mục trước khi nhập, nhưng vẫn nên giáo viên xác nhận lần cuối trước khi dùng chính thức.**

## Kiểm thử

- `node tests/test_chem.js`: 24/24 kiểm tra hóa học/cấu trúc.
- `node tests/test_grade77.cjs`: 7/7 kiểm tra API.
- `node tests/test_publish711.cjs`: kiểm tra số câu/khóa/chương bài.
- `node tests/test_source712.cjs`: kiểm tra bảy nguồn, 145 bản ghi nhập, 42 công bố, 217 khóa chấm.
- Chromium kiểm tra màn hình 1440px và 390px với dữ liệu JSON đúng từ bộ đóng gói (nạp HTML/CSS/JS vào trang giả lập do môi trường kiểm thử chặn `localhost`). Truy cập 7 chương, luyện từng câu, xác nhận và lưu, không tràn ngang/lỗi JS trong luồng thử.
- Tải DOCX từ Chromium; kiểm tra tính toàn vẹn ZIP và dựng trang bằng LibreOffice.

**Chưa nghiệm thu:** môi trường Vercel thực tế, tải hệ thống nhiều học sinh, chấm tất cả dạng Đúng/Sai/trả lời ngắn/tự luận trong các nguồn vừa nhập, độ chính xác độc lập toàn bộ 217 câu.


## TÍCH HỢP PHIÊN BẢN 7.13

- Màn hình đầu hiển thị thẻ chức năng và toàn bộ 21 chương Hóa 10–12 ngay bên ngoài thanh công cụ.
- Đã trích 294 câu từ 14 DOCX: 168 A–D, 28 Đúng/Sai, 56 trả lời ngắn, 42 tự luận.
- 105 câu A–D được đối chiếu đáp án bước đầu và bổ sung vào kho công khai. 189 câu còn lại CHỈ có trong ZIP thẩm định riêng, KHÔNG tải lên web.
- Ngân hàng công khai: 322 câu. Phần II–IV của bộ nguồn mới cần kiểm duyệt hình và đáp án trước khi chấm.
- Sau nộp: /api/grade chỉ trả đáp án và ghi chú câu có khóa. Chạy index.html đơn lẻ sẽ không có API chấm.
- Giáo viên cần kiểm tra vòng cuối trước thi chính thức. Kết quả học tập hiện lưu trên thiết bị, chưa có máy chủ lưu báo cáo lớp.
- Giữ GitHub repository PRIVATE khi có API chứa đáp án. Không đưa bất kỳ ZIP thẩm định hoặc tệp answer keys lên GitHub công khai.
