# EDUPLAN AI 7.1 – WEBAPP HỌC SINH, DÀNH CHO GITHUB PAGES / VERCEL TĨNH

Tác giả giải pháp: **Lê Bá Nhẫn – Trường THPT Hòn Đất**.

## 1. Bản này phục vụ học sinh, đã loại bỏ khóa đáp án

Đây là bản web công khai **không chứa khóa đáp án**. Dữ liệu được lấy từ cùng 1.958 câu hỏi nguồn của EduPlan AI 7.0, sau khi loại bỏ các trường `answer`, `proposed_answer`, `correct`, `explanation`, `review_status`, v.v. Vì nhiều câu nguồn chưa được xác minh độc lập, học sinh được **tự giải – tự luyện – lưu lời làm**, nhưng hệ thống **không chấm tự động hoặc tiết lộ đáp án**. Muốn chấm bài online an toàn: dùng bản Next.js/Supabase (server giữ khóa đáp án), triển khai và kiểm thử thực tế.

## 2. Cấu trúc file

```
index.html         (HTML nhẹ, là điểm vào của website)
css/app.css        (giao diện responsive)
js/app.js          (logic lọc câu, tự luyện, phiếu tự học, lịch sử)
data/curriculum.json
 data/hoa10.json, hoa11.json, hoa12.json   (1958 câu KHÔNG có khóa đáp án)
assets/            (160 ảnh/tệp tư liệu dùng cho câu hỏi)
favicon.svg
README.md
```

Tất cả các file cần ở đúng cấu trúc. **Không được chỉ upload index.html** rồi bỏ thư mục `data`, `css`, `js`, `assets`.

## 3. Chạy trên máy để thử

Mở terminal ngay tại thư mục giải nén, chạy `python -m http.server 8000` rồi mở `http://localhost:8000/`. Khi chỉ mở `file://index.html`, một số trình duyệt chặn `fetch` đọc các tệp `.json` nên WebApp có thể báo lỗi tải dữ liệu; đây không phải lỗi thiếu câu.

## 4. Cách đưa lên GitHub Pages

1. Tạo repository mới chỉ dành cho **bộ học sinh an toàn này**, không chứa bất kỳ ZIP quản trị hay tệp data có đáp án nào.
2. Giải nén và upload toàn bộ thư mục con cùng `index.html` vào **gốc** repo bằng Git/GitHub Desktop hoặc tính năng upload files.
3. Vào **Settings → Pages → Build and deployment → Deploy from a branch**; chọn `main`, thư mục `/(root)`, lưu.
4. Sau khi GitHub Pages xuất bản, mở URL dự án dạng `https://<tên-tài-khoản>.github.io/<tên-repo>/`. Đây là ví dụ cấu trúc, không phải địa chỉ đã triển khai.
5. Kiểm tra Hóa 10, Hóa 11, Hóa 12 có tổng **809 + 473 + 676 = 1.958** câu. Kiểm tra một câu có hình, tạo 5 câu, lưu phiên rồi tải lại trang.

**Lưu ý:** Vì Pages là hosting tĩnh, dữ liệu học tập chỉ lưu trong `localStorage` trên trình duyệt từng học sinh; không thể thống kê lượt truy cập hay số học sinh toàn trường từ các tệp này. Không dùng bản này làm kiểm tra chính thức có điểm.

## 5. Cách đưa lên Vercel (static)

1. Tạo repo Git chứa chính bộ học sinh an toàn.
2. Trên Vercel chọn **Add New → Project → Import Git repository**.
3. Chọn framework **Other** hoặc **No Framework**; thiết lập thư mục gốc chứa `index.html` và để trống lệnh build/output nếu Vercel dùng chế độ static cho file ở gốc. Nếu cấu hình nền tảng yêu cầu Output Directory, chọn `.` (thư mục gốc).
4. Deploy, sau đó thử mở cả đường dẫn trang gốc và `/data/hoa10.json`.
5. Nếu trang trắng, kiểm tra Network/Console và chắc chắn các đường dẫn tương đối `./js/app.js`, `./data/hoa10.json`, `./assets/...` đều trả HTTP 200.

## 6. Tương tác đã có

- Tổng quan học tập; chọn bài/chương KNTT đầy đủ.
- Luyện từng câu, nhóm 5/10/15/20/30/40/50 câu, hoặc tất cả câu của phạm vi.
- Không trùng ID câu trong phiên; lưu câu trả lời, tự chuyển câu; đánh dấu cần ôn.
- Tự kiểm tra không chấm; phiếu học tập để in/PDF; báo cáo lịch sử trên thiết bị và xuất CSV.
- Công cụ tính M cho công thức đơn giản không ngoặc, C=n/V; mở ChatGPT ngoài ứng dụng; gọi tên ngẫu nhiên; nguồn tài liệu uy tín.

Chú ý: một số đối tượng Word Equation/MathType, hình và bảng nguồn chưa được số hóa đầy đủ; thầy/cô cần đối chiếu Word gốc trước khi dùng trong đề đánh giá chính thức.

## 7. Kiểm thử và giới hạn

- Đã kiểm tra cấu trúc 1.958 câu và 160 ảnh; bảo đảm data public không chứa các **trường** khóa đáp án.
- Kiểm thử thuật toán và luồng chọn bài, tạo nhóm 5 câu, không trùng, xác nhận, tự chuyển câu, lưu lịch sử trên mô phỏng JavaScript.
- Đã kiểm tra trong Chromium bằng cách nạp mã & data vào trang ở 1280 px và 390 px; không phát sinh lỗi JavaScript hoặc tràn ngang trong luồng thử.
- Môi trường hiện chặn mở `localhost` qua Chromium và chưa được triển khai lên URL GitHub Pages/Vercel thật. Chưa có kết quả kiểm thử từ hosting công khai hoặc lưu tập trung nhiều học sinh.

## 8. Đưa chấm điểm online chính thức

Không đưa khóa đáp án vào bất kỳ tệp JS/JSON nào gửi tới học sinh. Triển khai mã nguồn Next.js/Supabase riêng tư, chấm điểm tại máy chủ, xác nhận quyền truy cập và nhập dữ liệu đã duyệt. Đây là bước riêng, không thể có đủ chức năng bảo mật trên một site GitHub Pages thuần tĩnh.

---

# EduPlan AI 7.2 - interactive learning and real DOCX exports

This release builds on 7.1 **without altering any of the 1,958 original public questions**. It adds the question browser, direct interactive answer entry, quiz/exam composition, interactive worksheets, self-assessment, and native `.docx` exports from the browser.

## What changed

- Each of the question browser, practice, interactive exercises, self-check, mixed exam generation and worksheet creation reads the **same `data/hoa10.json`, `hoa11.json`, `hoa12.json`** files.
- Lesson/chapter/level filters apply to all activity types. The source question ID is retained in saved sessions; the student can revisit answers and export an individual session to Word.
- `js/docx-export.js` writes an actual OpenXML `.docx` ZIP in the browser, with Times New Roman text, A-D choices, answers provided by the student (when requested) and images present in the supported `assets/` paths. There is no CDN dependency or API key.
- Site is deployable to GitHub Pages or Vercel Static. Upload **all** files and folders, not just `index.html`. `index.html` is about 2 KB; questions/images stay split into multiple assets.
- Data continues to use the existing `eduplan71_public_state` localStorage key, preserving progress saved by the prior public version in the same browser and origin.

## Important limitations

- Public student data **intentionally contains no answer keys**. Thus all 1,958 public questions can be answered for learning purposes, but **there is no official automatic grading or validated answer reveal** in this static website. The `I understood / Need review` buttons are learner self-assessments, not chemistry correctness checks.
- Historic answers and progress are saved in localStorage **on one browser/device only**. School-wide statistics, login accounts, protected exam keys and centrally persisted scores require an authenticated backend such as the existing private Next.js + Supabase project, integrated and tested separately. Do not upload the private teacher answer bundle to public Pages.
- Word Equation/MathType/OLE objects were not all converted in earlier extraction. If a question contains an incomplete equation or picture, consult the original Word file before using it as an official assessment. DOCX output embeds supported PNG/JPEG resources from `assets/`; not every complex original Word table or OLE object can be reconstructed automatically.
- Generating shuffled Word variants changes **question order only**. Answers are never embedded in the public export. Automatic marking must remain a server-only feature.

## How to publish

**GitHub Pages:** push the unzipped project to the repository root, including `index.html`, `css/`, `js/`, `data/`, `assets/`, `favicon.svg` and `.nojekyll`; then configure Settings -> Pages -> Deploy from a branch -> `main` -> `/(root)`.

**Vercel:** import the repository with framework `Other` and static output at the project root. The supplied `vercel.json` configures security response headers. If the dashboard requires an output folder, use `.`. This is a static project and does not need `npm install` or any AI keys.

**Local testing:** from the folder run `python -m http.server 8000` and open `http://localhost:8000/`. Browser security may block loading JSON when the HTML is opened directly via `file://`.

**Student flow:** select a lesson -> question browser / practice / interactive exercises / test / worksheet -> submit each answer -> complete -> open Results -> optionally download DOCX. Student answers are not considered formally marked.

Author: Le Ba Nhan - Hon Dat High School.
