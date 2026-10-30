from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]/'web'
soup=BeautifulSoup((root/'index.html').read_text(),'html.parser')
kv=soup.new_tag('script');kv.string="var __kv={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__kv[k]??null,setItem:(k,v)=>{__kv[k]=v},removeItem:k=>delete __kv[k]}})";soup.head.append(kv)
for scr in list(soup.find_all('script')):
 if scr.has_attr('src'):
  if 'mathjax' in scr['src']:scr.decompose();continue
  scr.string=(root/scr['src']).read_text();del scr['src']
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
  ctx=b.new_context(viewport={'width':1280,'height':860},accept_downloads=True)
  page=ctx.new_page();role=['pending']; calls=[]; errors=[]
  page.on('pageerror',lambda e: errors.append(str(e)))
  page.set_content(str(soup),wait_until='domcontentloaded')
  page.evaluate("""() => {
    window.QA={calls:[],role:'pending',signed:false};
    API.signUp=async (...a)=>{QA.calls.push(['signup',a]);return {id:'u1'}};
    API.requestPasswordReset=async (...a)=>{QA.calls.push(['recover',a]);return {ok:true}};
    API.signIn=async (...a)=>{QA.calls.push(['login',a]);QA.signed=true;return {access_token:'mock'}};
    API.hasSession=()=>QA.signed;
    API.signOut=()=>{QA.signed=false};
    API.call=async(action,data)=>{QA.calls.push([action,data]);if(action==='auth.status')return {email:'giaovien@truong.vn',role:QA.role,confirmed:true};if(action==='teacher.exams')return {exams:[]};if(action==='admin.teacherInvites')return {invites:[]};if(action==='admin.inviteTeacher')return {ok:true,email:data.email,activated:false};return {ok:true}};
  }""")
  page.locator('[data-go="teacher"]').click()
  page.locator('#openSignup').click()
  assert page.locator('#signupName').count()==1
  page.locator('#signupName').fill('Thầy Minh')
  page.locator('#signupEmail').fill('giaovien@truong.vn')
  page.locator('#signupPassword').fill('TenCharsPass123!')
  page.locator('#signupConfirm').fill('TenCharsPass123!')
  page.locator('#submitSignup').click()
  page.wait_for_selector('#loginEmail')
  assert page.evaluate("QA.calls.some(x=>x[0]==='signup')")
  page.locator('#openForgot').click()
  page.locator('#recoverEmail').fill('giaovien@truong.vn')
  page.locator('#requestRecovery').click()
  page.wait_for_timeout(150)
  assert page.evaluate("QA.calls.some(x=>x[0]==='recover')")
  page.locator('#backLogin').click()
  page.locator('#loginEmail').fill('giaovien@truong.vn')
  page.locator('#loginPassword').fill('TenCharsPass123!')
  page.locator('#login').click()
  page.get_by_text('đang chờ cấp quyền',exact=False).first.wait_for(timeout=10000)
  assert page.locator('[data-view="list"]').count()==0
  page.evaluate("QA.role='teacher'")
  page.locator('#pendingCheck').click()
  page.locator('[data-view="list"]').wait_for(timeout=10000)
  assert page.locator('[data-view="staff"]').count()==0
  page.evaluate("QA.role='admin'")
  page.locator('[data-view="list"]').click()
  page.locator('[data-view="staff"]').wait_for(timeout=10000)
  page.locator('[data-view="staff"]').click()
  page.locator('#inviteEmail').fill('dongnghiep@truong.vn')
  page.locator('#inviteName').fill('Cô Ngọc')
  page.locator('#inviteSave').click()
  page.wait_for_timeout(500)
  assert page.evaluate("QA.calls.some(x=>x[0]==='admin.inviteTeacher' && x[1].email==='dongnghiep@truong.vn')")
  page.screenshot(path=str(Path(__file__).parent/'teacher_accounts_preview.png'),full_page=False)
  assert not errors,errors
  print('PASS signup, confirm-role pending, teacher access, admin invite, password recovery, no JS errors')
  b.close()
finally:
 pass
