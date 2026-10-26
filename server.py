"""EduPlan AI 7.14 - self contained local backend, keeps answer keys on server."""
from __future__ import annotations
import os,re,io,sys,hashlib,json,time,uuid,secrets,random,base64,csv,subprocess,tempfile,shutil,unicodedata,threading
from pathlib import Path
from collections import Counter
from fastapi import FastAPI,HTTPException,UploadFile,File,Form,Request,Depends
from fastapi.responses import HTMLResponse,FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from pydantic import BaseModel
from bs4 import BeautifulSoup
HERE=Path(__file__).resolve().parent; DATA=HERE/'questions_private.json'; MEDIA=HERE/'media';MEDIA.mkdir(exist_ok=True)
app=FastAPI(title='EduPlan 7.14 - Hóa học Đúng/Sai', docs_url=None,redoc_url=None)
app.mount('/media',StaticFiles(directory=str(MEDIA)),name='media')
security=HTTPBasic()
PASSWORD=os.environ.get('EDUPLAN_ADMIN_PASSWORD','')
PF=HERE/'.teacher_password'
if not PASSWORD:
 if not PF.exists():PF.write_text(secrets.token_urlsafe(15),encoding='utf8');os.chmod(PF,0o600)
 PASSWORD=PF.read_text(encoding='utf8').strip()
print('\nMẬT KHẨU QUẢN TRỊ CỤC BỘ (không chia sẻ cho học sinh):',PASSWORD,flush=True)
LOCK=threading.Lock();QUESTIONS=json.loads(DATA.read_text(encoding='utf8'));SESSION={}
def admin(creds:HTTPBasicCredentials=Depends(security)):
 if not (secrets.compare_digest(creds.username,'giaovien') and secrets.compare_digest(creds.password,PASSWORD)):
  raise HTTPException(401,'Sai tài khoản hoặc mật khẩu.',headers={'WWW-Authenticate':'Basic realm="EduPlan"'})
 return True
def strip(h):return re.sub(r'\s+',' ',BeautifulSoup(h or '','html.parser').get_text(' ',strip=True)).strip()
def fingerprint(q):
 s='|'.join(unicodedata.normalize('NFKC',strip(x)).casefold() for x in q.get('statements',[]));return hashlib.sha256(s.encode()).hexdigest() if len(q.get('statements',[]))==4 else ''
def gradeable(q):
 key=q.get('correct',[]);return q.get('status') in ['historical_source_key','auto_accepted_source_key'] and len(q.get('statements',[]))==4 and len(key)==4 and all(type(x)==bool for x in key) and len(q.get('explanations',[]))==4
PRIVATE=['correct','explanations','solutionIntroHtml','sourceReviewWarning','qualityFlags','qualityChecks','approval','sourceHasFullKey','sourceCorrectnessVerified','fingerprint','autoReviewNote','sourceFile','hasKey']
def public(q):return {k:v for k,v in q.items() if k not in PRIVATE}
def select(grade=None,chapter=None,lesson=None,part=None,term='',mode='graded'):
 term=term.lower().strip()
 with LOCK: data=list(QUESTIONS)
 rows=[]
 for q in data:
  if mode=='graded' and not gradeable(q):continue
  if mode=='source' and gradeable(q):continue
  if grade and int(q.get('grade',0))!=int(grade):continue
  if chapter and str(q.get('chapter'))!=str(chapter):continue
  if lesson and str(q.get('lesson'))!=str(lesson):continue
  if part and q.get('part')!=part:continue
  if term and term not in f"{strip(q.get('stemHtml',''))} {q.get('lessonName','')} {q.get('sourceNumber','')}".lower():continue
  rows.append(q)
 return rows
@app.get('/')
def index():return FileResponse(HERE/'index.html')
@app.get('/assets/{filename}')
def asset(filename:str):
 if filename not in ('app.css','app.js'):raise HTTPException(404)
 return FileResponse(HERE/filename)
@app.get('/api/catalog')
def catalog():
 with LOCK:qs=list(QUESTIONS)
 groups={}
 for q in qs:
  key=str(q.get('grade'))+'-'+str(q.get('chapter'))+'-'+str(q.get('lesson'))
  cur=groups.setdefault(key,{'grade':q.get('grade'),'chapter':q.get('chapter'),'chapterName':q.get('chapterName'),'lesson':q.get('lesson'),'lessonName':q.get('lessonName'),'part':q.get('part','II'),'total':0,'graded':0,'practice':0})
  cur['total']+=1;cur['graded' if gradeable(q) else 'practice']+=1
 return {'total':len(qs),'graded':sum(gradeable(q) for q in qs),'practice':sum(not gradeable(q) for q in qs),'groups':sorted(groups.values(),key=lambda x:(x['grade'],x['chapter'],x['lesson']))}
@app.get('/api/questions')
def questions(grade:int|None=None,chapter:int|None=None,lesson:int|None=None,part:str='II',term:str='',mode:str='source',limit:int=20,offset:int=0):
 rows=select(grade,chapter,lesson,part,term,mode)
 return {'total':len(rows),'items':[public(q) for q in rows[max(0,offset):max(0,offset)+min(max(limit,1),50)]]}
class StartReq(BaseModel):
 grade:int|None=None;chapter:int|None=None;lesson:int|None=None;part:str='II';mode:str='graded';count:int=5;term:str='';ids:list[str]|None=None
@app.post('/api/start')
def start(req:StartReq):
 mode=req.mode if req.mode in ('source','graded') else 'graded';items=select(req.grade,req.chapter,req.lesson,req.part,req.term,mode)
 if req.ids: items=[q for q in items if q['id'] in req.ids]
 if not items:raise HTTPException(400,'Không có câu trong phạm vi chọn. Hãy đổi chương, bài hoặc chế độ luyện.')
 picked=random.sample(items,min(max(req.count,1),min(len(items),30)))
 token=secrets.token_urlsafe(24)
 SESSION[token]={'ids':[q['id'] for q in picked],'mode':mode,'ts':time.time()}
 return {'session':token,'mode':mode,'total':len(picked),'questions':[public(q) for q in picked]}
class SubmitReq(BaseModel):
 session:str;answers:dict[str,list[bool|None]]
@app.post('/api/submit')
def submit(req:SubmitReq):
 entry=SESSION.pop(req.session,None)
 if not entry or time.time()-entry['ts']>10800:raise HTTPException(400,'Phiên bài đã hết hạn hoặc đã nộp. Tạo lượt mới để luyện tiếp.')
 with LOCK:idx={q['id']:q for q in QUESTIONS}
 output=[];correctCount=0;total=0
 for ident in entry['ids']:
  q=idx.get(ident)
  if not q:continue
  yours=(req.answers.get(ident) or [])[:4];yours+=([None]*max(0,4-len(yours)))
  truth=q.get('correct') if entry['mode']=='graded' and gradeable(q) else None
  detail=[]
  for i,s in enumerate(q.get('statements',[])):
   actual=truth[i] if truth is not None else None;ans=yours[i];ok=(ans==actual) if (actual is not None and ans is not None) else False
   if actual is not None:total+=1;correctCount+=int(ok)
   detail.append({'label':'abcd'[i],'text':s,'selected':ans,'correct':actual,'isCorrect':ok if actual is not None else None,'explanation':q['explanations'][i] if actual is not None else ''})
  output.append({'id':ident,'sourceNumber':q.get('sourceNumber'),'lessonName':q.get('lessonName'),'stemHtml':q.get('stemHtml',''),'mediaHtml':q.get('mediaHtml',''),'items':detail,'isGraded':truth is not None,'solutionIntroHtml':q.get('solutionIntroHtml','') if truth is not None else '','verification':'Đáp án theo tài liệu nguồn, chưa được chứng minh đúng tuyệt đối về mặt khoa học.' if truth is not None else 'Tài liệu nguồn chưa đủ điều kiện để chấm tự động.'})
 return {'correct':correctCount,'total':total,'percent':round(100*correctCount/total,1) if total else None,'questions':output}
@app.get('/api/admin/stats')
def stats(_:bool=Depends(admin)):
 with LOCK:qs=list(QUESTIONS)
 return {'total':len(qs),'graded':sum(gradeable(q) for q in qs),'quarantine':sum(not gradeable(q) for q in qs),'byChapter':{f'{gr}-{ch}':num for (gr,ch),num in Counter((q['grade'],q['chapter']) for q in qs).items()}}
@app.get('/api/admin/report')
def report(_:bool=Depends(admin)):
 with LOCK:qs=list(QUESTIONS)
 return {'items':[{'id':q['id'],'sourceFile':q.get('sourceFile'),'chapter':q.get('chapter'),'lessonName':q.get('lessonName'),'status':q.get('status'),'flags':q.get('qualityFlags',q.get('sourceReviewWarning',[]))} for q in qs[-250:]]}
@app.get('/api/admin/export')
def exp(_:bool=Depends(admin)):
 return FileResponse(DATA,filename='EduPlan_private_teacher_questions.json')
def save():
 temp=DATA.with_suffix('.tmp');temp.write_text(json.dumps(QUESTIONS,ensure_ascii=False,separators=(',',':')),encoding='utf8');temp.replace(DATA)
def adapt(q,filename,grade,chapter,i):
 q=dict(q);q['grade']=int(q.get('grade') or grade);q['chapter']=int(q.get('chapter') or chapter)
 q.setdefault('chapterName',f'Chương {chapter}')
 q.setdefault('lesson',int(q.get('lesson') or 0));q.setdefault('lessonName',f'Bài gợi ý {q["lesson"]}')
 q.setdefault('part','II');q.setdefault('type','true_false');q.setdefault('sourceNumber',i+1)
 q.setdefault('sectionOrigin','Nguồn bổ sung');q.setdefault('sourceFile',filename)
 q['id']=f'import-{uuid.uuid4().hex[:12]}'
 if isinstance(q.get('statements'),str):q['statements']=[s.strip() for s in q['statements'].split('||')]
 if isinstance(q.get('explanations'),str):q['explanations']=[s.strip() for s in q['explanations'].split('||')]
 if isinstance(q.get('correct'),str):q['correct']=[x.strip().lower() in ('đ','đúng','true','1') for x in re.split(r'[;,|\-]',q['correct']) if x.strip()]
 q.setdefault('stemHtml',q.get('stem',''));q.setdefault('statements',[])
 q.setdefault('correct',[]);q.setdefault('explanations',[]);q.setdefault('mediaHtml','');q.setdefault('solutionIntroHtml','')
 # Don't auto-certify chemistry: structural admission only, no key guessing
 enough=(len(q['statements'])==4 and len(q['correct'])==4 and all(type(x)==bool for x in q['correct']) and len(q['explanations'])==4 and all(len(strip(x))>=15 for x in q['explanations']) and not q.get('hasMedia') and not q.get('mediaMissing') and not q.get('qualityFlags') and not re.search(r'<img|\[Hình hoặc',str(q['stemHtml'])+str(q['statements'])))
 q['status']='auto_accepted_source_key' if enough else 'quarantined_unverified';q['sourceCorrectnessVerified']=False
 q['qualityFlags']=[] if enough else ['Thiếu 4 câu/4 đáp án/lời giải đủ dài hoặc có hình/công thức chưa xác minh']
 return q
@app.post('/api/admin/import')
async def importfile(file:UploadFile=File(...),grade:int=Form(...),chapter:int=Form(...),_:bool=Depends(admin)):
 if grade not in (10,11,12) or not 1<=chapter<=8:raise HTTPException(400,'Khối hoặc chương không hợp lệ')
 ext=Path(file.filename or '').suffix.lower();name=Path(file.filename or '').name
 if ext not in ('.json','.csv','.docx'):raise HTTPException(400,'Chỉ hỗ trợ DOCX/CSV/JSON')
 raw=await file.read(12*1024*1024+1)
 if len(raw)>12*1024*1024:raise HTTPException(413,'Tệp vượt quá 12 MB')
 if not raw:raise HTTPException(400,'Tệp rỗng')
 incoming=[];notes=[]
 try:
  if ext=='.json':
   data=json.loads(raw.decode('utf-8-sig'));incoming=data if isinstance(data,list) else data.get('questions',data.get('items',[]))
  elif ext=='.csv':
   incoming=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
  else:
   from parser_source import scan
   import parser_source as parser
   with tempfile.TemporaryDirectory(prefix='edp718-') as d:
    d=Path(d);p=d/name;p.write_bytes(raw)
    output=subprocess.run(['libreoffice','-env:UserInstallation=file:///tmp/lo_edp718_import','--headless','--convert-to','html:XHTML Writer File:UTF8','--outdir',str(d),str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=90)
    if output.returncode or not (d/(p.stem+'.html')).exists():raise ValueError('Không chuyển đổi được DOCX sang HTML')
    # Xác định lại khối/chương từ đầu tài liệu nếu có tiêu đề tường minh.
    rawtop=BeautifulSoup((d/(p.stem+'.html')).read_text(encoding='utf8'),'html.parser').get_text(' ',strip=True)[:1900]
    guessedGrade=re.search(r'H[ÓO]A\s*H[ỌO]C\s*(10|11|12)\b',rawtop,re.I)
    guessedChapter=re.search(r'CHƯƠNG\s*(\d{1,2})\b',rawtop,re.I)
    if guessedGrade:grade=int(guessedGrade.group(1))
    if guessedChapter:chapter=int(guessedChapter.group(1))
    notes.append(f'Tự nhận diện nội dung: Hóa {grade} · Chương {chapter}.')
    old=parser.HTML;parser.HTML=d
    try:incoming=scan(p.stem,(grade,chapter,f'Chương {chapter}'));notes.append('Tên bài được phân loại theo chuyên đề trích xuất; các chủ đề không xác định vẫn được giữ nguyên để tự luyện.')
    finally:parser.HTML=old
  if not isinstance(incoming,list):raise ValueError('Không thấy mảng câu hỏi')
  incoming=[adapt(q,name,grade,chapter,i) for i,q in enumerate(incoming) if isinstance(q,dict)]
 except Exception as exc:raise HTTPException(400,'Không đọc được nội dung nguồn: '+str(exc)[:200])
 added=0;duplicates=0;published=0;blocked=0
 with LOCK:
  seen={fingerprint(q) for q in QUESTIONS if fingerprint(q)}
  for q in incoming:
   fp=fingerprint(q)
   if fp and fp in seen:duplicates+=1;continue
   if fp:seen.add(fp)
   if gradeable(q):published+=1
   else:blocked+=1
   QUESTIONS.append(q);added+=1
  if added:save()
 return {'file':name,'scanned':len(incoming),'added':added,'duplicates':duplicates,'auto_accepted_with_source_key':published,'quarantined':blocked,'notes':notes,'warning':'Quy tắc tự chấp nhận chỉ kiểm tra khóa nguồn và cấu trúc, không xác nhận đáp án Hóa học tuyệt đối.'}
