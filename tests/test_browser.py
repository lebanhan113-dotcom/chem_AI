from pathlib import Path
import subprocess,time,signal
from playwright.sync_api import sync_playwright
path=Path(__file__).resolve().parent.parent
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 page=b.new_page(viewport={"width":1320,"height":900},accept_downloads=True)
 errors=[]
 page.on('pageerror',lambda e: errors.append(str(e)))
 from bs4 import BeautifulSoup
 soup=BeautifulSoup((path/'web/index.html').read_text(),'html.parser')
 pre=soup.new_tag('script');pre.string="var __kv={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__kv[k]??null,setItem:(k,v)=>{__kv[k]=v},removeItem:k=>delete __kv[k]}})";soup.head.append(pre)
 for scr in list(soup.find_all('script')):
  if scr.has_attr('src'):
   filename=path/'web'/scr['src']
   if 'mathjax' in str(filename):scr.decompose();continue
   scr.string=filename.read_text()
   del scr['src']
 page.set_content(str(soup),wait_until='domcontentloaded',timeout=45000)
 page.locator('[data-go="teacher"]').click()
 print('INITIAL',page.locator('#app').inner_text()[:600], 'ERRS',errors); page.locator('#offlineEdit').click(timeout=3000)
 page.locator('#wordFile').set_input_files('/mnt/data/Nguon GK1 Hoa 10-001 - TRONDE - 3P.docx')
 page.wait_for_function("window.A4_DEBUG.getState().questions.length > 0",timeout=45000)
 payload=page.evaluate('''() => {const s=window.A4_DEBUG.getState();return {count:s.questions.length,sections:s.questions.reduce((p,q)=>(p[q.section]=(p[q.section]||0)+1,p),{}),answers:s.questions.slice(0,4).map(x=>x.answer),warnings:s.questions.flatMap(q=>q.issues.map(w=>({at:q.position,text:w}))).slice(0,12)}}''')
 print('WORD_RESULT',payload)
 assert payload['count']==21,payload
 assert payload['sections']=={'I':15,'II':2,'III':4},payload
 assert payload['answers'][:2]==['A','C'],payload
 assert any('WMF' in x['text'] or 'wmf' in x['text'].lower() for x in payload['warnings']),payload
 page.screenshot(path=str(path/'tests/word_preview.png'),full_page=True)
 page.locator('[data-toq="18"]').click()
 q=page.locator('#editBody').input_value()
 print('SHORT_QUESTION',q[:110])
 assert 'Nguyên tố R' in q
 print('BROWSER_ERRORS',errors[:4]); assert not errors,errors
 b.close()

