# CHEM-MAP TUTOR AI V7.0

**Tác giả:** Lê Bá Nhẫn – Trường THPT Hòn Đất.

## Trạng thái triển khai

- **WebApp HTML chạy được offline** và gói **Vercel Static demo**; không cần Gemini API key.
- 1113 bản ghi **mẫu, chưa được giáo viên thẩm định đầy đủ**; bổ sung 99 câu mới, trong đó 78 MCQ riêng theo từng bài và 21 bài trả lời ngắn định lượng gắn theo chương.
- Danh mục 21 chương/78 bài KNTT lớp 10 (23), lớp 11 (25), lớp 12 (30).
- Đã bổ sung chọn *ngân hàng minh họa* hoặc *chỉ câu giáo viên đã duyệt* ở khu vực luyện tập. Số câu trong bộ được duyệt có thể chưa đủ để tạo đề.
- Sửa lỗi khôi phục sao lưu: tệp sao lưu V3/V4/V5/V6/V7 hợp lệ có thể nhập vào V7 (sao lưu trước khi chuyển).
- Luyện 5/10/15 câu tùy ngân hàng và bộ lọc; 4 dạng câu Form 2025; chấm theo đáp án và quy tắc; gợi ý học lại, chuyển giao câu mới, bản đồ năng lực.
- **Bản demo tĩnh có đáp án trong source trình duyệt**, nên không dùng để thi thật, không nhập tên thật HS.
- **Máy chủ Node.js/SQLite** chỉ dùng localhost / phòng thí nghiệm kỹ thuật. Đáp án lưu server trước khi nộp, xác thực GV/HS và chấm tự luận do giáo viên; chưa đủ điều kiện vận hành công khai.

## Bộ dữ liệu & kiểm tra

Tải CSV kiểm duyệt toàn bộ và báo cáo độ phủ đi kèm. Không đồng nhất 1113 bản ghi với 1113 ý tưởng câu hỏi độc lập; có biến thể tính toán trong bộ cũ. Có 19 bài dưới 10 câu, 36 bài dưới 15 câu.

Nguồn tham khảo: SGK Hóa học 10/11/12 KNTT (chỉ tên mục lục), RSC Education, ACS, ChemCollective, PhET, IUPAC/NIST và OpenStax. Không sao chép hàng loạt tài liệu có bản quyền.

## Triển khai demo Vercel

1. Giải nén `CHEM_MAP_TUTOR_AI_V7_VERCEL_DEMO.zip`.
2. Đưa `index.html`, các tệp js, css, json trong gói vào một repository GitHub mới.
3. Từ Vercel Dashboard chọn Add New → Project → Import Git Repository → Framework Preset Other → Deploy.
4. Chỉ chia sẻ URL thử nghiệm, không thu thập dữ liệu cá nhân học sinh hoặc dùng tạo đề kiểm tra bảo mật.

## Để hoàn thành bản trường học

1. Duyệt từng câu, đáp án, ký hiệu hóa học, bản quyền, nội dung thực tiễn và ma trận NB/TH/VD/VDC, HH1–HH3.
2. Chuyển backend thử nghiệm sang hệ thống PostgreSQL, xác thực tài khoản, phân quyền theo trường/lớp, sao lưu và phục hồi dữ liệu.
3. Chấm bài trên server, tạo đề riêng cho từng lớp, ẩn đáp án trước khi nộp, chống sửa điểm và tạo báo cáo GV.
4. Kiểm thử nghiệp vụ và bảo mật, xin phép nhà trường, rồi thử nghiệm sư phạm với dữ liệu tối thiểu và sự đồng ý thích hợp.

**Không có URL Vercel công khai được xuất bản trong phiên này.** Tải bản HTML để chạy trên thiết bị ngay.
