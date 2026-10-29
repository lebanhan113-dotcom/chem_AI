# EDUVIDEO FLOW AI V4.1.1 — Chạy bằng index.html

**Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất**

**Đối tượng:** giáo viên lớp 1–12; hỗ trợ mọi môn, ưu tiên quy tắc kiểm tra kiến thức Hóa học.

**Trạng thái bàn giao:** mã nguồn backend + **`index.html` tại thư mục gốc**, có các endpoint thực, SQLite, bộ điều phối và FFmpeg. **Chưa tạo video Google thật trong môi trường bàn giao** vì không có tài khoản Google Cloud/quyền Veo hoặc API key; tuyệt đối không giả lập kết quả như thể đã tạo thành công.

## 1. Cấu hình ban đầu

Cần Python 3.11+, FFmpeg/FFprobe, Internet và quyền truy cập dịch vụ Google theo tài khoản của người triển khai. Chạy trong thư mục dự án:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows: sao chép `.env.example` thành `.env` trong File Explorer.

Điền trong `.env`:

```dotenv
GEMINI_API_KEY=YOUR_SERVER_SIDE_GEMINI_KEY
GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
VEO_LOCATION=us-central1
VEO_MODEL=veo-3.1-generate-001
APP_ACCESS_TOKEN=your-long-private-app-access-code
```

Đối với Veo 3.1 chính thức, cần Google Cloud Application Default Credentials và quyền model tương ứng:

```bash
gcloud auth application-default login
# Hoặc GOOGLE_APPLICATION_CREDENTIALS=/secure/private/service-account.json
```

> **Quan trọng:** Gemini API **Veo 3.1 Preview đã dừng ngày 22/10/2026**. Không dùng `veo-3.1-generate-preview`. Bản GA `veo-3.1-generate-001` dùng qua Google Cloud / Gemini Enterprise Agent Platform nếu tài khoản có quyền sử dụng. Khả năng truy cập/quota/fixed quota cần được xác nhận. `GEMINI_API_KEY` là khóa cho Gemini phân tích và Nano Banana, **khác** quyền Google Cloud Veo. Khóa/credential đều chỉ có ở server.

## 2. Khởi động WebApp

```bash
python server.py
```

Mở **http://localhost:8000/index.html** (hoặc **http://localhost:8000/**). Tệp chạy chính nằm tại **`index.html` ở thư mục gốc** và đã chứa sẵn CSS/JavaScript cho giao diện. Có thể nháy đúp index.html để **xem giao diện và hướng dẫn**, nhưng **không thể tạo video thật khi mở bằng `file://`**, vì cần chạy máy chủ để kết nối API AI và FFmpeg. Nếu chỉnh sửa frontend trong `static/`, chạy `python build_index.py` để cập nhật file index.html gốc. Nếu cấu hình `APP_ACCESS_TOKEN`, trang web sẽ yêu cầu nhập mã truy cập ứng dụng lần đầu; đây **không phải** khóa Gemini.

### Triển khai trực tuyến

Có Dockerfile. Với Render/Railway/VM có **ổ lưu trữ bền vững** và FFmpeg:

```bash
docker build -t eduvideo-flow-ai .
docker run -p 8000:8000 --env-file .env -v eduvideo-data:/app/data eduvideo-flow-ai
```

- Cần HTTPS và xác thực trước khi công bố Internet.
- SQLite + worker nội bộ thích hợp cho **một máy chủ/một worker**. Không chạy nhiều worker Uvicorn trên cùng DB với worker bộ nhớ hiện tại. Khi nhân rộng nhiều giáo viên, chuyển sang PostgreSQL + Redis/Celery và đăng nhập phân quyền theo giáo viên.
- Khi khởi động lại, dữ liệu dự án/cảnh/job đã lưu trong SQLite. Tác vụ Veo đang chạy có thể tiếp tục thăm dò bằng nút **Tiếp tục/Thử lại**; không tự gửi job mới khi `render_job` vẫn khớp dấu vân tay.
- `DATA_DIR` phải được gắn vào ổ persistent. `VEO_GCS_OUTPUT` tùy chọn nếu dùng Cloud Storage; tài khoản cần quyền đọc output.

## 3. Bản đồ logic 14 bước

| Bước | Xử lý | Bản ghi / điều kiện |
|---|---|---|
| 1 | Xác thực dữ liệu đầu vào | `config`, `ProjectID` |
| 2 | Gemini phân tích kiến thức | `analysis` |
| 3 | Chọn trọng tâm/cấu trúc | `blueprint` |
| 4 | Viết kịch bản hoàn chỉnh | `script` |
| 5 | Chia số cảnh = thời lượng/8 | `scenes`, `SCENE_001`... |
| 6 | Tạo/khóa Character/Environment/Voice/Audio Bible | `bible.lock_id` |
| 7 | Prompt ảnh cho từng Scene ID | `image_prompt` |
| 8 | Prompt video cho từng Scene ID | `video_prompt` |
| 9 | Nano Banana tạo ảnh 16:9 | tệp `image_vN.png` |
| 10 | Kiểm tra gói và gửi Veo | `render_job`, `render_fingerprint` |
| 11 | Theo dõi Veo tạo clip | `video_vN.mp4` |
| 12 | Kiểm tra clip có video và thời lượng hợp lệ | `VIDEO_READY` |
| 13 | Chỉ ghép khi tất cả cảnh đã chấp nhận | chuẩn hóa 1280×720, 24 FPS, AAC, nối clip |
| 14 | Kiểm tra MP4 và cung cấp xem/tải | `video.file` |

**Lưu ý:** app không tự coi video thành công chỉ vì dịch vụ trả mã job; chỉ được chấp nhận khi clip tải về và FFprobe đọc được. Video cuối bị khóa cho đến khi `accepted=true` ở tất cả các cảnh. Trên máy chủ, các tệp version cũ không bị xóa khi tạo lại.

## 4. Chỉnh sửa và tạo lại cảnh

- **Lưu chỉnh sửa nội dung**: nếu thay đổi bối cảnh/hành động, xóa tham chiếu hiện hành của prompt, ảnh và clip tương ứng ở cảnh đó. Dùng **Viết lại prompt AI** để sinh prompt mới cho riêng cảnh.
- **Chỉnh lời thoại**: xóa prompt video cũ và clip cũ của cảnh; giữ ảnh nếu bối cảnh/hình ảnh không đổi. Sinh lại prompt hoặc nhập prompt mới.
- **Tạo lại ảnh**: gọi Nano Banana cho riêng cảnh, video của cảnh bị vô hiệu hóa; các cảnh khác không đổi.
- **Tạo lại video**: dùng ảnh, prompt và Bible có hiệu lực của riêng cảnh; lưu một `render_job` riêng để khôi phục.
- **Ghép**: nếu 1 cảnh lỗi hoặc chưa được duyệt, nút bị khóa.
- **Tiến trình lưu trong DB**; lỗi từng bước lưu ở `project.errors`.

### Thiết kế an toàn cho lời thoại

Veo 3.1 nhận **prompt văn bản mô tả lời thoại**, không nhận một `WAV` thoại tùy ý theo yêu cầu image-to-video. Hệ thống mô tả câu thoại tiếng Việt trong prompt và kiểm tra kỹ thuật video. Việc âm thanh có phát âm chuẩn 100% **không thể được bảo đảm chỉ bằng câu lệnh**; đối với thuyết minh Hóa học, nên phát triển thêm một bộ TTS + đối chiếu phụ đề + thay audio ở hậu kỳ, có giáo viên duyệt.

### Thời lượng 8 giây và giữ nguyên lời nói

Bộ hậu kỳ **không cắt đầu/cuối cảnh** để ép 8 giây. Nó nhận các clip từ 7,2–8,8 giây rồi điều chỉnh nhẹ tốc độ để đạt 8 giây, giữ đủ âm thanh. Clip nằm ngoài biên sẽ bị từ chối và yêu cầu tạo lại. Cần đánh giá nghe nhìn sau ghép vì AI không luôn tuân thủ chính xác thời lượng/thoại.

### Phụ đề

Người dùng có lựa chọn tạo phụ đề, mặc định **tắt**. Khi giáo viên **chủ động bật**, app tạo tệp SRT theo lời thoại từng cảnh và dùng FFmpeg đốt phụ đề lên video cuối. Nếu bước này lỗi, dự án hiển thị lỗi xuất bản, không tuyên bố hoàn tất. Khi tắt, app không thêm phụ đề. Không yêu cầu Veo tự tạo chữ/phụ đề trong hình nhằm hạn chế lỗi chính tả và công thức Hóa học.

## 5. API có sẵn

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/api/health` | Kiểm tra cấu hình và trạng thái server |
| GET | `/api/projects` | Danh sách dự án |
| POST | `/api/projects` | Khởi tạo dự án và chạy bước 2–12 |
| GET | `/api/projects/{id}` | Xem toàn bộ trạng thái |
| PUT | `/api/projects/{id}` | Sửa đầu vào, vô hiệu hóa đầu ra phụ thuộc |
| POST | `/api/projects/{id}/resume` | Phục hồi quy trình |
| PATCH | `/api/projects/{id}/scenes/{scene}` | Sửa cảnh có kiểm soát |
| POST | `/api/projects/{id}/scenes/{scene}/regenerate-prompts` | Gemini viết lại prompt riêng cảnh |
| POST | `/api/projects/{id}/scenes/{scene}/regenerate-image` | Nano Banana tạo lại ảnh cảnh |
| POST | `/api/projects/{id}/scenes/{scene}/regenerate-video` | Veo tạo lại clip cảnh |
| POST | `/api/projects/{id}/scenes/{scene}/accept` | Duyệt cảnh khi có video hợp lệ |
| POST | `/api/projects/{id}/merge` | Ghép video và xuất MP4 |
| GET | `/api/projects/{id}/video` | Phát MP4 |
| GET | `/api/projects/{id}/download` | Tải MP4 |
| GET | `/api/projects/{id}/subtitles` | Tải SRT nếu đã bật phụ đề |
| POST | `/api/extract` | Trích xuất nội dung TXT/DOCX/PDF có chữ |

Truy cập tài liệu API tự sinh tại **http://localhost:8000/docs**.

## 6. Giới hạn hiện tại & kiểm nghiệm thực tế

- Mã nguồn được kiểm tra cú pháp và kiểm thử offline, **chưa kiểm chứng end-to-end với Gemini/Nano Banana/Veo trên tài khoản thực tế**, do môi trường bàn giao không có thông tin xác thực.
- Để đảm bảo lời thoại đúng hoàn toàn, cần thêm ASR đối soát/transcript và TTS sửa tiếng; các kiểm tra hiện tại chủ yếu xác minh cấu trúc và thời lượng. AI sinh hình ảnh/video vẫn có nguy cơ sai khoa học; giáo viên phải duyệt từng cảnh.
- Không có hệ thống tài khoản/role nhiều giáo viên. `APP_ACCESS_TOKEN` là lớp bảo vệ đơn giản cho một người dùng; triển khai cấp trường cần SSO/OAuth, phân quyền, giới hạn chi phí và lưu trữ.
- Không nên tải PDF scan vì chưa có OCR tích hợp.
- Không có cơ chế thu phí hoặc tính chi phí thực từ Google.
- Tạo video thực phụ thuộc quota, billing và quyền truy cập dịch vụ Veo GA; sai cấu hình sẽ trả lỗi hiển thị công khai trong dự án, không tạo tệp MP4 giả.

## 7. Tài liệu kỹ thuật gốc

- Gemini 3.1 Pro: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- Nano Banana Image: https://ai.google.dev/gemini-api/docs/image-generation
- Veo 3.1 GA: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/veo/3-1-generate
- Vertex image-to-video REST: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/generate-videos-from-an-image
- Model sunset: https://ai.google.dev/gemini-api/docs/deprecations

## 8. Bản vá V4.1 – Chỉnh sửa tối thiểu theo tài liệu kiểm soát lỗi

Bản V4.1 được phát triển từ V4.0 theo tiêu chí **không viết lại giao diện, không xóa các endpoint đang hoạt động, không render lại các Scene không bị ảnh hưởng**.

Các bổ sung đã có trong mã nguồn:

- `start_state`, `end_state`, `continuity_from`: truyền trạng thái kết thúc cảnh trước sang cảnh tiếp theo trong prompt ảnh/video. Nếu người dùng thay đổi trạng thái kết thúc cảnh N, cảnh N+1 được đánh dấu cần viết lại prompt và tạo lại media; các cảnh xa hơn được giữ nguyên nếu không có quan hệ phụ thuộc trực tiếp bị thay đổi.
- `dialogue_locked` và `dialogue_hash`: chỉ kịch bản/scenario editor mới được sửa thoại; prompt video dùng văn bản đã khóa. Đây là khóa dữ liệu chứ không bảo đảm tuyệt đối AI video đọc đúng âm thanh: vẫn cần người dùng nghe kiểm tra.
- `reference_lock`: endpoint `POST /api/projects/{id}/scenes/{scene}/accept-image`, nút **Khóa ảnh tham chiếu** trong giao diện. Reference ảnh được duyệt làm neo hình ảnh để Nano Banana tham khảo khi tạo lại cảnh; image file version cũ không bị xóa.
- Tạo prompt **chỉ cho Scene ID đang thiếu/không hợp lệ**, tránh đè prompt của các cảnh khác khi chạy Resume.
- Sửa riêng `title`: giữ nguyên scenes/clip/MP4. Sửa `subtitles`: chỉ cần xuất bản lại từ clip đã có, không phải gọi Gemini/Nano Banana/Veo.
- API dữ liệu dự án không tiết lộ đường dẫn tệp nội bộ trong `reference_lock`.

### Giới hạn chưa xác thực trực tiếp

- Chưa thử tạo ảnh/video bằng tài khoản Google Cloud thật; phải kiểm tra quota, kết nối, tiếng Việt, độ chính xác khoa học, và tính nhất quán hình ảnh trên dữ liệu thực.
- Neo hình ảnh `reference_lock` mặc định lấy **một ảnh đã được giáo viên chấp nhận**. Muốn quản lý riêng các reference cho nhiều nhân vật/bối cảnh cần phát triển tiếp cơ chế gán Character ID/Environment ID đến từng ảnh tham chiếu.
- Việc kế thừa `Start State`/`End State` là ràng buộc dữ liệu và câu lệnh, chưa phải kiểm chứng chất lượng bằng computer vision hay nhận dạng tiếng nói. Giáo viên vẫn phải duyệt cảnh.
- Chỉ cập nhật cảnh liền sau khi `End State` đổi; nếu thay đổi kéo theo dây chuyền nhiều cảnh, người dùng cần kiểm tra và chỉnh sửa bổ sung các cảnh chịu ảnh hưởng.

Chạy kiểm thử:

```bash
python -m pytest -q
node --check static/app.js
```


## 9. Bản sửa V4.1.1 – Điểm khởi chạy index.html và tác giả

- **Tệp chạy:** `/index.html` nằm ngay thư mục gốc. API phục vụ tại `/` và `/index.html`; không còn phụ thuộc đường dẫn `static/index.html` để khởi chạy ứng dụng.
- **Tác giả giải pháp:** Lê Bá Nhẫn – Trường THPT Hòn Đất. Tên tác giả được ghi trong tiêu đề HTML, phần đầu trang và chân trang.
- File `index.html` được đóng gói sẵn CSS và JavaScript giao diện; **các API thực vẫn bắt buộc cần backend**. Mở trực tiếp file để xem giao diện sẽ hiển thị thông báo về máy chủ và khóa thao tác tạo video.
- Có script `build_index.py` để đồng bộ giao diện từ các tệp nguồn `static/index.html`, `static/style.css`, `static/app.js`.
- Giữ nguyên API, workflow 14 bước, Scene ID và lưu trữ bản V4.1.
