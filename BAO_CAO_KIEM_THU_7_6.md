# BÁO CÁO KIỂM THỬ EDUPLAN AI 7.6

**Phạm vi:** nâng cấp lớp hiển thị, soát dữ liệu nguồn, kiểm thử không phá vỡ WebApp 7.5.  
**Tác giả:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## A. Hoàn thành và đã kiểm thử

| Hạng mục | Kết quả |
|---|---|
| Bảo toàn 1.958 câu Hóa 10–12 | Đối chiếu SHA-256: không thay đổi 3 tệp JSON nguồn |
| Giữ nguyên danh mục 21 chương, 78 bài và 99 sơ đồ | Đối chiếu tệp dữ liệu + kiểm tra cấu trúc |
| Giữ nguyên Sổ ôn lỗi sai 57 chuyên đề | Tệp dữ liệu không đổi |
| Hiển thị H₂O, H₂SO₄, Ca(OH)₂, Al₂(SO₄)₃ | Đạt kiểm tra HTML/Word có chỉ số dưới |
| Hiển thị SO₄²⁻, Fe³⁺, NH₄⁺, cấu hình electron, đồng vị | Đạt kiểm tra HTML/Word có chỉ số trên/dưới |
| Phân biệt Co/CO, No/NO | Không tự thay chữ hoa/thường; đạt phép kiểm tra |
| Hiển thị phương trình dạng `\ce{2H2 + O2 -> 2H2O}` | Chuyển mũi tên và chỉ số có cấu trúc; đạt kiểm tra |
| Kiểm tra bảo toàn nguyên tử phương trình trung hòa | Nhận đúng ca cân bằng/chưa cân bằng; công khai giới hạn |
| Xuất Word `.docx` thực | Có `w:vertAlign` chuẩn Word; tệp giải nén XML hợp lệ, mở/render LibreOffice đạt |
| Bảng kiểm định theo khối–chương–bài | Mở được; không tự duyệt câu nguồn |
| Chạy thử trình duyệt Chromium 1440 px và 390 px | Tải 1.958 câu, lọc/kiểm tra/luyện/sơ đồ; không có lỗi JavaScript trong luồng thử, không tràn ngang |
| Kiểm thử bằng `node tests/test_chem.js` | 24/24 ca đạt |

## B. Cảnh báo chất lượng phát hiện trong dữ liệu nguồn

| Chỉ tiêu | Số câu mang cờ |
|---|---:|
| Chưa liên kết chủ đề kiến thức | 1.958 |
| Chưa liên kết yêu cầu cần đạt | 1.958 |
| Nguồn có cờ cần rà soát khoa học | 1.769 |
| Mức độ NB/TH/VD/VDC chưa xác minh | 672 |
| Bài KNTT chưa xác nhận | 445 |
| Câu Đúng/Sai thiếu cấu trúc 4 ý | 266 |
| Có ảnh cần đối chiếu nguồn | 139 |
| Nội dung có dấu hiệu trùng | 58 |
| Trắc nghiệm A–D chưa đủ 4 phương án | 11 |

**Cách hiểu:** một câu có thể mang nhiều cờ. Đây là cảnh báo metadata / trích xuất tự động, KHÔNG có nghĩa toàn bộ là câu sai khoa học. Không tự động sửa hoặc phê duyệt.

## C. Chưa hoàn thành, chưa nghiệm thu

- Chưa kiểm chứng độc lập nội dung, đáp án, phương trình và lời giải của từng câu trong 1.958 câu; chưa thể xác nhận đầy đủ 8 bước theo tiêu chí người dùng.
- Chưa xác lập từng yêu cầu cần đạt của GDPT 2018 và chủ đề kiến thức cho từng mã câu.
- Chưa khôi phục trực quan toàn bộ công thức MathType/OLE/ảnh nguồn; công cụ hiển thị chỉ xử lý các cấu trúc có thể xác định chắc chắn.
- Chưa triển khai hoặc thử bằng URL GitHub Pages/Vercel thực tế; chưa thử Supabase đa thiết bị hoặc phân quyền chỉnh sửa.
- DOCX mẫu đạt, nhưng chưa kiểm thử định dạng Word với tất cả 1.958 câu; những câu có công thức/hình phức tạp cần đối chiếu sau khi xuất.

## D. Nguyên tắc bảo đảm an toàn

1. **Không sửa ngầm** JSON nguồn, không giả định khóa đáp án khi chưa có bằng chứng.
2. **Không tự phê duyệt** câu dựa vào trình định dạng, cảnh báo hay phép kiểm tra cân bằng.
3. **Không công khai** đáp án hoặc cấu hình quản trị trên GitHub Pages.
4. Nếu biểu thức nằm ngoài khả năng định dạng, **báo cần xem nguồn**, không tự suy đoán.
