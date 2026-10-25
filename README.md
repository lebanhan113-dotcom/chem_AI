# EDUPLAN AI 7.6 – KIỂM ĐỊNH CÂU HỎI VÀ CÔNG THỨC HÓA HỌC

**Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất.  
**Sách:** Hóa học Kết nối tri thức với cuộc sống, lớp 10–12.  
**Tệp chạy chính:** `index.html` (HTML nhỏ; JavaScript, CSS và dữ liệu ở tệp riêng).

## 1. Nâng cấp so với EduPlan 7.5

- Thêm `js/chem-normalize.js`: bộ hiển thị công thức theo **cấu trúc đã nhận diện chắc chắn** bằng `<sub>`/`<sup>`; không ghi đè nguyên bản câu hỏi. Phân biệt hoa–thường **Co / CO** và **No / NO**.
- Hiển thị bổ sung trong đề bài, phương án trắc nghiệm, ghi chú Sổ ôn lỗi sai và phần diễn giải/sơ đồ tư duy SVG.
- Trường hợp nhận diện được: `H2O`, `H2SO4`, `Ca(OH)2`, `Al2(SO4)3`, `SO4^2-`, `Fe3+`, `NH4+`, `1s2 2s2 2p6`, `\\ce{2H2 + O2 -> 2H2O}` và đồng vị `\\({}^{27}_{13}\\mathrm{Al}\\)`.
- Bộ xuất `.docx` trực tiếp tại `js/docx-export.js` dùng **thuộc tính `w:vertAlign` subscript/superscript thật** trong Word; không xuất HTML/TXT đổi đuôi.
- Thêm thanh **Kiểm định câu hỏi**: bộ lọc khối–chương–bài, thống kê cảnh báo, 8 bước kiểm soát, tải các câu cần đối chiếu ra DOCX.
- Kiểm tra **bảo toàn nguyên tố** cho phương trình phân tử trung hòa đơn giản. Không kiểm chứng sản phẩm phản ứng hoặc điều kiện, không tự kết luận phản ứng ion/thuận nghịch.
- Thêm `data/quality_audit.json` và phép thử chạy không cần khóa API.

## 2. Hướng dẫn sử dụng tại mỗi chức năng

1. Trên thanh công cụ, mở **Kiểm định câu hỏi**.
2. Chọn khối, chương, bài, dạng và mức độ. Xem số câu có cảnh báo.
3. Đọc lỗi theo mã câu, mở **Tự giải** để xem câu nguồn và phương án.
4. Có thể nhập phản ứng đơn giản như `2H2 + O2 -> 2H2O` để kiểm tra số nguyên tử; với phương trình ion và phản ứng phức tạp, đối chiếu giáo viên/tài liệu gốc.
5. Nhấn **Tải câu cần rà soát Word .docx** nếu cần kiểm tra trên giấy.
6. Trở lại **Kho câu hỏi**, **Luyện 5/10/15**, **Phiếu tự học**, **Sổ ôn lỗi sai**, **Sơ đồ tư duy** để học và làm bài. Các chức năng cũ vẫn giữ nguyên.

## 3. Dữ liệu, độ tin cậy và giới hạn

- Giữ nguyên **1.958 câu hỏi nguồn** (Hóa 10: 809, Hóa 11: 473, Hóa 12: 676), **21 chương/78 bài KNTT**, **57 chuyên đề lỗi sai** và **99 sơ đồ tư duy**.
- Dữ liệu JSON Hóa 10/11/12, chương–bài, sổ lỗi sai và sơ đồ từ 7.5 được đối chiếu SHA-256 **không thay đổi**. Dữ liệu tự luyện cục bộ vẫn dùng khóa lưu của bản trước.
- **Không khẳng định tất cả 1.958 câu đã chuẩn chương trình, có đáp án đúng hoặc đã được giáo viên duyệt**. Bảng audit là bộ phát hiện nghi vấn kỹ thuật và metadata, không thay cho kiểm định nội dung từng câu.
- Phát hiện 1.958 câu **chưa có trường liên kết cụ thể** đến chủ đề và yêu cầu cần đạt (trong dữ liệu công khai); 672 câu chưa xác định mức độ; 445 câu chưa xác nhận bài; 58 câu nghi trùng, 11 câu trắc nghiệm thiếu phương án, 266 câu Đ/S thiếu cấu trúc, 139 câu có hình cần đối chiếu. Các nhóm **chồng lấn**, không được cộng thành tổng câu sai.
- Các biểu thức MathType/OLE, LaTeX phức tạp, phức chất, bảng có công thức, hệ có ion hoặc phương trình nhiều giai đoạn **không được tự động chuyển đổi hay xác minh**. Nếu không đọc được an toàn, chỉ hiển thị cảnh báo; phải đối chiếu bản Word gốc trước khi sử dụng kiểm tra chính thức.
- Bản này dành cho học sinh công khai: không chứa khóa đáp án; **không có quyền tự duyệt câu hỏi**, không tự chấm những câu chưa có khóa xác minh. Website tĩnh dùng localStorage, **chưa đồng bộ kết quả toàn trường**.
- Không yêu cầu `GEMINI_API_KEY` để tải câu hỏi, luyện tập, thống kê cục bộ, sơ đồ và xuất Word.

## 4. Chạy trực tuyến với GitHub Pages hoặc Vercel

**GitHub Pages:** Tạo repo → tải toàn bộ tệp vào nhánh `main`, giữ `index.html` ở thư mục gốc → Settings → Pages → Deploy from a branch → `main` → `/ (root)`.

**Vercel:** Import Git repo, chọn khung công nghệ Other / static site, root là thư mục có `index.html`. Giữ các thư mục `css`, `js`, `data`, `assets`, `references` và `tests`. `vercel.json` có sẵn.

Không mở `index.html` một mình qua `file://` khi dữ liệu được tải bằng `fetch`; để chạy cục bộ: trong thư mục dự án, gọi `python -m http.server 8000` rồi truy cập `http://127.0.0.1:8000`.

## 5. Kiểm thử và xác minh

`node tests/test_chem.js` → 24/24 phép kiểm tra ngữ pháp công thức, phân biệt kí hiệu, phương trình phân tử, JSON và không có khóa công khai.

Trình duyệt Chromium đã được thử ở 1440px và 390px: nạp ngân hàng, bảng kiểm định, thử phương trình, luyện câu, sơ đồ. Tệp Word mẫu đã mở và render bằng LibreOffice. Báo cáo chi tiết: `BAO_CAO_KIEM_THU_7_6.md`.

**Chưa thử**: GitHub Pages/Vercel trên tên miền thật, nhiều tài khoản Supabase, kiểm định hóa học độc lập cho từng câu, xuất Word với mọi loại MathType/OLE.


## EduPlan AI 7.7: giao dien toi gian va dap an sau nop

- Menu chinh con 6 muc: Trang chu, Chon bai, Luyen tap, Kiem tra, Ket qua, Hoc lieu & cong cu.
- Hai muc Luyen tap/Kiem tra co nut chon nhanh 5/10/15 cau, bo loc nang cao thu gon.
- Nhan Nop bai -> luu lich su -> goi API `/api/grade` neu trien khai tren Vercel.
- API chi tra dap an va loi giai cua cau co co `verified` truoc do va khong co canh bao du lieu.
- Trong bo nguon 6.6 co 379 cau mang co kiem chung; loai 2 cau can doi chieu bang, con 377 cau du dieu kien kiem tra o muc do du lieu hien tai.
- Thu muc `api` CHUA KHOA DAP AN. Phai de repo PRIVATE, Vercel serverless API. Khong public api code tren GitHub Pages.
- Khi chay GitHub Pages tu goi public, khong co API -> WebApp van luu bai, nhung khong the tu hien khoa dap an, va phai noi ro chua co may chu cham.
- Day la co che tra dap an sau nop cho TU HOC, khong co xac thuc/phong gian lan cua mot ky thi chinh thuc.
- 1958 cau nguon giu nguyen; chua tham dinh khoa hoc doc lap toan bo.
