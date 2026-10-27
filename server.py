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
HERE=Path(__file__).resolve().parent
# Persist student records, teacher question edits and source upload history across redeploys.
# Render/Railway: mount a persistent disk/volume at EDUPLAN_DATA_DIR (/data).
DATA_DIR=Path(os.environ.get('EDUPLAN_DATA_DIR',str(HERE))).resolve()
DATA_DIR.mkdir(parents=True,exist_ok=True)
DATA=DATA_DIR/'questions_private.json'
HISTORY=DATA_DIR/'source_import_history.json'
MEDIA=DATA_DIR/'media'
MEDIA.mkdir(parents=True,exist_ok=True)
# First-run initialization only: never overwrite a teacher's persistent edits.
if not DATA.exists():
    shutil.copy2(HERE/'questions_private.json',DATA)
if not HISTORY.exists() and (HERE/'source_import_history.json').exists():
    shutil.copy2(HERE/'source_import_history.json',HISTORY)
# Prepackaged diagrams/formula images and user uploads share the /media URL prefix.
# Existing content is copied only when absent, not overwritten on redeploy.
for _src in (HERE/'media').iterdir():
    if _src.is_file() and not (MEDIA/_src.name).exists():
        shutil.copy2(_src,MEDIA/_src.name)

app=FastAPI(title='EduPlan 7.14 - Hóa học Đúng/Sai', docs_url=None,redoc_url=None)
app.mount('/media',StaticFiles(directory=str(MEDIA)),name='media')
security=HTTPBasic()
PASSWORD=os.environ.get('EDUPLAN_ADMIN_PASSWORD','').strip()
PF=DATA_DIR/'.teacher_password'
IS_PRODUCTION=os.environ.get('EDUPLAN_ENV','').lower()=='production'
if IS_PRODUCTION and len(PASSWORD)<16:
    raise RuntimeError('Máy chủ online yêu cầu EDUPLAN_ADMIN_PASSWORD từ 16 ký tự; đặt trong hosting environment, không đưa vào repo.')
if not PASSWORD:
    if not PF.exists():
        PF.write_text(secrets.token_urlsafe(24),encoding='utf8')
        os.chmod(PF,0o600)
    PASSWORD=PF.read_text(encoding='utf8').strip()
    if not IS_PRODUCTION:
        print('MẬT KHẨU GIÁO VIÊN PHÁT TRIỂN CỤC BỘ:',PASSWORD,flush=True)
LOCK=threading.Lock();QUESTIONS=json.loads(DATA.read_text(encoding='utf8'));SESSION={}

try:IMPORTED_SOURCES=json.loads(HISTORY.read_text(encoding='utf8')) if HISTORY.exists() else {}
except (ValueError,OSError):IMPORTED_SOURCES={}

def admin(creds:HTTPBasicCredentials=Depends(security)):
 if not (secrets.compare_digest(creds.username,'giaovien') and secrets.compare_digest(creds.password,PASSWORD)):
  raise HTTPException(401,'Sai tài khoản hoặc mật khẩu.',headers={'WWW-Authenticate':'Basic realm="EduPlan"'})
 return True
def strip(h):return re.sub(r'\s+',' ',BeautifulSoup(h or '','html.parser').get_text(' ',strip=True)).strip()
def fingerprint(q):
 # Cùng bốn nhận định nhưng khác tình huống/đề dẫn vẫn là hai câu khác nhau.
 statements=q.get('statements',[])
 if not isinstance(statements,list) or len(statements)!=4:return ''
 parts=[q.get('stemHtml','')]+statements
 s='|'.join(re.sub(r'\s+',' ',unicodedata.normalize('NFKC',strip(x)).casefold()).strip() for x in parts)
 return hashlib.sha256(s.encode('utf8')).hexdigest()

def near_source_duplicate(a,b):
 # Word có thể chèn/bỏ nhãn [KNTT - SBT] trước đề dẫn.
 # Chỉ coi trùng nếu CÙNG tệp nguồn, lớp/chương, bốn nhận định giống nhau
 # và phần đề dẫn sau chuẩn hóa về cơ bản giống nhau.
 if a.get('sourceFile')!=b.get('sourceFile') or a.get('grade')!=b.get('grade') or a.get('chapter')!=b.get('chapter'):return False
 if len(a.get('statements',[]))!=4 or len(b.get('statements',[]))!=4:return False
 def clean(x):
  t=unicodedata.normalize('NFKC',strip(x)).casefold()
  t=re.sub(r'\[(?:kntt|cd|ctst|qg|sgk|sbt)[^\]]{0,35}\]',' ',t)
  return re.sub(r'\s+',' ',t).strip()
 if [clean(x) for x in a['statements']]!=[clean(x) for x in b['statements']]:return False
 from difflib import SequenceMatcher
 stem1=clean(a.get('stemHtml',''));stem2=clean(b.get('stemHtml',''))
 return (stem1==stem2) or (min(len(stem1),len(stem2))>24 and SequenceMatcher(None,stem1,stem2).ratio()>=0.92)

def gradeable(q):
 key=q.get('correct',[]);return q.get('status') in ['historical_source_key','auto_accepted_source_key'] and len(q.get('statements',[]))==4 and len(key)==4 and all(type(x)==bool for x in key) and len(q.get('explanations',[]))==4
# Chỉ xuất các thuộc tính đã cho phép; không dùng blacklist vì nguồn nhập JSON
# có thể chứa những tên như answer, answerKey, key, solution, ...
PUBLIC_FIELDS=('id','sourceNumber','sectionOrigin','grade','chapter','chapterName','lesson','lessonName','part','type','stemHtml','statements','mediaHtml','levelSuggested','competencySuggested')
def safe_html(raw):
    soup=BeautifulSoup(str(raw or ''),'html.parser')
    allowed={'p','b','strong','i','em','u','sub','sup','br','table','thead','tbody','tr','th','td','ul','ol','li','div','span','img'}
    for el in list(soup.find_all(True)):
        if el.name in {'script','iframe','style','object','embed','svg','form','meta','link'}:
            el.decompose()
        elif el.name not in allowed:
            el.unwrap()
        elif el.name=='img':
            src=el.get('src','')
            if not re.fullmatch(r'/media/[A-Za-z0-9._-]+\.(?:png|jpe?g|gif|webp)',src):
                el.decompose()
            else: el.attrs={'src':src,'alt':el.get('alt','Hình minh họa hóa học'),'loading':'lazy'}
        else:
            el.attrs={k:el.attrs[k] for k in ('colspan','rowspan') if k in el.attrs and str(el.attrs[k]).isdigit()}
    return str(soup)

def public(q):
    data={k:q[k] for k in PUBLIC_FIELDS if k in q}
    for k in ('stemHtml','mediaHtml'):
        if k in data:data[k]=safe_html(data[k])
    if 'statements' in data:data['statements']=[safe_html(x) for x in data['statements']]
    return data


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
@app.middleware('http')
async def security_headers(request:Request,call_next):
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']='camera=(),microphone=(),geolocation=()'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control']='no-store'
    return response

@app.get('/healthz',include_in_schema=False)
def health():
    return {'status':'ok','app':'EduPlan AI 7.14 Online','questions':len(QUESTIONS),'persistent_data':DATA_DIR!=HERE}

@app.get('/')
def index():return FileResponse(HERE/'index.html')
@app.get('/assets/{filename}')
def asset(filename:str):
 if filename not in ('app.css','app.js','management.js'):raise HTTPException(404)
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
def questions(grade:int|None=None,chapter:int|None=None,lesson:int|None=None,part:str='II',term:str='',mode:str='source',level:str='',competency:str='',limit:int=20,offset:int=0):
 rows=select(grade,chapter,lesson,part,term,mode)
 if level:rows=[q for q in rows if q.get('levelSuggested')==level]
 if competency:rows=[q for q in rows if q.get('competencySuggested')==competency]
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
 with LOCK:
  # Giới hạn phiên chưa nộp; không để số lượng phiên tăng vô hạn.
  now=time.time()
  for old in [k for k,v in SESSION.items() if now-v['ts']>10800]:SESSION.pop(old,None)
  if len(SESSION)>3000:raise HTTPException(429,'Quá nhiều phiên đang mở. Hãy thử lại sau.')
  SESSION[token]={'ids':[q['id'] for q in picked],'mode':mode,'ts':now}
 return {'session':token,'mode':mode,'total':len(picked),'questions':[public(q) for q in picked]}
class SubmitReq(BaseModel):
 session:str;answers:dict[str,list[bool|None]]
@app.post('/api/submit')
def submit(req:SubmitReq):
 with LOCK:
  entry=SESSION.get(req.session)
  if not entry or time.time()-entry['ts']>10800:raise HTTPException(400,'Phiên bài đã hết hạn hoặc đã nộp. Tạo lượt mới để luyện tiếp.')
  if entry['mode']=='graded':
   for ident in entry['ids']:
    answer=req.answers.get(ident,[])
    if len(answer)!=4 or any(type(v)!=bool for v in answer):
     raise HTTPException(400,'Hãy chọn đầy đủ Đúng hoặc Sai cho cả bốn ý của từng câu trước khi nộp.')
  SESSION.pop(req.session,None)
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
   detail.append({'label':'abcd'[i],'text':safe_html(s),'selected':ans,'correct':actual,'isCorrect':ok if actual is not None else None,'explanation':safe_html(q['explanations'][i]) if actual is not None else ''})
  output.append({'id':ident,'sourceNumber':q.get('sourceNumber'),'lessonName':q.get('lessonName'),'stemHtml':safe_html(q.get('stemHtml','')),'mediaHtml':safe_html(q.get('mediaHtml','')),'items':detail,'isGraded':truth is not None,'solutionIntroHtml':safe_html(q.get('solutionIntroHtml','')) if truth is not None else '','verification':'Đáp án theo tài liệu nguồn, chưa được chứng minh đúng tuyệt đối về mặt khoa học.' if truth is not None else 'Tài liệu nguồn chưa đủ điều kiện để chấm tự động.'})
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
def save_source_history():
 temp=HISTORY.with_suffix('.tmp')
 temp.write_text(json.dumps(IMPORTED_SOURCES,ensure_ascii=False,indent=2),encoding='utf8')
 temp.replace(HISTORY)

def parse_answer(raw):
 if isinstance(raw,list):
  if len(raw)!=4 or any(type(x)!=bool for x in raw):return []
  return raw
 if not isinstance(raw,str):return []
 tokens=[x.strip().casefold() for x in re.split(r'[;,|]',raw) if x.strip()]
 if len(tokens)!=4:return []
 yes={'đ','đúng','d','true','1'};no={'s','sai','false','0'}
 if any(x not in yes|no for x in tokens):return []
 return [x in yes for x in tokens]

def office_executable():
 for candidate in (os.environ.get('SOFFICE_PATH'),shutil.which('libreoffice'),shutil.which('soffice'),
                   str(Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'LibreOffice'/'program'/'soffice.exe'),
                   str(Path(os.environ.get('PROGRAMFILES(X86)','C:/Program Files (x86)'))/'LibreOffice'/'program'/'soffice.exe'),
                   '/Applications/LibreOffice.app/Contents/MacOS/soffice'):
  if candidate and Path(candidate).is_file():return str(candidate)
 return None

def adapt(q,filename,grade,chapter,i):
 q=dict(q);q['grade']=int(q.get('grade') or grade);q['chapter']=int(q.get('chapter') or chapter)
 if q['grade'] not in (10,11,12) or not 1<=q['chapter']<=8:raise ValueError('Khối hoặc chương trong dữ liệu nguồn không hợp lệ')
 known=next((x['chapterName'] for x in QUESTIONS if x['grade']==q['grade'] and x['chapter']==q['chapter']),f'Chương {q["chapter"]}')
 q['chapterName']=q.get('chapterName') or known
 q['lesson']=int(q.get('lesson') or 0)
 known_lesson=next((x['lessonName'] for x in QUESTIONS if x['grade']==q['grade'] and x['chapter']==q['chapter'] and x.get('lesson')==q['lesson']),None)
 q['lessonName']=q.get('lessonName') or known_lesson or (f'Chưa xác định bài · {known}' if not q['lesson'] else f'Bài {q["lesson"]} · {known}')
 q.setdefault('part','II');q.setdefault('type','true_false');q.setdefault('sourceNumber',i+1)
 q.setdefault('sectionOrigin','Nguồn bổ sung');q.setdefault('sourceFile',filename)
 q['id']=f'import-{uuid.uuid4().hex[:12]}'
 if isinstance(q.get('statements'),str):q['statements']=[s.strip() for s in q['statements'].split('||')]
 if isinstance(q.get('explanations'),str):q['explanations']=[s.strip() for s in q['explanations'].split('||')]
 q['correct']=parse_answer(q.get('correct'))
 q.setdefault('stemHtml',q.get('stem',''));q.setdefault('statements',[])
 q.setdefault('explanations',[]);q.setdefault('mediaHtml','');q.setdefault('solutionIntroHtml','')
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
 raw=await file.read(32*1024*1024+1)
 if len(raw)>32*1024*1024:raise HTTPException(413,'Tệp vượt quá 32 MB')
 if not raw:raise HTTPException(400,'Tệp rỗng')
 digest=hashlib.sha256(raw).hexdigest()
 with LOCK:
  if digest in IMPORTED_SOURCES:
   return {'file':name,'scanned':0,'added':0,'duplicates':0,'auto_accepted_with_source_key':0,'quarantined':0,'unchanged_source':True,'notes':['Tệp này đã có trong ngân hàng và không thay đổi; đã tự động bỏ qua toàn bộ để tránh nhập lặp.'],'warning':'Tệp chưa thay đổi, không thực hiện nhập lại.'}
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
    office=office_executable()
    if not office:raise ValueError('Chưa tìm thấy LibreOffice. Cài LibreOffice hoặc cấu hình SOFFICE_PATH (đường dẫn soffice.exe)')
    profile=d/'lo_profile';profile.mkdir(exist_ok=True)
    output=subprocess.run([office,'-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','html:XHTML Writer File:UTF8','--outdir',str(d),str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
    if output.returncode or not (d/(p.stem+'.html')).exists():raise ValueError('Không chuyển đổi được DOCX sang HTML')
    # Xác định lại khối/chương từ đầu tài liệu nếu có tiêu đề tường minh.
    rawtop=BeautifulSoup((d/(p.stem+'.html')).read_text(encoding='utf8'),'html.parser').get_text(' ',strip=True)[:1900]
    guessedGrade=re.search(r'H[ÓO]A\s*H[ỌO]C\s*(10|11|12)\b',rawtop,re.I)
    guessedChapter=re.search(r'CHƯƠNG\s*(\d{1,2})\b',rawtop,re.I)
    if guessedGrade:grade=int(guessedGrade.group(1))
    if guessedChapter:chapter=int(guessedChapter.group(1))
    notes.append(f'Tự nhận diện nội dung: Hóa {grade} · Chương {chapter}.')
    old=parser.HTML;old_media=parser.MEDIA;parser.HTML=d;parser.MEDIA=MEDIA
    try:incoming=scan(p.stem,(grade,chapter,f'Chương {chapter}'));notes.append('Tên bài được phân loại theo chuyên đề trích xuất; các chủ đề không xác định vẫn được giữ nguyên để tự luyện.')
    finally:parser.HTML=old;parser.MEDIA=old_media
  if not isinstance(incoming,list):raise ValueError('Không thấy mảng câu hỏi')
  incoming=[adapt(q,name,grade,chapter,i) for i,q in enumerate(incoming) if isinstance(q,dict)]
 except Exception as exc:raise HTTPException(400,'Không đọc được nội dung nguồn: '+str(exc)[:200])
 added=0;duplicates=0;published=0;blocked=0;conflicts=0
 with LOCK:
  by_fingerprint={fingerprint(q):q for q in QUESTIONS if fingerprint(q)}
  seen=set(by_fingerprint)
  by_source={}
  for prev in QUESTIONS:by_source.setdefault((prev.get('sourceFile'),prev.get('grade'),prev.get('chapter')),[]).append(prev)
  for q in incoming:
   fp=fingerprint(q)
   peers=by_source.get((q.get('sourceFile'),q.get('grade'),q.get('chapter')),[])
   matching=by_fingerprint.get(fp) if fp else None
   if matching is None:matching=next((prev for prev in peers if near_source_duplicate(q,prev)),None)
   if matching:
    duplicates+=1
    old_key=matching.get('correct',[]);new_key=q.get('correct',[])
    if len(old_key)==len(new_key)==4 and all(type(x)==bool for x in old_key+new_key) and old_key!=new_key:conflicts+=1
    continue
   if fp:seen.add(fp);by_fingerprint[fp]=q
   by_source.setdefault((q.get('sourceFile'),q.get('grade'),q.get('chapter')),[]).append(q)
   if gradeable(q):published+=1
   else:blocked+=1
   QUESTIONS.append(q);added+=1
  if conflicts:notes.append(f'{conflicts} câu trùng nội dung nhưng khác khóa đáp án. Đã giữ nguyên bản cũ và cảnh báo, không ghi đè tự động.')
  if added:save()
  IMPORTED_SOURCES[digest]={'file':name,'importedCount':len(incoming),'lastProcessed':time.strftime('%Y-%m-%d')}
  save_source_history()
 return {'file':name,'scanned':len(incoming),'added':added,'duplicates':duplicates,'answer_conflicts':conflicts,'auto_accepted_with_source_key':published,'quarantined':blocked,'notes':notes,'warning':'Quy tắc tự chấp nhận chỉ kiểm tra khóa nguồn và cấu trúc, không xác nhận đáp án Hóa học tuyệt đối.'}

# Mô-đun quản lý lớp, giao bài, khóa học, kiểm tra online, chấm phiếu và phân tích kết quả.
import workflow
workflow.setup(app,admin,QUESTIONS,gradeable,public,LOCK,safe_html)
