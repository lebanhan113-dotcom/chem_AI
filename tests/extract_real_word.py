from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
P=Path(__file__).resolve().parent.parent
soup=BeautifulSoup((P/'web/index.html').read_text(),'html.parser')
pre=soup.new_tag('script');pre.string="var __kv={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__kv[k]??null,setItem:(k,v)=>{__kv[k]=v},removeItem:k=>delete __kv[k]}})";soup.head.append(pre)
for sc in list(soup.find_all('script')):
 if sc.has_attr('src'):
  fp=P/'web'/sc['src']
  if 'mathjax' in str(fp):sc.decompose();continue
  sc.string=fp.read_text();del sc['src']
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 page=b.new_page()
 page.set_content(str(soup))
 page.locator('[data-go="teacher"]').click()
 page.locator('#offlineEdit').click()
 page.locator('#wordFile').set_input_files('/mnt/data/Nguon GK1 Hoa 10-001 - TRONDE - 3P.docx')
 page.wait_for_function('window.A4_DEBUG.getState().questions.length===21')
 data=page.evaluate('''() => { const s=window.A4_DEBUG.getState();return {meta:s.meta,questions:s.questions} }''')
 f=P/'docs/DE_GOC_HOA10_CHO_GIAO_VIEN_DUYET.json';f.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 problems=[]
 for q in data['questions']:
  for w in q['issues']:problems.append(f"PHẦN {q['section']} – CÂU {q['number']}: {w}")
 (P/'docs/BAO_CAO_DUYET_DE_GOC.txt').write_text(f"Đề gốc đã đọc: {len(data['questions'])} câu (15 PHẦN I, 2 PHẦN II, 4 PHẦN III).\nCâu hỏi chưa được duyệt; điểm đang là 0 và phải nhập theo hướng dẫn chấm.\nCác cảnh báo:\n"+'\n'.join(problems),encoding='utf-8')
 print('Saved imported genuine data',len(data['questions']),'warnings',len(problems))
 b.close()
