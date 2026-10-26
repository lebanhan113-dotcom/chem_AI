# Báo cáo nâng cấp EduPlan AI 7.9

## Đã xử lý

1. Khắc phục lỗi nghiêm trọng: hai hàm `chem()` trùng tên khiến nội dung câu hỏi bị thay bằng giao diện Công cụ Hóa học; đổi tên hàm của trang công cụ, khôi phục định dạng câu hỏi bằng `EduPlanChem.html`.
2. Giữ nguyên dữ liệu gốc: 1.958 câu hỏi, 21 chương/78 bài KNTT, 57 chuyên đề lỗi sai, 99 sơ đồ.
3. Thêm mục Form 2025 (18 + 4 + 6), có lựa chọn mở rộng thêm 4 tự luận và báo thiếu câu chính xác theo từng phần.
4. Phần Đúng/Sai hiển thị bốn ý riêng và các ô chọn Đúng/Sai; những câu không tách được đủ bốn ý không lấy làm đề chuẩn.
5. Sau nộp, hiển thị lại toàn bộ nội dung 28 câu, lựa chọn và câu trả lời; chỉ công bố đáp án/lời giải đã có khóa trên API. Câu thiếu khóa hiển thị chờ kiểm duyệt.
6. Xuất Word `.docx` thật cho đề, bài làm và lời giải có sẵn, có thể lưu về máy.
7. Liên kết Form từ Trang chủ/Chọn bài/Luyện tập/Tạo đề/Phiếu học tập mà không tách ngân hàng.

## Kiểm thử đã chạy trong container

- 24/24 phép thử dữ liệu/công thức và 7/7 phép thử API chấm điểm từ dự án trước: đạt.
- Chromium dùng nội dung HTML và dữ liệu gốc nạp trực tiếp (không phải URL triển khai thực): 1400 px và 390 px, nạp đủ 1.958 câu; Form 2025 tạo 28 câu, 4 câu TF4 thành 16 ô chọn; nộp bài trả về 28 bản ghi câu hỏi; xuất hai tệp DOCX hợp lệ; không phát sinh lỗi JavaScript, không tràn màn hình.
- Kiểm thử hồi quy: mở Luyện từng câu và khung làm bài tại Sơ đồ tư duy; chọn 5 câu không trùng; thiếu câu đúng bài thì thông báo, không tự lấy câu ngoài phạm vi; Form đủ khi phạm vi toàn khối.
- DOCX được kiểm tra ZIP/OOXML và dựng trang bằng LibreOffice. Nội dung có bảng câu trả lời/lời giải và chỉ số dưới với trường hợp nhận diện được.

## Chưa hoàn thành/chưa đạt nghiệm thu chính thức

- Chưa triển khai và đo kiểm từ URL Vercel thực tế; API trong luồng thử trình duyệt được **mô phỏng bằng đúng bộ khóa máy chủ hiện có**.
- Chưa thẩm định độc lập toàn bộ 1.958 câu hỏi; chỉ có 377 khóa từ dữ liệu rà soát trước, trong đó không có TF4/tự luận.
- Đa phần câu hỏi nguồn cũ còn MathType/OLE có thể thiếu công thức; không tự suy diễn hay điền dữ kiện. Câu nghi vấn cần đối chiếu Word gốc.
- Chưa có tài khoản bảo mật, chấm điểm theo đầy đủ thang 10 điểm chính thức, lưu điểm tập trung, kiểm tra chống gian lận.
- Bản Vercel Private được giao để **thử tự học**; không dùng làm đề thi chính thức cho đến khi thẩm định nội dung và nghiệm thu bảo mật.
