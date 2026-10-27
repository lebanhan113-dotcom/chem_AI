# CHEM-MAP TUTOR AI V7.2 – Quản lý lớp học, giao bài và thống kê tập trung

**Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất**

## A. Phiên bản bàn giao

Phiên bản V7.2 là ứng dụng web có máy chủ Node.js và cơ sở dữ liệu SQLite được lưu **tập trung trên một máy chủ**, không phải tập tin HTML dùng độc lập. Không yêu cầu Gemini API key. Có thể chạy cục bộ ngay sau khi cài Node.js 22.13 trở lên; dùng cho **kiểm thử kỹ thuật**. Chưa được triển khai, nghiệm thu bảo mật và vận hành công khai trên Internet.

Ngân hàng kế thừa V7.1 gồm **1.113 bản ghi câu hỏi minh họa**, có cả biến thể, gắn theo danh mục KNTT **21 chương / 78 bài** cho lớp 10–12. Cần kiểm duyệt trước khi dùng kiểm tra thực tế.

## B. Chạy trên Windows – hướng dẫn nhanh

1. Cài **Node.js 22.13 trở lên** từ https://nodejs.org/ (nên dùng bản LTS phù hợp).
2. Giải nén tệp ZIP, không chạy trong cửa sổ xem trước tệp nén.
3. Nhấp đúp `START_CHEM_MAP_WINDOWS.bat` và giữ cửa sổ lệnh mở.
4. Mở trình duyệt vào **http://127.0.0.1:8080/**.
5. Ở lần khởi tạo đầu, cửa sổ lệnh hiển thị **tài khoản giáo viên quản trị** và **học sinh demo**, cùng mật khẩu được sinh ngẫu nhiên. Tên người dùng và mật khẩu không được cố định trong mã nguồn.
6. Đăng nhập giáo viên quản trị; tạo lớp (ví dụ 10A1), thêm học sinh với tài khoản, tạo bài luyện tập mẫu 5 câu; đăng nhập tài khoản học sinh để làm bài; đăng nhập lại giáo viên để xem báo cáo và xuất CSV.

**Nếu đã có cơ sở dữ liệu:** tài khoản cũ được giữ nguyên; chương trình không tạo lại mật khẩu demo. Nếu quên mật khẩu, không xóa cơ sở dữ liệu nếu chưa sao lưu và chưa có phương án khôi phục.

## C. Chạy macOS / Linux

Chạy `sh START_CHEM_MAP_MAC_LINUX.sh` từ thư mục đã giải nén, sau đó mở http://127.0.0.1:8080/.

Hoặc chạy trực tiếp:

```bash
CHEMMAP_DEMO=1 node server/server.js
```

## D. Tài khoản quản trị không dùng chế độ demo

Đặt biến môi trường trước **lần khởi tạo cơ sở dữ liệu trống**:

```bash
TEACHER_USERNAME=giaovien1 TEACHER_PASSWORD='MatKhauManhCuaBan2026!' node server/server.js
```

Trên PowerShell dùng `$env:TEACHER_USERNAME` và `$env:TEACHER_PASSWORD`. Không commit mật khẩu lên Git. Nếu cần truy cập qua HTTPS, đặt `HTTPS_ONLY=1` tại reverse proxy sau HTTPS; không bật cờ này khi chỉ dùng HTTP localhost, vì trình duyệt có thể không gửi cookie.

## E. Năm phân hệ hoạt động

| Phân hệ | Chức năng |
|---|---|
| Quản lý lớp học | Tạo lớp theo khối và năm học, phân công giáo viên (quản trị), liệt kê lớp được phụ trách. |
| Danh sách học sinh | Tạo tài khoản học sinh, ghi danh tài khoản đã có, xem số lượt nộp và thời điểm nộp gần nhất. |
| Giao bài | Lọc ngân hàng theo khối, chương, bài; tạo 5/10/15 câu; chỉ bài được duyệt cho chế độ kiểm tra; yêu cầu hạn đóng; giới hạn một lần nộp. |
| Theo dõi kết quả | Xem học sinh chưa bắt đầu / đang làm / đã nộp, điểm tự động chấm, xuất danh sách CSV. |
| Thống kê toàn trường | Quản trị thấy tổng các lớp/học sinh/bài giao, các trình duyệt truy cập duy nhất theo cookie trong 90 ngày; giáo viên thấy dữ liệu lớp được phân công. |

**Lưu ý cách đếm:** `Lượt truy cập` = lượt mở trang ghi vào bảng visits trong 90 ngày, `trình duyệt duy nhất` = cookie (không tương đương người thật). `Học sinh tham gia` = số tài khoản HS khác nhau đã bắt đầu hoặc nộp. `Lượt nộp` = số phiên nộp, một học sinh có thể có nhiều lượt ở các bài khác nhau.

## F. Quyền truy cập

- **Quản trị:** xem thống kê toàn trường, tạo giáo viên và phân công lớp, toàn bộ lớp và bài giao.
- **Giáo viên:** tạo lớp, tạo tài khoản học sinh, xem danh sách và giao bài CHỈ cho lớp được phân công. Giáo viên không thể xem báo cáo bài giao của lớp khác.
- **Học sinh:** chỉ thấy bài giao cho các lớp mình đã ghi danh; làm bài một lần; không được xem API quản trị.

Bài kiểm tra bắt buộc có hạn đóng; trước hạn đó, đáp án và điểm không được trả về trong phản hồi nộp bài hay API lịch sử học sinh. Bài luyện tập minh họa có thể hiển thị lời giải sau khi nộp; không dùng câu chưa thẩm định cho thi thật.

## G. Lưu trữ và sao lưu

Cơ sở dữ liệu mặc định: `server/data/chemmap.db` và các tệp WAL liên quan khi server đang mở. Để sao lưu nhất quán, **dừng máy chủ** rồi sao chép toàn bộ thư mục `server/data/`; kiểm tra khôi phục trên một bản riêng. Có thể chuyển dữ liệu sang máy chủ PostgreSQL cho môi trường dùng thật; V7.2 **chưa triển khai PostgreSQL và chưa đồng bộ giữa các máy chủ độc lập**.

Không tải thư mục `server/data/` lên GitHub hay đặt cơ sở dữ liệu trong thư mục phục vụ file tĩnh. Phải đặt `DATA_DIR` ở đường dẫn lưu trữ bền vững nếu triển khai bằng máy chủ riêng. Hosting chỉ có ổ đĩa tạm sẽ làm mất dữ liệu SQLite khi khởi động lại/triển khai mới.

## H. Đã kiểm thử và giới hạn

- Kiểm thử 37 trường hợp API: đăng nhập, phân quyền, tạo lớp, học sinh, phân công, giao bài, bắt đầu, nộp, chống nộp hai lần, báo cáo, CSV.
- Kiểm thử giao diện trong Chromium (qua cầu nối yêu cầu API do môi trường chặn localhost trực tiếp): quản trị tạo lớp, ghi danh, giao bài, học sinh làm 5 câu trên màn hình điện thoại, giáo viên xem kết quả.
- Kiểm thử riêng chế độ kiểm tra: câu đã duyệt, không gửi đáp án trước khi nộp, không cho lộ điểm/lời giải trước hạn đóng.
- Bản chạy còn là nguyên mẫu: SQLite theo kiến trúc một máy chủ, Node `node:sqlite` chưa có cam kết ổn định dài hạn tương đương thư viện đã trưởng thành, chưa có khôi phục mật khẩu, nhật ký kiểm toán chi tiết, quản lý xóa dữ liệu, kiểm thử tải lớn, đánh giá bảo mật độc lập hoặc chính sách quyền riêng tư đã được trường thông qua.

**Tuyệt đối không dùng dữ liệu định danh học sinh thật trong giai đoạn này nếu chưa có chấp thuận và biện pháp bảo vệ dữ liệu phù hợp.**

## I. Công việc cần làm trước triển khai trường học

1. Kiểm duyệt chuyên môn ngân hàng 1.113 câu, gắn người duyệt, ngày duyệt, phiên bản; tách kho đề chính thức và kho minh họa.
2. Chuyển lớp dữ liệu sang PostgreSQL quản lý, bổ sung migration, sao lưu tự động, kiểm tra khôi phục, đặt máy chủ HTTPS có domain; không triển khai SQLite trong môi trường serverless có lưu trữ tạm.
3. Hoàn thiện chính sách phân quyền theo trường, lớp, giáo viên; kiểm toán quyền theo tình huống chéo lớp và thay đổi giáo viên chủ nhiệm.
4. Thêm đặt lại mật khẩu, trạng thái tài khoản, sửa/xóa thành viên, import học sinh theo biểu mẫu có xác nhận, lịch sử thay đổi điểm và quản lý thời hạn dữ liệu.
5. Kiểm thử bảo mật bởi bên độc lập, thử tải nhiều lớp; phê duyệt sử dụng dữ liệu học sinh, thông báo quyền riêng tư, kế hoạch xử lý sự cố.
6. Thử nghiệm sư phạm có đối chứng phù hợp; đối chiếu pre/post-test tương đương độ khó và minh chứng tiến bộ.

**Tài khoản và quyền triển khai hosting:** hiện không có kết nối đến tài khoản GitHub/Vercel/Supabase của người dùng. Gói này có thể chạy localhost, nhưng chưa có URL công khai.
