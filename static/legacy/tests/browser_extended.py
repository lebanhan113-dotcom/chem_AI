from pathlib import Path
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parents[1]
shim='<script>Object.defineProperty(window,"localStorage",{configurable:true,value:(()=>{const s={};return{getItem(k){return s[k]??null},setItem(k,v){s[k]=String(v)},removeItem(k){delete s[k]}}})()});</script>'
html=(p/'CHEM_MAP_TUTOR_AI_2_1_Offline.html').read_text(encoding='utf8').replace('</head>',shim+'</head>')
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
 page.set_content(html,wait_until='domcontentloaded')
 page.screenshot(path=str(p/'tests/mobile_home.png'),full_page=True)
 page.locator('.mobile-menu').click()
 assert 'open' in page.locator('#sidebar').get_attribute('class')
 page.locator('#nav-main [data-nav="practice"]').click()
 assert 'open' not in page.locator('#sidebar').get_attribute('class')
 page.locator('#practice-type').select_option('tf')
 page.locator('#practice-grade').select_option('12')
 page.locator('#practice-form button[type="submit"]').click()
 assert page.locator('.question-card').count()==2
 page.locator('input[name^="tf-"][value="T"]').first.check()
 page.locator('#quiz-form button[type="submit"]').click()
 data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
 assert len(data['attempts'])==1 and data['attempts'][0]['questions'][0]['type']=='tf'
 page.screenshot(path=str(p/'tests/mobile_result.png'),full_page=True)
 page.locator('[data-nav="learning"]').last.click()
 assert page.locator('[data-action="start-plan"]').count()==1
 page.locator('[data-action="start-plan"]').click()
 assert page.locator('#quiz-form').count()==1
 page.locator('#quiz-form button[type="submit"]').click()
 data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
 assert data['interventions'][-1]['afterAttemptId']!=None
 page.locator('#role-switch').select_option('student')
 page.locator('#content [data-nav="practice"]').last.click()
 page.locator('#practice-type').select_option('essay')
 page.locator('#practice-grade').select_option('11')
 page.locator('#practice-form button[type="submit"]').click()
 assert page.locator('.question-card').count()==1
 page.locator('textarea[name^="essay-"]').fill('Tôi viết lời giải thử nghiệm của học sinh.')
 page.locator('#quiz-form button[type="submit"]').click()
 data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
 assert data['attempts'][-1]['pendingCount']==1
 page.locator('#role-switch').select_option('teacher')
 page.locator('[data-action="teacher-tab"][data-id="grade"]').click()
 page.locator('input[id^="review-"]').fill('0.75')
 page.locator('[data-action="grade-essay"]').click()
 data=page.evaluate("JSON.parse(localStorage.getItem('chemmap2-local-v1'))")
 assert data['attempts'][-1]['pendingCount']==0
 assert data['attempts'][-1]['score']==7.5, data['attempts'][-1]['score']
 assert not errors, errors
 print('Extended E2E PASS: responsive menu, true/false, personalized intervention with before-after link, essay pending, teacher grading score')
 b.close()
