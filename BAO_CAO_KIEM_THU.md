# Báo cáo kiểm thử cục bộ – EduPlan AI 7.14 WebApp nâng cấp

**Ngày thực hiện:** 27/10/2026  
**Dữ liệu:** 623 câu trước đó + 150 câu không trùng từ bốn nguồn Hóa học 12.  
**Tổng:** 773 câu. Đủ điều kiện nhập có khóa nguồn để luyện chấm theo quy tắc cấu trúc: 112 câu. Tự luyện nguồn không chấm: 661 câu.

## Đầu vào mới

| Tệp | Lượt trích xuất | Lượt trùng | Câu mới | Đủ điều kiện khóa nguồn | Cách ly tự động |
|---|---:|---:|---:|---:|---:|
| Pin điện và điện phân | 34 | 1 | 33 | 1 | 32 |
| Đại cương kim loại | 52 | 2 | 50 | 1 | 49 |
| Nhóm IA, IIA | 24 | 0 | 24 | 0 | 24 |
| Kim loại chuyển tiếp và phức chất | 44 | 1 | 43 | 0 | 43 |
| **Tổng** | **154** | **4** | **150** | **2** | **148** |

## Các tình huống đã kiểm tra

- API tải danh sách trả về **chỉ câu hỏi**, không có trường `correct`, `explanations` hoặc `solutionIntroHtml`.
- API tạo bài chọn được 5 câu không trùng theo khối/chương; API nộp chấm 20 mệnh đề, trả từng câu gốc, 4 lựa chọn, đáp án nguồn, 4 lời giải và đánh dấu ý đúng/sai.
- Không cho nộp lại cùng phiên sau khi hoàn thành.
- Kho nguồn Hóa 12 chương 7–8 không nhận khóa đáp án để chấm khi tài liệu chưa có lời giải.
- API giáo viên từ chối truy cập thiếu xác thực; cho phép tải dữ liệu khi có mật khẩu.
- Nhập lại tệp DOCX “Pin điện và điện phân”: 34 câu nhận diện trùng, không thêm bản sao; tự xác định lại Hóa 12/Chương 5 ngay cả khi biểu mẫu chọn nhầm lớp.
- Thử nhập câu CSV mới có khóa nguồn đủ, sau đó nhập lần hai: lần đầu bổ sung 1, lần hai chặn trùng 1; dữ liệu kiểm thử đã được loại khỏi tệp giao.
- Test browser giao diện và màn hình kết quả qua Chromium trên 1440 px và 390 px: không có lỗi JavaScript, không xuất hiện tràn ngang. Do chính sách môi trường chặn mở localhost trong Chromium, bài kiểm thử giao diện dùng API giả lập; API thật được thử độc lập qua HTTP.

## Giới hạn và bước khuyến nghị trước khi chạy Internet

Không xác nhận đáp án Hóa học tuyệt đối: tài liệu nguồn có thể chứa lỗi học thuật, mâu thuẫn hoặc phương trình MathType/OLE không chuyển thành hình. Hệ thống không tự dựng đáp án bị thiếu. Mô-đun không bao gồm tài khoản học sinh, HTTPS, nhật ký xác thực, rate-limit, cơ sở dữ liệu chịu tải hoặc tích hợp trực tiếp GitHub/Vercel/Supabase. Chỉ phù hợp thử nghiệm trên máy giáo viên cho đến khi thực hiện tích hợp chính thức.
