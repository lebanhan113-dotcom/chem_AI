from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import threading
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(("127.0.0.1",0),partial(SimpleHTTPRequestHandler,directory=str(p)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as w:
    browser=w.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-web-security'])
    page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('dialog',lambda d: d.accept())
    html=(p/'CHEM_MAP_TUTOR_AI_2_1_Offline.html').read_text(encoding='utf-8')
    shim='<script>Object.defineProperty(window,"localStorage",{configurable:true,value:(()=>{const s={};return{getItem(k){return s[k]??null},setItem(k,v){s[k]=String(v)},removeItem(k){delete s[k]}}})()});</script>'
    page.set_content(html.replace('</head>',shim+'</head>'),wait_until='domcontentloaded')
    page.wait_for_timeout(400)
    assert page.get_by_text('Chào mừng đến với CHEM-MAP').count()>0,'Home is not rendered'
    page.screenshot(path=str(p/'tests/home.png'),full_page=True)
    page.locator('[data-nav="practice"]').first.click()
    assert page.get_by_text('Thiết lập bài luyện').count()>0
    page.locator('#practice-grade').select_option('10')
    page.locator('#practice-type').select_option('mcq')
    page.locator('#practice-count').select_option('5')
    page.locator('#practice-form button[type="submit"]').click()
    assert page.get_by_text('Phiên làm bài đang hoạt động').count()>0
    page.locator('.question-card input[type="radio"]').first.check()
    page.screenshot(path=str(p/'tests/quiz.png'),full_page=True)
    page.locator('#quiz-form button[type="submit"]').click()
    page.wait_for_timeout(250)
    assert page.get_by_text('Đáp án, lời giải').count()>0
    assert page.get_by_text('HƯỚNG DẪN GIẢI').count()>0
    assert page.get_by_text('Điểm bài làm').count()>0
    page.screenshot(path=str(p/'tests/results.png'),full_page=True)
    data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
    assert len(data['attempts'])==1 and len(data['attempts'][0]['questions'])==5
    assert data['attempts'][0]['score']>=0 and data['attempts'][0]['score']<=10
    page.locator('#role-switch').select_option('teacher')
    page.wait_for_timeout(100)
    assert page.get_by_text('Không gian giáo viên').count()>0
    page.locator('[data-action="teacher-tab"][data-id="author"]').click()
    assert page.locator('#author-form').count()==1
    page.locator('#author-form [name="skill"]').fill('Bảo toàn khối lượng')
    page.locator('#author-form [name="stem"]').fill('Trong bài thử nghiệm, giá trị 2+2 bằng mấy?')
    for i,v in enumerate(['1','2','3','4']):page.locator(f'#author-form [name="opt{i}"]').fill(v)
    page.locator('#author-form [name="correctMcq"]').select_option('3')
    page.locator('#author-form [name="explanation"]').fill('Theo phép cộng: 2 + 2 = 4.')
    page.locator('#author-form button[type="submit"]').click()
    data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
    assert len(data['customQuestions'])==1 and data['customQuestions'][0]['approved']==False
    page.locator('[data-action="approve-question"]').click()
    data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
    assert data['customQuestions'][0]['approved']==True
    page.locator('[data-nav="exams"]').click()
    page.locator('#assignment-form [name="title"]').fill('Kiểm tra demo')
    page.locator('#assignment-grade').select_option('12')
    page.locator('#assignment-type').select_option('mcq')
    page.locator('#assignment-form button[type="submit"]').click()
    assert page.get_by_text('Kiểm tra demo').count()>0
    page.locator('[data-nav="reports"]').click()
    assert page.get_by_text('Báo cáo thống kê').count()>0
    page.locator('[data-nav="admin"]').click()
    assert page.get_by_text('Sao lưu và phục hồi').count()>0
    page.screenshot(path=str(p/'tests/system.png'),full_page=True)
    print('Browser E2E PASS: landing, practice, submit, result, teacher authoring, assignment, reports, system')
    print('Console/page errors:',errors)
    assert not errors, errors
    browser.close()
server.shutdown()
