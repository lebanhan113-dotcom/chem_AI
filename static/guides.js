"use strict";
const HELP_GUIDES = [
  {
    "id": "type-00",
    "kind": "type",
    "title": "Khởi động bài học",
    "subtitle": "Gây tò mò trong những phút đầu tiết học",
    "steps": [
      "Chọn Khởi động bài học; nhập câu hỏi hoặc tình huống gây tò mò, chưa tiết lộ đáp án.",
      "Chọn 8–24 giây, phong cách phù hợp; tạo video rồi kiểm tra câu hỏi mở đầu và hình ảnh.",
      "Phát video ở đầu tiết; tạm dừng để học sinh dự đoán, sau đó dẫn vào chủ đề."
    ],
    "note": "Giữ câu hỏi ngắn, tránh tiết lộ kết luận ngay trên màn hình.",
    "video": "01_khoi-ong-bai-hoc.mp4",
    "typeValue": "Khởi động bài học"
  },
  {
    "id": "type-01",
    "kind": "type",
    "title": "Giới thiệu bài học",
    "subtitle": "Định hướng cho học sinh về nội dung sắp học",
    "steps": [
      "Nhập mục tiêu, tình huống và khái niệm nền của bài mới.",
      "Chọn Giới thiệu bài học, 16–32 giây; duyệt mạch mở đầu – mục tiêu – chủ đề.",
      "Phát trước khi vào bài; yêu cầu học sinh nêu điều mình sẽ tìm hiểu."
    ],
    "note": "Chỉ nêu các mục tiêu chính, không nhồi quá nhiều kiến thức.",
    "video": "02_gioi-thieu-bai-hoc.mp4",
    "typeValue": "Giới thiệu bài học"
  },
  {
    "id": "type-02",
    "kind": "type",
    "title": "Đặt vấn đề",
    "subtitle": "Tạo mâu thuẫn nhận thức để khơi gợi thảo luận",
    "steps": [
      "Nhập một vấn đề thực tế hoặc hiện tượng cần giải thích; nêu rõ câu hỏi trung tâm.",
      "Chọn Đặt vấn đề; kiểm tra cảnh cuối phải mở ra câu hỏi chưa được giải ngay.",
      "Cho học sinh thảo luận cặp đôi hoặc nhóm trước khi khám phá lời giải."
    ],
    "note": "Tình huống phải có cơ sở khoa học, tránh dữ kiện gây hiểu lầm.",
    "video": "03_at-van-e.mp4",
    "typeValue": "Đặt vấn đề"
  },
  {
    "id": "type-03",
    "kind": "type",
    "title": "Giải thích khái niệm",
    "subtitle": "Biến khái niệm trừu tượng thành hình ảnh dễ hiểu",
    "steps": [
      "Nhập định nghĩa chính xác, ví dụ và dấu hiệu nhận biết.",
      "Chọn Giải thích khái niệm; kiểm tra mô phỏng, thuật ngữ và lời thoại.",
      "Phát video; yêu cầu học sinh tự diễn đạt khái niệm và đưa ví dụ mới."
    ],
    "note": "Hiển thị công thức hoặc ký hiệu khoa học bằng lớp chữ chính xác.",
    "video": "04_giai-thich-khai-niem.mp4",
    "typeValue": "Giải thích khái niệm"
  },
  {
    "id": "type-04",
    "kind": "type",
    "title": "Trình bày kiến thức",
    "subtitle": "Tóm tắt các ý cốt lõi theo thứ tự logic",
    "steps": [
      "Nhập các luận điểm hoặc quy tắc theo thứ tự và ví dụ minh họa.",
      "Chọn Trình bày kiến thức; dùng 24–64 giây, duyệt từng cảnh và ý chuyển tiếp.",
      "Phát theo đoạn; tạm dừng để học sinh lập sơ đồ hoặc ghi ý chính."
    ],
    "note": "Mỗi cảnh tập trung một ý kiến thức, không vượt thời lượng lời thoại.",
    "video": "05_trinh-bay-kien-thuc.mp4",
    "typeValue": "Trình bày kiến thức"
  },
  {
    "id": "type-05",
    "kind": "type",
    "title": "Minh họa tình huống",
    "subtitle": "Cho học sinh quan sát một tình huống cụ thể",
    "steps": [
      "Nêu nhân vật, hoàn cảnh, quyết định và hậu quả trong tình huống.",
      "Chọn Minh họa tình huống; kiểm tra Character/Environment Bible và hội thoại.",
      "Phát video; hỏi học sinh nhân vật nên xử lý thế nào và vì sao."
    ],
    "note": "Giữ nhân vật nhất quán, tránh tình huống định kiến hoặc phản cảm.",
    "video": "06_minh-hoa-tinh-huong.mp4",
    "typeValue": "Minh họa tình huống"
  },
  {
    "id": "type-06",
    "kind": "type",
    "title": "Kể chuyện giáo dục",
    "subtitle": "Dạy học thông qua câu chuyện có thông điệp",
    "steps": [
      "Nhập bối cảnh, nhân vật, xung đột, diễn biến và bài học rút ra.",
      "Chọn Kể chuyện giáo dục; duyệt lời thoại tự nhiên và tính liên tục các cảnh.",
      "Phát toàn bộ truyện; yêu cầu học sinh phân tích hành động và thông điệp."
    ],
    "note": "Nội dung phù hợp độ tuổi; nhân vật, trang phục không thay đổi tùy tiện.",
    "video": "07_ke-chuyen-giao-duc.mp4",
    "typeValue": "Kể chuyện giáo dục"
  },
  {
    "id": "type-07",
    "kind": "type",
    "title": "Mô phỏng hiện tượng",
    "subtitle": "Quan sát các quá trình khó hoặc nguy hiểm khi làm thật",
    "steps": [
      "Nhập hiện tượng, điều kiện, diễn biến và kết luận khoa học có căn cứ.",
      "Chọn Mô phỏng hiện tượng, phong cách Khoa học – mô phỏng; kiểm tra màu, chất, động tác.",
      "Phát chậm hoặc theo cảnh; yêu cầu học sinh mô tả quan sát rồi giải thích."
    ],
    "note": "Mô phỏng phải đúng khoa học; không dùng AI thay thế hướng dẫn an toàn thí nghiệm.",
    "video": "08_mo-phong-hien-tuong.mp4",
    "typeValue": "Mô phỏng hiện tượng"
  },
  {
    "id": "type-08",
    "kind": "type",
    "title": "Câu hỏi khám phá",
    "subtitle": "Mở đầu chu trình tìm tòi và dự đoán",
    "steps": [
      "Nhập câu hỏi mở, dữ kiện và những giả thuyết học sinh có thể nêu.",
      "Chọn Câu hỏi khám phá; kiểm tra video đưa đủ dữ kiện nhưng không làm lộ đáp án.",
      "Phát video và dừng ở câu hỏi; cho học sinh ghi dự đoán, chia sẻ chứng cứ."
    ],
    "note": "Ưu tiên câu hỏi có thể giải thích bằng kiến thức của lớp đã chọn.",
    "video": "09_cau-hoi-kham-pha.mp4",
    "typeValue": "Câu hỏi khám phá"
  },
  {
    "id": "type-09",
    "kind": "type",
    "title": "Luyện tập",
    "subtitle": "Giúp học sinh áp dụng kiến thức vừa học",
    "steps": [
      "Nhập câu hỏi, yêu cầu thao tác và đáp án kèm giải thích để giáo viên kiểm duyệt.",
      "Chọn Luyện tập; để khoảng dừng hợp lý sau khi nêu đề; kiểm tra kết quả.",
      "Phát câu hỏi, tạm dừng cho học sinh làm rồi mới hiện phần giải thích."
    ],
    "note": "Không hiển thị đáp án quá sớm; đáp án cần được giáo viên kiểm tra.",
    "video": "10_luyen-tap.mp4",
    "typeValue": "Luyện tập"
  },
  {
    "id": "type-10",
    "kind": "type",
    "title": "Vận dụng",
    "subtitle": "Kết nối kiến thức với tình huống thực tiễn",
    "steps": [
      "Nhập một nhiệm vụ thực tiễn, dữ liệu liên quan và yêu cầu giải quyết.",
      "Chọn Vận dụng; dùng 24–64 giây và kiểm tra tính hợp lý của dữ kiện.",
      "Phát tình huống; giao học sinh thảo luận phương án và giải thích lựa chọn."
    ],
    "note": "Gắn thực tế, tránh tự bịa dữ kiện sản xuất hoặc kết quả nghiên cứu.",
    "video": "11_van-dung.mp4",
    "typeValue": "Vận dụng"
  },
  {
    "id": "type-11",
    "kind": "type",
    "title": "Tổng kết bài học",
    "subtitle": "Hệ thống hóa kiến thức cuối tiết",
    "steps": [
      "Nhập các kiến thức trọng tâm, liên hệ và một câu hỏi tự kiểm tra.",
      "Chọn Tổng kết bài học; dùng 16–40 giây, trình bày 2–4 ý chính.",
      "Phát cuối tiết; học sinh tự nhắc lại 3 ý và ghi điều còn thắc mắc."
    ],
    "note": "Ngắn, chính xác, ưu tiên liên kết giữa các khái niệm.",
    "video": "12_tong-ket-bai-hoc.mp4",
    "typeValue": "Tổng kết bài học"
  },
  {
    "id": "stage-12",
    "kind": "stage",
    "title": "Phân tích bài học",
    "subtitle": "Đọc và kiểm tra bản phân tích do Gemini tạo",
    "steps": [
      "Mở Sản xuất sau khi nhấn Tạo video; xem tiến trình Phân tích bài học.",
      "Đọc mục tiêu, kiến thức trọng tâm và cảnh báo; đối chiếu với tài liệu gốc.",
      "Nếu có lỗi kiến thức, sửa nội dung đầu vào rồi chạy lại phần phụ thuộc."
    ],
    "note": "Không tiếp tục biên kịch nếu đầu vào chưa được xác thực.",
    "video": "13_phan-tich-bai-hoc.mp4",
    "typeValue": null
  },
  {
    "id": "stage-13",
    "kind": "stage",
    "title": "Tạo kịch bản",
    "subtitle": "Duyệt mạch nội dung, lời thoại và thời lượng",
    "steps": [
      "Mở Sản xuất → Kịch bản tổng thể sau khi phân tích hoàn thành.",
      "Kiểm tra mở đầu, diễn biến, kết thúc; lời thoại đúng chuyên môn và thời lượng.",
      "Nếu kịch bản chưa đạt, chỉnh nguồn hoặc kịch bản rồi tạo lại phần bị ảnh hưởng."
    ],
    "note": "Không sửa sai kịch bản bằng cách sửa riêng prompt video.",
    "video": "14_tao-kich-ban.mp4",
    "typeValue": null
  },
  {
    "id": "stage-14",
    "kind": "stage",
    "title": "Chia cảnh",
    "subtitle": "Xem số cảnh, nhịp chuyển và Bible nhất quán",
    "steps": [
      "Xem số cảnh bằng thời lượng tổng chia 8 giây; xem mục tiêu mỗi cảnh.",
      "Đối chiếu Character Bible, Environment Bible, Start State và End State.",
      "Chỉ chấp nhận dữ liệu khi cảnh tiếp theo nối logic và nhân vật không đổi."
    ],
    "note": "Thay đổi Bible cần kiểm tra lại các cảnh đang sử dụng.",
    "video": "15_chia-canh.mp4",
    "typeValue": null
  },
  {
    "id": "stage-15",
    "kind": "stage",
    "title": "Tạo câu lệnh",
    "subtitle": "Kiểm tra prompt ảnh và prompt video cho đúng Scene ID",
    "steps": [
      "Mở Các cảnh; xem Image Prompt và Video Prompt của từng cảnh.",
      "Đối chiếu cảnh, nhân vật, đạo cụ, bối cảnh, lời thoại và góc máy.",
      "Nếu sửa prompt, lưu lại; tạo lại chỉ những tài nguyên phụ thuộc của cảnh đó."
    ],
    "note": "Không để lời thoại hoặc ảnh tham chiếu thuộc Scene khác.",
    "video": "16_tao-cau-lenh.mp4",
    "typeValue": null
  },
  {
    "id": "stage-16",
    "kind": "stage",
    "title": "Tạo hình ảnh",
    "subtitle": "Duyệt hình ảnh tham chiếu từ Nano Banana",
    "steps": [
      "Trong Các cảnh, xem ảnh do Nano Banana tạo sau khi có prompt hợp lệ.",
      "Kiểm tra 16:9, nhân vật, trang phục, phông nền và tính khoa học.",
      "Nếu ảnh sai, chọn Tạo lại hình ảnh riêng cảnh; chấp nhận ảnh đúng."
    ],
    "note": "Tạo lại ảnh có thể làm video cũ của cảnh hết hiệu lực.",
    "video": "17_tao-hinh-anh.mp4",
    "typeValue": null
  },
  {
    "id": "stage-17",
    "kind": "stage",
    "title": "Tạo video",
    "subtitle": "Duyệt clip Veo 3.1 và phát hiện lỗi theo cảnh",
    "steps": [
      "Mở Các cảnh, theo dõi trạng thái tạo video của từng Scene ID.",
      "Xem clip, kiểm tra hành động, âm thanh, lời thoại, điểm đầu và cuối.",
      "Chọn Tạo lại video nếu chưa đạt; nhấn Chấp nhận cảnh khi clip đã hợp lệ."
    ],
    "note": "Không chấp nhận clip chỉ vì đã có mã tác vụ render.",
    "video": "18_tao-video.mp4",
    "typeValue": null
  },
  {
    "id": "stage-18",
    "kind": "stage",
    "title": "Ghép video",
    "subtitle": "Xác nhận mọi cảnh trước khi xuất bản",
    "steps": [
      "Kiểm tra tất cả cảnh đã có clip hợp lệ và được chấp nhận.",
      "Nhấn Ghép video → Xuất MP4; theo dõi trạng thái ghép và âm thanh.",
      "Nếu ghép lỗi, thử lại bước ghép từ clip đã có, không tạo lại toàn bộ cảnh."
    ],
    "note": "Nút ghép phải khóa khi thiếu dù chỉ một cảnh được chấp nhận.",
    "video": "19_ghep-video.mp4",
    "typeValue": null
  },
  {
    "id": "stage-19",
    "kind": "stage",
    "title": "Hoàn thành",
    "subtitle": "Xem, tải và đưa sản phẩm vào hoạt động dạy học",
    "steps": [
      "Mở Video cuối sau khi xuất MP4 thành công.",
      "Phát thử, kiểm tra tiếng, hình, phụ đề tùy chọn và thời lượng.",
      "Nhấn Tải MP4; lưu vào giáo án, trình chiếu hoặc kho học liệu của trường."
    ],
    "note": "Nếu sửa một cảnh, giữ lại bản MP4 cũ trong lịch sử phiên bản.",
    "video": "20_hoan-thanh.mp4",
    "typeValue": null
  },
  {
    "id": "overview-20",
    "kind": "overview",
    "title": "Tổng quan ứng dụng",
    "subtitle": "Từ nội dung bài học đến video MP4 có thể tải về",
    "steps": [
      "Vào Tạo video, chọn môn, lớp, tên bài, nhập nội dung và cấu hình video.",
      "Nhấn Tạo video; theo dõi quy trình, duyệt kịch bản, ảnh và clip từng cảnh.",
      "Chấp nhận các cảnh đúng, chọn Ghép video và tải sản phẩm MP4."
    ],
    "note": "Cần backend và quyền truy cập AI phù hợp để sản xuất video thật.",
    "video": "21_tong-quan-ung-dung.mp4",
    "typeValue": null
  }
];
