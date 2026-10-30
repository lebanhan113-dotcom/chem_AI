from pathlib import Path
from html import escape
p=Path(__file__).parent
css=(p/'app.css').read_text()
gcss=(p/'game.css').read_text()
gjs=(p/'game.js').read_text().replace('</script>',r'<\/script>')
appjs=(p/'app.js').read_text().replace('</script>',r'<\/script>')
html='''<!DOCTYPE html>
<html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101b38"><meta name="author" content="Giáo viên: Lê Bá Nhẫn – Trường THPT Hòn Đất (An Giang)"><title>EDU GAME STUDIO AI – Xưởng trò chơi giáo dục</title><style>'''+css+'''</style></head>
<body><div class="shell"><aside class="sidebar" id="sidebar"><div class="brand"><span class="brand-mark">✦</span><div>EDU GAME<br><span style="font-weight:500;color:#aabaf9;font-size:12px">STUDIO AI</span></div></div><div class="nav-label">KHÔNG GIAN LÀM VIỆC</div>
<button class="nav-btn active" data-page="dashboard"><span class="nav-ico">▦</span> Tổng quan</button>
<button class="nav-btn" data-page="lessons"><span class="nav-ico">📚</span> Bài học của tôi</button>
<button class="nav-btn" data-page="editor"><span class="nav-ico">✎</span> Biên soạn bài học</button>
<button class="nav-btn" data-page="bank"><span class="nav-ico">🧠</span> Ngân hàng học tập</button>
<div class="nav-label">TRÒ CHƠI GIÁO DỤC</div>
<button class="nav-btn" data-page="library"><span class="nav-ico">🎮</span> Thư viện 8 game</button>
<button class="nav-btn" data-page="instances"><span class="nav-ico">▣</span> Game Instance</button>
<button class="nav-btn" data-page="settings"><span class="nav-ico">⚙</span> Cài đặt & sao lưu</button>
<div class="sidebar-foot"><b style="color:#eef1ff">V1.0 • 8 gameplay</b><br>Biến bài học thành trò chơi thật. Mỗi trò chơi có thể xuất ra một HTML độc lập.<br><br><span style="color:#8194bc">Giáo viên: Lê Bá Nhẫn – Trường THPT Hòn Đất (An Giang)</span></div></aside>
<div class="main"><header class="topbar"><div class="row"><button class="btn ghost mobile-menu" id="mobile-menu">☰</button><span class="breadcrumbs" id="page-breadcrumb">EDU GAME STUDIO / <strong>Tổng quan</strong></span></div><div class="top-actions"><span class="save-state" id="save-status"><span class="dot"></span> Đang khởi tạo...</span><span class="avatar">GV</span></div></header><div class="content" id="content"></div></div></div>
<div id="modal-root"></div><div id="toast" class="toast" style="display:none"></div>
<script id="game-style-source" type="text/plain">'''+gcss+'''</script>
<script id="game-runtime-source" type="text/plain">'''+gjs+'''</script>
<script>'''+appjs+'''</script></body></html>'''
(p/'index.html').write_text(html,encoding='utf8')
print('Wrote',len(html),'characters')
