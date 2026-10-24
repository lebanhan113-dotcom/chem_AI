from playwright.sync_api import sync_playwright
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'static/index.html').read_text().replace('<link rel="stylesheet" href="/assets/ui.css">','').replace('<script src="/assets/app3.js"></script>','')
css=(ROOT/'static/ui.css').read_text().replace("@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');",'')
html=html.replace('</head>','<style>'+css+'</style></head>')
js=(ROOT/'static/app3.js').read_text()
c=json.loads((ROOT/'data/curriculum.json').read_text())
# Browser-origin access can be restricted in this sandbox; stub both server replies and session storage for visual tests.
mock="""
Object.defineProperty(window,'sessionStorage',{value:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}}});
Object.defineProperty(window,'localStorage',{value:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}}});
window.fetch=async function(input){let x=String(input);let data={}; if(x.includes('/curriculum'))data=__CURR__;else if(x.includes('/health'))data={ok:true};else if(x.includes('/references'))data=[];else if(x.includes('/visit'))data={recorded:true};else if(x.includes('/exams'))data=[];else if(x.includes('/questions/counts'))data={total:1};return {ok:true,status:200,json:async()=>data}};
""".replace('__CURR__',json.dumps(c,ensure_ascii=False))
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name,width,height in [('desktop',1400,900),('mobile',390,844)]:
  pg=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
  errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  pg.set_content(html)
  pg.add_script_tag(content=mock)
  pg.add_script_tag(content=js)
  pg.wait_for_timeout(350)
  print(name,'headings',pg.locator('h1').all_inner_texts(), 'errors',errors)
  pg.screenshot(path=str(ROOT/f'tests/ui_{name}.png'),full_page=True)
  if name=='desktop':
   pg.locator('[data-view="curriculum"]').first.click();pg.wait_for_timeout(100)
   print('curriculum',pg.locator('h1').all_inner_texts(), 'errors',errors)
   pg.screenshot(path=str(ROOT/'tests/ui_curriculum.png'),full_page=True)
  pg.close()
 b.close()
