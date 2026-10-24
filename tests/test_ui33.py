"""UI 3.3 browser smoke with local assets and mocked fetch (no localhost browser navigation)."""
from pathlib import Path
import json, tempfile, os, sys, base64
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mkdtemp()+'/ui33.sqlite'
os.environ['ADMIN_PASSWORD']='test_33_teacher_only'
os.environ['SESSION_SECRET']='b'*64
sys.path.insert(0,str(ROOT))
from server import APP
client=TestClient(APP)
assert client.get('/index.html').status_code==200
assert client.get('/').text==client.get('/index.html').text
teacher=client.post('/api/auth/teacher',json={'password':os.environ['ADMIN_PASSWORD']}).json()
th={'Authorization':'Bearer '+teacher['token']}
cl=client.post('/api/classes',headers=th,json={'name':'11A Test','grade':11}).json()
exam=client.post('/api/exams/build',headers=th,json={'grade':11,'chapter':'Nitrogen - Sulfur','title':'De UI 3.3'}).json()
student=client.post('/api/auth/join',json={'code':cl['code'],'name':'HS demo','pin':'pass1234'}).json()
st={'Authorization':'Bearer '+student['token']}
exam_detail=client.get('/api/exams/'+exam['id'],headers=st).json()
source_summary=client.get('/api/sources/summary',headers=th).json()
sources=client.get('/api/sources/questions',params={'grade':12,'chapter':'Pin điện và điện phân','status':'import-pending','limit':15},headers=th).json()
assert sources['total']==32
curr=client.get('/api/curriculum').json()
html=(ROOT/'index.html').read_text(encoding='utf-8').replace('<link rel="stylesheet" href="assets/ui.css">','').replace('<script src="assets/app3.js" defer></script>','')
css=(ROOT/'static/ui.css').read_text(encoding='utf-8')
code=(ROOT/'static/app3.js').read_text(encoding='utf-8')
mock={'curriculum':curr,'teacher':teacher,'student':student,'exam':exam_detail,'exam_list':[{'id':exam['id'],'title':exam['title'],'grade':11,'chapter':'Nitrogen - Sulfur','category':'Giữa kì 1'}],'summary':source_summary,'sources':sources}
mockjs=r'''(function(){
  const S = window.CHEM_MOCK;
  window.fetch = async function(url, opts){
   const u=String(url);let result={};let code=200;
   if(u.includes('/curriculum'))result=S.curriculum;
   else if(u.includes('/auth/teacher'))result=S.teacher;
   else if(u.includes('/auth/join'))result=S.student;
   else if(u.includes('/sources/summary'))result=S.summary;
   else if(u.includes('/sources/questions?'))result=S.sources;
   else if(u.includes('/questions/counts'))result={total:0,by_type:{},by_level:{}};
   else if(u.includes('/questions/drafts'))result=[];
   else if(u.includes('/classes'))result=[];
   else if(u.includes('/attempts/mine'))result=[];
   else if(u.includes('/exams/'+S.exam.id))result=S.exam;
   else if(u.endsWith('/exams'))result=S.exam_list;
   else if(u.includes('/references'))result=[];
   else if(u.includes('/visit'))result={ok:true};
   else result={};
   return new Response(JSON.stringify(result),{status:code,headers:{'content-type':'application/json'}});
  };
})();'''
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 def new_page(width,height,mobile=False):
  context=browser.new_context(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile)
  page=context.new_page();errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
  raw=base64.b64encode(json.dumps(mock,ensure_ascii=False).encode()).decode()
  content=html.replace('</body>',f'<style>{css}</style><script>window.CHEM_MOCK=JSON.parse(decodeURIComponent(escape(atob(\"{raw}\"))));const fakeStore=()=>{{const m=new Map();return {{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}}}};Object.defineProperty(window,"sessionStorage",{{configurable:true,value:fakeStore()}});Object.defineProperty(window,"localStorage",{{configurable:true,value:fakeStore()}});{mockjs}</script><script>{code}</script></body>')
  page.set_content(content,wait_until='domcontentloaded')
  page.locator('.hero').wait_for(timeout=5000)
  return page,errs,context
 page,errs,ctx=new_page(1440,900)
 assert page.locator('.nav-group').count()>=3
 assert page.get_by_text('755',exact=True).count()==1
 assert page.locator('.navitem[data-view="sources"]').count()==0
 page.screenshot(path=str(ROOT/'tests/ui33_desktop.png'),full_page=True)
 page.locator('#adminPass').fill(os.environ['ADMIN_PASSWORD'])
 page.locator('#teacherLogin').click()
 page.locator('.navitem[data-view="sources"]').wait_for(timeout=5000)
 page.locator('.navitem[data-view="sources"]').click()
 page.locator('#srcGrade').select_option('12')
 page.locator('#srcChapter').select_option(label='Chương 5: Pin điện và điện phân')
 page.locator('#srcStatus').select_option('import-pending')
 page.get_by_text('32 câu trong bộ lọc').wait_for(timeout=5000)
 page.screenshot(path=str(ROOT/'tests/ui33_sources.png'),full_page=True)
 page.locator('#logout').click()
 page.locator('#joinCode').fill(cl['code']);page.locator('#joinName').fill('HS demo');page.locator('#joinPin').fill('pass1234')
 page.locator('#joinBtn').click();page.locator('.navitem[data-view="results"]').wait_for(timeout=5000)
 page.locator('.navitem[data-view="exams"]').click()
 page.locator('[data-exam="'+exam['id']+'"]').click()
 page.locator('.question').wait_for(timeout=5000)
 assert page.locator('.question').count()==1
 page.locator('button[data-option="0"]').first.click()
 page.get_by_text('Câu 2/32').wait_for(timeout=3000)
 page.locator('.quiz-index summary').click()
 assert page.locator('button[data-jump]').count()==32
 page.locator('button[data-jump="0"]').click()
 page.get_by_text('Câu 1/32').wait_for(timeout=3000)
 page.once('dialog',lambda dialog:dialog.dismiss())
 page.locator('.navitem[data-view="curriculum"]').click()
 assert page.get_by_text('Câu 1/32').is_visible()
 page.screenshot(path=str(ROOT/'tests/ui33_quiz.png'),full_page=True)
 assert not errs,errs
 m,me,mc=new_page(390,844,True)
 assert m.locator('#sidebar').bounding_box()['x'] < 0
 m.locator('#menu').click()
 m.wait_for_timeout(350)
 assert m.locator('#sidebar').bounding_box()['x'] >= -1 and m.locator('#mobileBackdrop').is_visible()
 m.locator('#mobileBackdrop').click(position={'x':375,'y':350})
 m.wait_for_timeout(350)
 assert m.locator('#sidebar').bounding_box()['x'] < 0
 m.screenshot(path=str(ROOT/'tests/ui33_mobile.png'),full_page=True)
 assert not me,me
 ctx.close();mc.close();browser.close()
print('UI smoke PASS: navigation, counts, index route, chapter/status filtering, student exam, jump, exit warning, mobile drawer')
