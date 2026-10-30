# Báo cáo kiểm thử bản bàn giao A4

**Thử nghiệm được thực hiện trên mã nguồn trong gói này. Không có chứng nhận thử nghiệm trên Supabase production.**

| Hạng mục | Kết quả |
|---|---|
| `node --check web/app.js`, `word.js`, `api.js` | Không lỗi cú pháp |
| `node --experimental-strip-types --check .../index.ts` | Không lỗi cú pháp TypeScript có thể strip |
| `node tests/test_scoring.mjs` | PASS: nhiều lựa chọn, Đúng/Sai, trả lời ngắn, tự luận chờ chấm |
| `python tests/test_browser.py` | PASS: đọc 21 câu từ file Word thực (15 + 2 + 4), nhận diện chữ đỏ, cảnh báo WMF |
| `python tests/test_student_mock.py` | PASS: luồng học sinh (API mock), nộp không thấy điểm, `.xlsx` hợp lệ |
| `python tests/test_standalone.py` | PASS: WebApp một tệp chứa 21 câu chờ duyệt, không lỗi JS |
| SQL migration trên Supabase thật | CHƯA: chưa có dự án/truy cập |
| Edge Function được triển khai và chạy trực tuyến | CHƯA: chưa có thông tin Supabase |
| Kiểm thử nhiều thiết bị/mạng yếu | CHƯA: cần phòng thi thật |
| Xuất PDF/WMF/OMML phức tạp bảo toàn 100% | CHƯA: yêu cầu bổ sung ảnh gốc/kiểm tra thủ công |

**Dữ liệu gốc:** `DE_GOC_HOA10_CHO_GIAO_VIEN_DUYET.json` chỉ chứa câu đã trích xuất; toàn bộ được giữ `approved = false`, `points = 0` do chưa có hướng dẫn chấm. Không có đề giả được thêm vào WebApp.
