"""Browser UI interaction smoke for new study flow with mocked transport; API tested separately."""
from pathlib import Path
import os,json,tempfile,sys,base64
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mkdtemp()+'/studyui34.sqlite'
os.environ['SESSION_SECRET']='j'*64
sys.path.insert(0,str(ROOT));from server import APP
client=TestClient(APP)
curr=client.get('/api/curriculum').json()
cat=client.get('/api/study/catalog',params={'grade':11}).json()
pool=client.get('/api/study/pool',params={'grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':'11-4','kind':'mcq'}).json()
q=pool['questions'][0]
answer=client.post('/api/study/check',json={'id':q['id'],'answer':1}).json()
html=(ROOT/'index.html').read_text().replace('<link rel="stylesheet" href="assets/ui.css">','').replace('<script src="assets/app3.js" defer></script>','')
css=(ROOT/'static/ui.css').read_text();code=(ROOT/'static/app3.js').read_text()
mock={'curr':curr,'cat':cat,'pool':pool,'answer':answer}
js='''(function(){const D=window.STUDY34;window.fetch=async function(url){let u=String(url);let x={};if(u.includes('/curriculum'))x=D.curr;else if(u.includes('/study/catalog'))x=D.cat;else if(u.includes('/study/pool'))x=D.pool;else if(u.includes('/study/check'))x=D.answer;else if(u.includes('/visit'))x={recorded:true};else if(u.includes('/exams'))x=[];return new Response(JSON.stringify(x),{status:200,headers:{'content-type':'application/json'}})}})();'''
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for width,height,mobile in [(1440,850,False),(390,844,True)]:
  ctx=browser.new_context(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile)
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  raw=base64.b64encode(json.dumps(mock,ensure_ascii=False).encode()).decode()
  content=html.replace('</body>',f'<style>{css}</style><script>const fakeStore=()=>{{const m=new Map();return {{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}}}};Object.defineProperty(window,"sessionStorage",{{configurable:true,value:fakeStore()}});Object.defineProperty(window,"localStorage",{{configurable:true,value:fakeStore()}});window.STUDY34=JSON.parse(decodeURIComponent(escape(atob("{raw}"))));{js}</script><script>{code}</script></body>')
  page.set_content(content,wait_until='domcontentloaded');page.locator('.hero').wait_for(timeout=8000)
  if mobile:page.locator('#menu').click()
  page.locator('[data-view="curriculum"]').first.click();page.get_by_text('Chương 2. Nitrogen - Sulfur').wait_for(timeout=9000)
  assert page.locator('.topic-chapter').count()==6
  lesson=page.locator('[data-lesson-open="11-4"]');lesson.click()
  page.locator('#beginStudy').wait_for(timeout=5000)
  assert page.locator('#selLesson').input_value()=='11-4'
  page.locator('#beginStudy').click()
  page.locator('[data-study-option]').first.wait_for(timeout=5000)
  page.locator('[data-study-option="1"]').click();page.locator('#studyCheck').click()
  page.locator('.study-feedback').wait_for(timeout=5000)
  assert page.locator('.study-feedback').inner_text().find('Đáp án chuẩn')>=0
  page.screenshot(path=str(ROOT/f'tests/ui34_study_{"mobile" if mobile else "desktop"}.png'),full_page=True)
  assert not errors,errors
  ctx.close()
 browser.close()
print('UI 3.4 lesson navigation and answer feedback PASSED (desktop/mobile).')
