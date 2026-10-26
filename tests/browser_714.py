from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height in [(1440,900),(390,844)]:
  page=b.new_page(viewport={'width':width,'height':height},accept_downloads=True)
  errs=[];page.on('pageerror',lambda e: errs.append(str(e)))
  page.goto('http://127.0.0.1:8974/index.html',wait_until='domcontentloaded',timeout=25000)
  page.wait_for_function('typeof bank!=="undefined" && bank.length===322',timeout=40000)
  page.locator('.bankupdate-feature714 button').first.click();page.wait_for_timeout(450)
  assert 'Cập nhật' in page.locator('#main').inner_text()
  assert page.locator('.feature710').count()>=18
  assert page.locator('.course-card713').count()==21
  page.screenshot(path=f'/mnt/data/EduPlan_AI_7_14_Giao_Dien_{width}px.png',full_page=False)
  print('UI',width, 'questions',page.evaluate('bank.length'), 'tiles',page.locator('.feature710').count(),'chapters',page.locator('.course-card713').count(), 'overflow',page.evaluate('document.documentElement.scrollWidth>innerWidth'),'js_err',errs[:2])
  page.close()
 # Teacher importer
 page=b.new_page(viewport={'width':1400,'height':900})
 errs=[];page.on('pageerror',lambda e: errs.append(str(e)))
 page.goto('http://127.0.0.1:8974/teacher-tools/index.html',wait_until='domcontentloaded',timeout=25000)
 page.wait_for_function('document.getElementById("summary").textContent.includes("câu đã nhập")',timeout=40000)
 sample=Path('/mnt/data/2026 - 2027. 11.1 Can bang hoa hoc. TTB  - Dap an - DE1.docx')
 assert sample.exists()
 page.locator('#source-files').set_input_files(str(sample))
 page.wait_for_function('document.querySelector("#summary").textContent.match(/[1-9][0-9]* câu đã nhập/)',timeout=30000)
 print('DOCX import:',page.locator('#summary').inner_text(),'listed:',page.locator('.question-item').count(),'js_err',errs[:3])
 assert page.locator('.question-item').count()>0
 page.locator('.question-item').first.click()
 assert page.locator('#editor').is_visible()
 assert page.locator('#problems').inner_text()
 page.screenshot(path='/mnt/data/EduPlan_AI_7_14_Nhap_Nguon.png',full_page=False)
 b.close()
