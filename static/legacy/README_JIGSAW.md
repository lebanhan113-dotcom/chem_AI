# CHEM-MAP TUTOR AI 2.1 – Phiếu học tập Jigsaw

**Tác giả:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Cách sử dụng

1. Mở `CHEM_MAP_TUTOR_AI_2_1_Offline.html` bằng Chrome/Edge, hoặc tải các tệp WebApp lên Vercel dưới dạng web tĩnh.
2. Chọn vai trò **Giáo viên** (vai trò demo, chưa có đăng nhập), mở **Phiếu học tập Jigsaw** trong thanh điều hướng.
3. Tải nội dung bài học `.docx`, `.txt` hoặc `.md` (nếu có). Ứng dụng đọc phần văn bản vào ô tài liệu nguồn, **không tự phân tích và sinh đáp án bằng AI**. Tài liệu PDF cần chuyển sang Word/TXT hoặc dán văn bản thủ công. Công thức MathType/ảnh nhúng có thể không trích được, phải đối chiếu với bản gốc.
4. Sửa tên bài, yêu cầu cần đạt, câu hỏi A/B (4 câu mỗi nhóm), nhiệm vụ tổng hợp, bài luyện tập, phiếu cuối tiết, đáp án, bẫy thường gặp và chỉ báo năng lực số.
5. Xác nhận đã kiểm tra khoa học, nguồn, an toàn, mã năng lực số. Bấm **Xuất giáo án GV .docx** và **Xuất phiếu HS .docx**. Bản HS không xuất đáp án.
6. Có thể sao chép Prompt Jigsaw để sử dụng trong ChatGPT, sau đó dán kết quả đã kiểm duyệt vào biểu mẫu.

## Chức năng Jigsaw mới

- 6 nhóm gốc, 2 nhiệm vụ A/B; từ 48 HS -> 6 nhóm mảnh ghép có 4 chuyên gia A + 4 chuyên gia B.
- Đúng 45 phút: 4′ mở đầu, 30′ hình thành kiến thức (12′ chuyên gia + 2′ chuyển nhóm + 12′ mảnh ghép + 4′ báo cáo/chuẩn hóa), 5′ luyện tập, 6′ vận dụng/exit-ticket.
- 4 hoạt động với mục tiêu, nội dung, sản phẩm, 4 bước tổ chức.
- File giáo viên có đáp án, phân tích bẫy, sơ đồ tư duy A/B/tổng hợp, rubric, mức NLS, ma trận minh chứng.
- File học sinh có phiếu A/B, phiếu mảnh ghép, bài luyện, bài tự học vận dụng cao, sơ đồ tư duy trống và chỗ viết; **không có đáp án**.
- Mã NLS học sinh được đối chiếu: 1.2, 2.4, 3.1. Mức **Nâng cao 1 (Bậc 5)** cho lớp 10–12 theo CV 3456/2025. Không dùng khung NLS giáo viên TT18/2026 thay cho khung học sinh.
- Màu mức độ: xanh dương (Nhận biết), xanh lá (Thông hiểu), cam (Vận dụng), tím (Vận dụng cao), luôn kèm nhãn chữ.
- Cơ chế xuất Word hoàn toàn offline thông qua JSZip đóng gói tại `assets/jszip.min.js`. Không cần `GEMINI_API_KEY`.

## Phạm vi – kiểm soát chất lượng

- Jigsaw 2.1 là **trình biên soạn và xuất giáo án/phiếu theo quy tắc**; không có mô hình AI sinh bài, không tự nhận diện PDF, không xác nhận chính xác nội dung tệp nguồn và **không tự tạo tài liệu hoàn chỉnh cho bài mới chỉ bằng việc tải tệp**. Giáo viên phải biên tập và duyệt trước khi dùng.
- Ví dụ mặc định Hóa học 11 về tính acid và tính oxi hóa của nitric acid chỉ dùng để minh họa và kiểm thử. Mọi bài học và nội dung thí nghiệm thực tế cần đối chiếu chương trình, SGK và điều kiện an toàn của nhà trường.
- Dữ liệu biểu mẫu được lưu ở trình duyệt (LocalStorage), không đồng bộ nhiều máy. Chưa có đăng nhập/xác thực. Không nhập thông tin định danh học sinh thật vào demo.
- Đối chiếu: TT 32/2018/TT-BGDĐT và các văn bản sửa đổi liên quan; Phụ lục IV CV 5512/BGDĐT-GDTrH; TT 02/2025/TT-BGDĐT; CV 3456/BGDĐT-GDPT; TT 18/2026/TT-BGDĐT (dành riêng giáo viên/cán bộ quản lý).

## Bản mẫu và kiểm thử

- `Jigsaw_Hoa_11_Giao_vien_Le_Ba_Nhan.docx` – giáo án, đáp án, sơ đồ tư duy, rubric.
- `Jigsaw_Hoa_11_Hoc_sinh_Le_Ba_Nhan.docx` – phiếu học tập tự điền.
- Kiểm thử: `tests/engine.test.js` (Node), `tests/test_jigsaw.py`, `tests/browser_test.py`, `tests/browser_extended.py` (Playwright nếu môi trường hỗ trợ).
