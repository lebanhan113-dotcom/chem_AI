from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parent.parent
html=BeautifulSoup((p/'index.html').read_text(),'html.parser')
pre=html.new_tag('script');pre.string="var __kv={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__kv[k]??null,setItem:(k,v)=>{__kv[k]=v},removeItem:k=>delete __kv[k]}})";html.head.append(pre)
with sync_playwright() as play:
 b=play.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 page=b.new_page(viewport={'width':1280,'height':850})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(str(html),wait_until='domcontentloaded',timeout=80000)
 page.locator('[data-go="teacher"]').click()
 page.locator('#offlineEdit').click()
 page.locator('#wordFile').set_input_files('/mnt/data/Nguon GK1 Hoa 10-001 - TRONDE - 3P.docx')
 page.wait_for_function('window.A4_DEBUG.getState().questions.length===21',timeout=70000)
 print('OK SINGLE HTML',len(page.locator('[data-toq]').all()),'câu')
 page.screenshot(path=str(p/'tests'/'standalone_preview.png'),full_page=False)
 print('Browser errors',errors[:4]);assert not errors,errors
 b.close()
