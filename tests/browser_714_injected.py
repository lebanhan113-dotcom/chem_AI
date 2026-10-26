from playwright.sync_api import sync_playwright
from pathlib import Path
import re,json
root=Path('/mnt/data/edup714')
content=json.loads((root/'data/curriculum.json').read_text())
datas={str(Path('data')/f.name):json.loads(f.read_text()) for f in (root/'data').glob('*.json')}

def base(page,name):
 html=(root/name).read_text()
 html=re.sub(r'<script[^>]+src="[^"]+"[^>]*></script>','',html)
 html=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>','',html)
 page.set_content(html)
 page.evaluate("""() => {window.__queue=[];window.fetch=(url)=>new Promise(resolve=>window.__queue.push([String(url),resolve]));}""")

def load_scripts(page,paths):
 for f in paths:page.add_script_tag(content=(root/f).read_text())
 page.evaluate("""datas=>{window.fetch=async url=>{const u=String(url).replace(/^(\.\/|\.\.\/)/,'');const val=u.startsWith('api/public-bank')?{questions:[],enabled:false}:datas[u];return {ok:val!==undefined,status:val===undefined?404:200,json:async()=>val};}; for(const [u,res] of window.__queue)window.fetch(u).then(res);window.__queue=[];}""",datas)

with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-web-security'])
 for width,height in [(1440,900),(390,844)]:
  page=b.new_page(viewport={'width':width,'height':height},accept_downloads=True)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  base(page,'index.html')
  for css in ['app.css','form2025.css','launchpad710.css','source712.css','source713.css','bank-update714.css']:page.add_style_tag(content=(root/'css'/css).read_text())
  load_scripts(page,['js/chem-normalize.js','js/docx-export.js','js/app.js','js/integration78.js','js/form2025.js','js/launchpad710.js','js/gap-planning.js','js/source712.js','js/source713.js','js/bank-update714.js'])
  page.wait_for_function('bank.length===322',timeout=30000)
  page.wait_for_timeout(450)
  assert page.locator('.bankupdate-feature714 button').count()==2
  assert page.locator('.course-card713').count()==21
  page.locator('.bankupdate-feature714 button').first.click()
  assert 'Bổ sung nguồn câu hỏi' in page.locator('#main').inner_text()
  assert page.locator('a[href="./teacher-tools/index.html"]').count()==1
  page.screenshot(path=f'/mnt/data/EduPlan_AI_7_14_Giao_Dien_{width}px.png')
  print('UI',width,'322?',page.evaluate('bank.length'),'chapters',page.locator('.course-card713').count(),'cards',page.locator('.feature710').count(),'overflow',page.evaluate('document.documentElement.scrollWidth>innerWidth'),'errors',errors[:2]);page.close()
 page=b.new_page(viewport={'width':1400,'height':900},accept_downloads=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 base(page,'teacher-tools/index.html')
 page.add_style_tag(content=(root/'css/bank-update714.css').read_text())
 load_scripts(page,['teacher-tools/docx-reader.js','teacher-tools/import.js'])
 page.evaluate('window.dispatchEvent(new Event("DOMContentLoaded"))')
 page.wait_for_function('document.querySelector("#summary").textContent.includes("câu đã nhập")',timeout=15000)
 sample=Path('/mnt/data/2026 - 2027. 11.1 Can bang hoa hoc. TTB  - Dap an - DE1.docx')
 page.locator('#source-files').set_input_files(str(sample))
 page.wait_for_function('document.querySelector("#summary").textContent.match(/[1-9][0-9]* câu đã nhập/)',timeout=30000)
 print('DOCX IMPORT',page.locator('#summary').inner_text(),'entries',page.locator('.question-item').count(),'errors',errors[:2])
 page.locator('.question-item').first.click()
 print('EDITOR',page.locator('#grade').input_value(),page.locator('#chapter_no').input_value(),page.locator('#problems').inner_text()[:200])
 page.screenshot(path='/mnt/data/EduPlan_AI_7_14_Cap_Nhat_Nguon.png')
 assert page.locator('#grade').input_value()=='11'
 assert page.locator('#chapter_no').input_value()=='1'
 assert 'chưa' in page.locator('#problems').inner_text().lower() or len(page.locator('#problems').inner_text())>0
 print('TEST PASS: UI and DOCX import')
 b.close()
