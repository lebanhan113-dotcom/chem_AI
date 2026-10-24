"""CHEM-MAP TUTOR AI 3.5 - FastAPI multi-user online MVP.
Uses SQLite with persistent mounted DATA_DIR; optional PostgreSQL via DATABASE_URL + psycopg2.
No AI key required; optional OPENAI_API_KEY is server-only for verified teacher-reviewed drafts.
"""
from __future__ import annotations
import os, json, time, base64, hmac, hashlib, secrets, re, random, datetime
from pathlib import Path
from typing import Any
from collections import Counter
import httpx
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

ROOT=Path(__file__).resolve().parent
DATA=Path(os.getenv('DATA_DIR',str(ROOT/'runtime')));DATA.mkdir(parents=True,exist_ok=True)
DB_URL=os.getenv('DATABASE_URL') or 'sqlite:///'+str(DATA/'chemmap.sqlite')
if DB_URL.startswith('postgres://'):DB_URL=DB_URL.replace('postgres://','postgresql://',1)
engine=create_engine(DB_URL,connect_args={'check_same_thread':False} if DB_URL.startswith('sqlite') else {},pool_pre_ping=True)
SECRET=os.getenv('SESSION_SECRET') or ('dev-only-secret' if os.getenv('ENVIRONMENT','development')!='production' else None)
ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD')
if not SECRET:raise RuntimeError('Set SESSION_SECRET in production')
CURR=json.loads((ROOT/'data/curriculum.json').read_text())
SEED=json.loads((ROOT/'data/questions.json').read_text())
SOURCE_IMPORT=json.loads((ROOT/'data/teacher_docx_import.json').read_text())
APP=FastAPI(title='CHEM-MAP TUTOR AI 3.5',version='3.5')

with engine.begin() as c:
 for stmt in [
  'CREATE TABLE IF NOT EXISTS people (id TEXT PRIMARY KEY,name TEXT NOT NULL,role TEXT NOT NULL,class_id TEXT,pin_hash TEXT, created_at TEXT)',
  'CREATE TABLE IF NOT EXISTS classes (id TEXT PRIMARY KEY,name TEXT,grade INTEGER,code TEXT UNIQUE,created_at TEXT)',
  'CREATE TABLE IF NOT EXISTS questions (id TEXT PRIMARY KEY, grade INTEGER,chapter TEXT,lesson_id TEXT,type TEXT,level TEXT,status TEXT,payload TEXT,created_at TEXT)',
  'CREATE TABLE IF NOT EXISTS exams (id TEXT PRIMARY KEY,title TEXT, grade INTEGER,chapter TEXT,lesson_id TEXT,category TEXT,question_ids TEXT,created_at TEXT,public INTEGER)',
  'CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY,exam_id TEXT,student_id TEXT,class_id TEXT,answers TEXT,results TEXT,score REAL,graded INTEGER,created_at TEXT,updated_at TEXT)',
  'CREATE TABLE IF NOT EXISTS visits (visitor TEXT,day TEXT,created_at TEXT,PRIMARY KEY(visitor,day))',
  'CREATE TABLE IF NOT EXISTS worksheets (id TEXT PRIMARY KEY,grade INTEGER,chapter TEXT,lesson_id TEXT,title TEXT,kind TEXT,payload TEXT,created_at TEXT)',
  'CREATE TABLE IF NOT EXISTS study_events (id TEXT PRIMARY KEY,student_id TEXT,question_id TEXT,lesson_id TEXT,grade INTEGER,chapter TEXT,level TEXT,is_correct INTEGER,created_at TEXT)'
 ]:c.execute(text(stmt))
 count=c.execute(text('SELECT COUNT(*) FROM questions')).scalar()
 if not count:
  for q in SEED:
   c.execute(text('INSERT INTO questions(id,grade,chapter,lesson_id,type,level,status,payload,created_at) VALUES (:id,:g,:ch,:l,:t,:v,:s,:p,:at)'),
    {'id':q['id'],'g':q['grade'],'ch':q['chapter'],'l':q.get('lesson_id'),'t':q['type'],'v':q['level'],'s':'demo','p':json.dumps(q,ensure_ascii=False),'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})

 # Integrate new source documents idempotently; keep previously reviewed records and attempts unchanged.
 for q in SOURCE_IMPORT:
  c.execute(text('INSERT INTO questions(id,grade,chapter,lesson_id,type,level,status,payload,created_at) SELECT :id,:g,:ch,:l,:t,:v,:s,:p,:at WHERE NOT EXISTS (SELECT 1 FROM questions WHERE id=:id)'),
    {'id':q['id'],'g':q['grade'],'ch':q['chapter'],'l':q.get('lesson_id'),'t':q['type'],'v':q['level'],'s':'import-pending','p':json.dumps(q,ensure_ascii=False),'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})

 # Migrate lesson suggestions only for unreviewed imports not yet assigned by a teacher.
 # Existing approved/edited questions, student attempts and class data are untouched.
 for q in SOURCE_IMPORT:
  if not q.get('lesson_id'):continue
  record=c.execute(text("SELECT lesson_id,status,payload FROM questions WHERE id=:id"),{'id':q['id']}).mappings().first()
  if record and record['status']=='import-pending' and not record['lesson_id']:
   old=json.loads(record['payload'])
   if old.get('lesson_id'):continue
   old['lesson_id']=q['lesson_id']
   for field in ('lesson_mapping_status','lesson_mapping_basis','lesson_mapping_confidence'):
    old[field]=q.get(field)
   c.execute(text('UPDATE questions SET lesson_id=:lesson,payload=:payload WHERE id=:id'),{
    'id':q['id'],'lesson':q['lesson_id'],'payload':json.dumps(old,ensure_ascii=False)})

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def uid(prefix):return prefix+'-'+secrets.token_hex(8)
def commit(stmt,values={}):
 with engine.begin() as c:return c.execute(text(stmt),values)
def fetchall(stmt,values={}):
 with engine.connect() as c:return [dict(r) for r in c.execute(text(stmt),values).mappings().all()]
def fetchone(stmt,values={}):
 with engine.connect() as c:
  a=c.execute(text(stmt),values).mappings().first()
  return dict(a) if a else None

def pinhash(pin,salt=None):
 salt=salt or secrets.token_hex(12)
 h=hashlib.pbkdf2_hmac('sha256',str(pin).encode(),salt.encode(),180000).hex()
 return salt+'$'+h
def pincheck(pin,digest):
 try:
  salt,_=digest.split('$');return hmac.compare_digest(pinhash(pin,salt),digest)
 except Exception:return False

def token_for(id,role,exp=86400):
 p=json.dumps({'sub':id,'role':role,'exp':int(time.time()+exp)},separators=(',',':')).encode()
 data=base64.urlsafe_b64encode(p).decode().rstrip('=')
 sig=hmac.new(SECRET.encode(),data.encode(),hashlib.sha256).hexdigest()
 return data+'.'+sig

def user(req:Request):
 raw=req.headers.get('Authorization','')
 if not raw.startswith('Bearer '):raise HTTPException(401,'Vui lòng đăng nhập')
 try:
  body,signature=raw[7:].split('.')
  valid=hmac.new(SECRET.encode(),body.encode(),hashlib.sha256).hexdigest()
  if not hmac.compare_digest(signature,valid):raise ValueError('signature')
  payload=json.loads(base64.urlsafe_b64decode(body+'='*(-len(body)%4)))
  if int(payload['exp'])<time.time():raise ValueError('expired')
  return payload
 except Exception:raise HTTPException(401,'Phiên đăng nhập không hợp lệ')

def teacher(u=Depends(user)):
 if u['role']!='teacher':raise HTTPException(403,'Dành cho giáo viên')
 return u

class AuthIn(BaseModel):
 password:str
class JoinIn(BaseModel):
 code:str
 name:str=Field(min_length=2,max_length=60)
 pin:str=Field(min_length=6,max_length=30)
class ClassIn(BaseModel):
 name:str=Field(min_length=2,max_length=90)
 grade:int=Field(ge=10,le=12)
class BuildIn(BaseModel):
 grade:int=Field(ge=10,le=12)
 chapter:str='all'
 lesson_id:str|None=None
 title:str='Đề kiểm tra Hóa học Form 2025'
 category:str='Giữa kì 1'
 mcq:int=Field(default=18,ge=0,le=100)
 tf:int=Field(default=4,ge=0,le=50)
 short:int=Field(default=6,ge=0,le=50)
 essay:int=Field(default=4,ge=0,le=50)
class AnswerIn(BaseModel):
 answers:dict[str,Any]
class GradeIn(BaseModel):
 points:dict[str,float]
class QuestionIn(BaseModel):
 payload:dict[str,Any]
class SourceReviewIn(BaseModel):
 updates:dict[str,Any]=Field(default_factory=dict)
 confirmed:bool=False
 approve:bool=False
class WorksheetIn(BaseModel):
 grade:int=Field(ge=10,le=12)
 chapter:str
 lesson_id:str|None=None
 title:str
 kind:str='Phiếu học tập'
class AssistantIn(BaseModel):
 message:str=Field(min_length=2,max_length=2000)
 grade:int=11
 chapter:str=''

@APP.get('/api/health')
def health():return {'ok':True,'version':'3.5','storage':'database','ai_mode':'optional'}
@APP.get('/api/curriculum')
def curriculum():return CURR
@APP.post('/api/visit')
def visit(req:Request):
 # Unique per opaque anonymous visitor id per UTC date, never trust as hard identity.
 visitor=req.headers.get('X-Visitor','')
 if not re.fullmatch(r'[a-zA-Z0-9_-]{12,100}',visitor):return {'recorded':False}
 day=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
 with engine.begin() as c:
  n=c.execute(text('SELECT 1 FROM visits WHERE visitor=:v AND day=:d'),{'v':visitor,'d':day}).first()
  if not n:c.execute(text('INSERT INTO visits(visitor,day,created_at) VALUES (:v,:d,:at)'),{'v':visitor,'d':day,'at':now()})
 return {'recorded':True,'unique_per_day':True}
@APP.post('/api/auth/teacher')
def teacher_login(item:AuthIn):
 if not ADMIN_PASSWORD:raise HTTPException(503,'Cần cấu hình ADMIN_PASSWORD trên máy chủ')
 if not hmac.compare_digest(item.password,ADMIN_PASSWORD):raise HTTPException(401,'Mật khẩu không hợp lệ')
 return {'token':token_for('teacher','teacher',6*3600),'name':'Giáo viên','role':'teacher'}
@APP.post('/api/classes')
def create_class(item:ClassIn,u=Depends(teacher)):
 cid=uid('class');code=secrets.token_hex(3).upper()
 commit('INSERT INTO classes(id,name,grade,code,created_at) VALUES (:id,:n,:g,:c,:at)',{'id':cid,'n':item.name,'g':item.grade,'c':code,'at':now()})
 return {'id':cid,'name':item.name,'grade':item.grade,'code':code}
@APP.get('/api/classes')
def classes(u=Depends(teacher)):
 return fetchall('SELECT c.*, (SELECT COUNT(*) FROM people p WHERE p.class_id=c.id) AS students FROM classes c ORDER BY created_at DESC')
@APP.post('/api/auth/join')
def join(item:JoinIn):
 cls=fetchone('SELECT * FROM classes WHERE code=:c',{'c':item.code.strip().upper()})
 if not cls:raise HTTPException(404,'Mã lớp chưa đúng')
 name=item.name.strip()
 prev=fetchone('SELECT * FROM people WHERE class_id=:c AND lower(name)=:n',{'c':cls['id'],'n':name.lower()})
 if prev:
  if not pincheck(item.pin,prev['pin_hash']):raise HTTPException(401,'Tên đã tồn tại; vui lòng dùng PIN đã đăng ký')
  sid=prev['id']
 else:
  sid=uid('student')
  commit('INSERT INTO people(id,name,role,class_id,pin_hash,created_at) VALUES (:id,:n,:r,:c,:p,:at)',{'id':sid,'n':name,'r':'student','c':cls['id'],'p':pinhash(item.pin),'at':now()})
 return {'token':token_for(sid,'student',24*3600),'role':'student','id':sid,'name':name,'grade':cls['grade'],'class_name':cls['name']}
@APP.get('/api/me')
def me(u=Depends(user)):
 if u['role']=='teacher':return {'name':'Giáo viên','role':'teacher'}
 p=fetchone('SELECT id,name,class_id FROM people WHERE id=:i',{'i':u['sub']})
 if not p:raise HTTPException(401,'Không tìm thấy hồ sơ')
 return {**p,'role':'student'}
@APP.get('/api/classes/{cid}/random')
def random_name(cid:str,u=Depends(teacher)):
 rows=fetchall('SELECT id,name FROM people WHERE class_id=:c ORDER BY name',{'c':cid})
 if not rows:raise HTTPException(404,'Lớp chưa có học sinh')
 return {**secrets.choice(rows),'total':len(rows)}


def _is_source_question(q):
 return str(q.get('id','')).startswith('SRC-')

def _validate_source(q):
 errors=[]
 if not q.get('stem') or len(q['stem'].strip())<8:errors.append('Thiếu nội dung câu hỏi.')
 t=q.get('type')
 if t=='mcq':
  if len(q.get('options',[]))!=4 or any(not str(x).strip() for x in q['options']):errors.append('Phải có 4 phương án A–D đầy đủ.')
  if type(q.get('correct')) is not int or not 0<=q['correct']<4:errors.append('Cần xác nhận đáp án A–D.')
 elif t=='tf':
  if len(q.get('statements',[]))!=4 or any(not str(x).strip() for x in q['statements']):errors.append('Phải có đủ 4 nhận định a–d.')
  if len(q.get('correct',[]))!=4 or any(type(x) is not bool for x in q['correct']):errors.append('Cần xác nhận 4 đáp án Đúng/Sai.')
 elif t=='short':
  if type(q.get('correct')) not in (float,int):errors.append('Chưa có đáp số dạng số để chấm online; cần nhập đáp án số hợp lệ hoặc chuyển thành tự luận.')
 elif t=='essay':pass
 else:errors.append('Loại câu hỏi không hợp lệ.')
 if not q.get('explanation') or len(q['explanation'].strip())<8:errors.append('Thiếu hướng dẫn giải.')
 return errors

@APP.get('/api/sources/summary')
def source_summary(u=Depends(teacher)):
 rows=fetchall("SELECT grade,chapter,type,status,COUNT(*) as total FROM questions WHERE id LIKE 'SRC-%' GROUP BY grade,chapter,type,status ORDER BY grade,chapter,type")
 return {'total':sum(r['total'] for r in rows),'approved':sum(r['total'] for r in rows if r['status']=='approved'),'pending':sum(r['total'] for r in rows if r['status']=='import-pending'), 'by_chapter':rows}

@APP.get('/api/sources/questions')
def source_items(grade:int|None=None,chapter:str='all',kind:str='all',status:str='all',q:str='',offset:int=0,limit:int=Query(default=20,ge=1,le=100),u=Depends(teacher)):
 conditions=["id LIKE 'SRC-%'"];params={}
 if grade in (10,11,12):conditions.append('grade=:g');params['g']=grade
 if chapter!='all':conditions.append('chapter=:c');params['c']=chapter
 if kind!='all':conditions.append('type=:t');params['t']=kind
 if status!='all':conditions.append('status=:s');params['s']=status
 base=' FROM questions WHERE '+' AND '.join(conditions)
 records=fetchall('SELECT id,grade,chapter,lesson_id,type,level,status,payload'+base+' ORDER BY grade,chapter,type,id',params)
 matched=[]
 for rec in records:
  b=json.loads(rec['payload'])
  if q.casefold() not in (b.get('stem','')+' '+b.get('source','')+' '+b.get('id','')).casefold():continue
  matched.append({'id':rec['id'],'grade':rec['grade'],'chapter':rec['chapter'],'type':rec['type'],'level':rec['level'],'status':rec['status'],'stem':b['stem'][:260],'issue_count':len([n for n in b.get('review_notes',[]) if not n.startswith('Đã trích xuất')]),'valid_structure':not _validate_source(b),'source_number':b.get('source_number'),'lesson_id':rec.get('lesson_id') or b.get('lesson_id'),'lesson_mapping_status':b.get('lesson_mapping_status','chapter-only')})
 return {'total':len(matched),'offset':offset,'items':matched[offset:offset+limit]}

@APP.get('/api/sources/documents/{filename}')
def source_document(filename:str,u=Depends(teacher)):
 # Original documents are server-private; access requires teacher authorization.
 if filename!=Path(filename).name or not filename.lower().endswith('.docx'):raise HTTPException(404)
 path=ROOT/'source_docs'/filename
 if not path.is_file():raise HTTPException(404,'Tệp nguồn không tồn tại')
 return FileResponse(path,filename=filename,media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@APP.get('/api/sources/questions/{qid}')
def source_detail(qid:str,u=Depends(teacher)):
 r=fetchone('SELECT payload,status FROM questions WHERE id=:i',{'i':qid})
 if not r or not qid.startswith('SRC-'):raise HTTPException(404,'Không tìm thấy học liệu nhập từ DOCX')
 b=json.loads(r['payload']);b['status']=r['status']
 return {'question':b,'validation_errors':_validate_source(b)}

@APP.post('/api/sources/questions/{qid}/review')
def source_review(qid:str,item:SourceReviewIn,u=Depends(teacher)):
 r=fetchone('SELECT payload,status FROM questions WHERE id=:i',{'i':qid})
 if not r or not qid.startswith('SRC-'):raise HTTPException(404)
 b=json.loads(r['payload']);allowed={'stem','options','statements','correct','level','explanation','lesson_id','tolerance','rubric','statementExplanations'}
 if set(item.updates)-allowed:raise HTTPException(422,'Trường cập nhật không được cho phép')
 for key,value in item.updates.items():b[key]=value
 if b.get('lesson_id'):
  ch=next((ch for ch in CURR['grades'][str(b['grade'])] if ch['title']==b['chapter']),None)
  if not ch or b['lesson_id'] not in {l['id'] for l in ch['lessons']}:raise HTTPException(422,'Bài được chọn không thuộc chương hiện tại.')
 errors=_validate_source(b)
 if item.approve:
  if not item.confirmed:raise HTTPException(422,'Giáo viên phải xác nhận đã đối chiếu tài liệu gốc và kiểm tra tính chính xác hóa học.')
  if errors:raise HTTPException(422,{'message':'Không thể duyệt câu chưa đủ cấu trúc hoặc chưa chấm được','errors':errors})
  b['status']='approved';b['approved_at']=now();b['approved_by']='teacher';b['lesson_mapping_status']='teacher-confirmed' if b.get('lesson_id') else 'chapter-confirmed';new_status='approved'
 else:
  b['status']='import-pending';new_status='import-pending'
 commit('UPDATE questions SET payload=:p,level=:lv,lesson_id=:lesson,status=:s WHERE id=:i',{'p':json.dumps(b,ensure_ascii=False),'lv':b.get('level','Thông hiểu'),'lesson':b.get('lesson_id'),'s':new_status,'i':qid})
 return {'id':qid,'status':new_status,'validation_errors':errors}

def _filter(grade:int,chapter:str='all',lesson_id:str|None=None,typ:str|None=None,approved=False):
 st='SELECT * FROM questions WHERE grade=:g';args={'g':grade}
 if chapter and chapter!='all':st+=' AND chapter=:c';args['c']=chapter
 if lesson_id:st+=' AND lesson_id=:l';args['l']=lesson_id
 if typ:st+=' AND type=:t';args['t']=typ
 if approved:st+=" AND status IN ('approved','demo')"
 return fetchall(st,args)
@APP.get('/api/questions/counts')
def counts(grade:int,chapter:str='all',lesson_id:str|None=None):
 rows=_filter(grade,chapter,lesson_id,approved=True)
 return {'total':len(rows),'by_type':dict(Counter(x['type'] for x in rows)),'by_level':dict(Counter(x['level'] for x in rows))}
@APP.get('/api/questions')
def list_questions(grade:int,chapter:str='all',lesson_id:str|None=None,show_answers:bool=False,u=Depends(user)):
 if show_answers and u['role']!='teacher':raise HTTPException(403,'Đáp án chỉ dành cho giáo viên')
 rows=_filter(grade,chapter,lesson_id,approved=True)
 return [_public_question(json.loads(x['payload'])) if not show_answers else json.loads(x['payload']) for x in rows]

def _public_question(q):
 p={k:v for k,v in q.items() if k not in ['correct','correct_text','explanation','statementExplanations','distractors','rubric','method','tip','review_notes','source_file','student_source_file','source_kind','has_teacher_solution','source_section','source_number','approved_by','approved_at','lesson_mapping_basis','lesson_mapping_confidence','lesson_mapping_status']}
 return p
@APP.post('/api/questions')
def create_question(item:QuestionIn,u=Depends(teacher)):
 q=item.payload;grade=q.get('grade');typ=q.get('type');stem=str(q.get('stem') or '').strip()
 if grade not in [10,11,12] or typ not in ['mcq','tf','short','essay'] or not stem:raise HTTPException(422,'Thiếu lớp, loại câu hoặc nội dung')
 if typ=='mcq' and (len(q.get('options',[]))!=4 or q.get('correct') not in range(4)):raise HTTPException(422,'Câu nhiều lựa chọn cần 4 phương án và đáp án từ 0 đến 3')
 if typ=='tf' and (len(q.get('statements',[]))!=4 or len(q.get('correct',[]))!=4):raise HTTPException(422,'Đúng/Sai cần 4 ý và 4 đáp án')
 if typ=='short' and not isinstance(q.get('correct'),(float,int)):raise HTTPException(422,'Trả lời ngắn tự chấm chỉ hỗ trợ giá trị số')
 q['id']=uid('Q');q['status']='draft';q['source']=q.get('source') or 'Giáo viên biên soạn mới'
 commit('INSERT INTO questions(id,grade,chapter,lesson_id,type,level,status,payload,created_at) VALUES (:id,:g,:c,:l,:t,:v,:s,:p,:at)',{'id':q['id'],'g':grade,'c':q.get('chapter',''),'l':q.get('lesson_id'),'t':typ,'v':q.get('level','Thông hiểu'),'s':'draft','p':json.dumps(q,ensure_ascii=False),'at':now()})
 return {'id':q['id'],'status':'draft'}
@APP.get('/api/questions/drafts')
def drafts(u=Depends(teacher)):
 return [json.loads(r['payload']) for r in fetchall("SELECT payload FROM questions WHERE status='draft' ORDER BY created_at DESC")]
@APP.post('/api/questions/{qid}/approve')
def approve(qid:str,u=Depends(teacher)):
 q=fetchone('SELECT * FROM questions WHERE id=:id',{'id':qid})
 if not q:raise HTTPException(404)
 body=json.loads(q['payload'])
 if _is_source_question(body):raise HTTPException(403,'Vui lòng duyệt học liệu nhập qua mục Nguồn câu hỏi, có xác nhận đã kiểm tra nội dung.')
 body['status']='approved'
 commit('UPDATE questions SET status=:s,payload=:p WHERE id=:id',{'s':'approved','p':json.dumps(body,ensure_ascii=False),'id':qid})
 return {'ok':True,'id':qid}
@APP.post('/api/exams/build')
def build_exam(item:BuildIn,u=Depends(teacher)):
 request={'mcq':item.mcq,'tf':item.tf,'short':item.short,'essay':item.essay}
 rows=_filter(item.grade,item.chapter,item.lesson_id,approved=True)
 found=Counter(r['type'] for r in rows)
 missing={k:{'need':v,'available':found.get(k,0),'missing':max(0,v-found.get(k,0))} for k,v in request.items() if found.get(k,0)<v}
 if missing:raise HTTPException(status_code=409,detail={'message':'Ngân hàng chưa đủ theo phạm vi đã chọn; cần bổ sung và duyệt câu hỏi.','shortage':missing,'total_available':len(rows)})
 ids=[]
 for kind,num in request.items():
  possible=[r['id'] for r in rows if r['type']==kind]
  ids.extend(secrets.SystemRandom().sample(possible,num))
 if not ids:raise HTTPException(422,'Không thể tạo đề 0 câu')
 eid=uid('exam')
 commit('INSERT INTO exams(id,title,grade,chapter,lesson_id,category,question_ids,created_at,public) VALUES (:i,:t,:g,:c,:l,:cat,:q,:at,1)',{'i':eid,'t':item.title[:140],'g':item.grade,'c':item.chapter,'l':item.lesson_id,'cat':item.category,'q':json.dumps(ids),'at':now()})
 return {'id':eid,'title':item.title,'count':len(ids),'by_type':request,'join_path':'/?exam='+eid}
@APP.get('/api/exams')
def exams(grade:int|None=None):
 if grade:return fetchall('SELECT id,title,grade,chapter,lesson_id,category,created_at FROM exams WHERE public=1 AND grade=:g ORDER BY created_at DESC',{'g':grade})
 return fetchall('SELECT id,title,grade,chapter,lesson_id,category,created_at FROM exams WHERE public=1 ORDER BY created_at DESC')
@APP.get('/api/exams/{eid}')
def exam_detail(eid:str,u=Depends(user)):
 exam=fetchone('SELECT * FROM exams WHERE id=:e',{'e':eid})
 if not exam:raise HTTPException(404,'Không thấy đề')
 ids=json.loads(exam['question_ids']);rows=[]
 for qid in ids:
  r=fetchone('SELECT payload FROM questions WHERE id=:i',{'i':qid})
  if r:rows.append(_public_question(json.loads(r['payload'])))
 return {'id':eid,'title':exam['title'],'grade':exam['grade'],'category':exam['category'],'questions':rows}

def _judge(q,a):
 typ=q['type']
 if typ=='essay':return {'points':0,'max':1,'pending':True,'correct':None,'answer':str(a or ''),'diagnostics':[]}
 if typ=='mcq':
  try: idx=int(a)
  except Exception: idx=-1
  ok=(idx==q['correct'])
  d=q.get('distractors',{}).get(str(idx),{}) if not ok else {}
  return {'points':int(ok),'max':1,'pending':False,'correct':ok,'answer':idx,'right':q['correct'],'diagnostics':[{'code':d.get('code'),'hypothesis':d.get('hypothesis','Cần đối chiếu lời giải.'),'status':'Giả thuyết lỗi sai'}] if not ok else []}
 if typ=='tf':
  ans=a if isinstance(a,list) else []
  correct=q['correct'];right=sum(1 for i,c in enumerate(correct) if i<len(ans) and ans[i] in [True,False] and ans[i] is c)
  return {'points':right/4,'max':1,'pending':False,'correct':right==4,'answer':ans,'right':correct,'diagnostics':[]}
 if typ=='short':
  try: num=float(str(a).strip().replace(',','.'));ok=abs(num-float(q['correct']))<=float(q.get('tolerance',0.001))
  except Exception:ok=False
  return {'points':int(ok),'max':1,'pending':False,'correct':ok,'answer':a,'right':q['correct'],'diagnostics':[{'status':'Quan sát','hypothesis':'Sai đáp số; chưa đủ thông tin xác định nguyên nhân nếu không có bước giải.'}] if not ok else []}
 raise HTTPException(422)
@APP.post('/api/exams/{eid}/submit')
def submit(eid:str,item:AnswerIn,u=Depends(user)):
 if u['role']!='student':raise HTTPException(403,'Chỉ học sinh được nộp bài')
 exam=fetchone('SELECT * FROM exams WHERE id=:id',{'id':eid})
 if not exam:raise HTTPException(404)
 prior=fetchone('SELECT id FROM attempts WHERE exam_id=:e AND student_id=:s',{'e':eid,'s':u['sub']})
 if prior:raise HTTPException(409,'Bạn đã nộp bài này. Mỗi học sinh nộp một lần/đề.')
 ids=json.loads(exam['question_ids']);results=[];earned=0;pending=False
 for qid in ids:
  row=fetchone('SELECT payload FROM questions WHERE id=:i',{'i':qid})
  if not row:continue
  q=json.loads(row['payload']);r=_judge(q,item.answers.get(qid));earned+=r['points'];pending|=r['pending']
  results.append({'id':qid,'type':q['type'],'stem':q['stem'],'explanation':q.get('explanation',''),'level':q['level'],'chapter':q['chapter'],'question':_public_question(q),**r})
 score=round(10*earned/max(len(ids),1),2)
 a_id=uid('attempt')
 class_id=fetchone('SELECT class_id FROM people WHERE id=:i',{'i':u['sub']})['class_id']
 commit('INSERT INTO attempts(id,exam_id,student_id,class_id,answers,results,score,graded,created_at,updated_at) VALUES (:i,:e,:s,:c,:a,:r,:score,:g,:at,:at)',{'i':a_id,'e':eid,'s':u['sub'],'c':class_id,'a':json.dumps(item.answers,ensure_ascii=False),'r':json.dumps(results,ensure_ascii=False),'score':score,'g':int(not pending),'at':now()})
 return {'id':a_id,'score':score,'graded':not pending,'message':'Điểm tạm tính; chờ chấm tự luận' if pending else 'Điểm cuối cùng','results':results}
@APP.get('/api/attempts/mine')
def my_attempts(u=Depends(user)):
 if u['role']!='student':raise HTTPException(403)
 rows=fetchall('SELECT a.id,a.exam_id,e.title,a.score,a.graded,a.created_at FROM attempts a JOIN exams e ON e.id=a.exam_id WHERE a.student_id=:s ORDER BY a.created_at DESC',{'s':u['sub']})
 return rows
@APP.get('/api/attempts/{aid}')
def attempt_detail(aid:str,u=Depends(user)):
 a=fetchone('SELECT * FROM attempts WHERE id=:id',{'id':aid})
 if not a:raise HTTPException(404)
 if u['role']!='teacher' and a['student_id']!=u['sub']:raise HTTPException(403)
 return {'id':aid,'score':a['score'],'graded':bool(a['graded']),'results':json.loads(a['results']),'created_at':a['created_at']}
@APP.get('/api/analytics')
def analytics(u=Depends(teacher)):
 def count(s):return fetchone(s)['total']
 students=count('SELECT COUNT(*) AS total FROM people WHERE role=\'student\'')
 exams=count('SELECT COUNT(*) AS total FROM exams')
 tests=count('SELECT COUNT(*) AS total FROM attempts')
 visits=count('SELECT COUNT(*) AS total FROM visits')
 participants=count('SELECT COUNT(DISTINCT student_id) AS total FROM attempts')
 recent=fetchall('SELECT a.id,a.score,a.graded,a.created_at,p.name AS student,e.title AS exam FROM attempts a JOIN people p ON p.id=a.student_id JOIN exams e ON e.id=a.exam_id ORDER BY a.created_at DESC LIMIT 100')
 return {'unique_daily_visits':visits,'students_registered':students,'exams':exams,'attempts':tests,'distinct_participants':participants,'recent':recent,'note':'Lượt truy cập là tổng khách truy cập ẩn danh duy nhất theo từng ngày, không phải người dùng duy nhất toàn thời gian.'}
@APP.post('/api/attempts/{aid}/grade')
def grade_essay(aid:str,item:GradeIn,u=Depends(teacher)):
 a=fetchone('SELECT * FROM attempts WHERE id=:id',{'id':aid})
 if not a:raise HTTPException(404)
 results=json.loads(a['results'])
 for r in results:
  if r['type']=='essay' and r['id'] in item.points:
   v=float(item.points[r['id']]);
   if not 0<=v<=1:raise HTTPException(422,'Điểm tự luận mỗi câu từ 0 đến 1')
   r['points']=v;r['pending']=False;r['correct']=v>=0.99
 score=round(10*sum(x['points'] for x in results)/max(1,len(results)),2)
 graded=not any(x['pending'] for x in results)
 commit('UPDATE attempts SET results=:r,score=:s,graded=:g,updated_at=:at WHERE id=:id',{'r':json.dumps(results,ensure_ascii=False),'s':score,'g':int(graded),'at':now(),'id':aid})
 return {'id':aid,'score':score,'graded':graded}

@APP.post('/api/worksheets')
def worksheet(item:WorksheetIn,u=Depends(teacher)):
 row=_filter(item.grade,item.chapter,item.lesson_id,approved=True)
 selected=row[:12]
 w={'title':item.title,'grade':item.grade,'chapter':item.chapter,'lesson_id':item.lesson_id,'kind':item.kind,'nls':[{'code':'1.2','name':'Đánh giá dữ liệu, thông tin và nội dung số','evidence':'Phiếu đánh giá nguồn thông tin Hóa học'},{'code':'2.4','name':'Hợp tác thông qua công nghệ số','evidence':'Sản phẩm làm việc nhóm, có phân công và phản hồi'},{'code':'6.3','name':'Đánh giá trí tuệ nhân tạo','evidence':'Kiểm chứng một nhận định AI bằng dữ liệu nguồn'}],'activities':[{'title':'Khởi động','minutes':4},{'title':'Hình thành kiến thức','minutes':30},{'title':'Luyện tập','minutes':5},{'title':'Vận dụng','minutes':6}], 'questions':[_public_question(json.loads(r['payload'])) for r in selected], 'answers':[{'id':r['id'],'correct':json.loads(r['payload']).get('correct'),'explanation':json.loads(r['payload']).get('explanation')} for r in selected], 'source':'Câu hỏi trong ngân hàng nội bộ đã có; không tự tạo nội dung nếu thiếu'}
 wid=uid('worksheet')
 commit('INSERT INTO worksheets(id,grade,chapter,lesson_id,title,kind,payload,created_at) VALUES (:i,:g,:c,:l,:t,:k,:p,:at)',{'i':wid,'g':item.grade,'c':item.chapter,'l':item.lesson_id,'t':item.title,'k':item.kind,'p':json.dumps(w,ensure_ascii=False),'at':now()})
 return {'id':wid,'questions':len(selected),'status':'draft','note':'Phiếu tự lấy từ ngân hàng, cần giáo viên rà soát và bổ sung nếu chưa đủ nội dung.'}
@APP.get('/api/worksheets/{wid}')
def get_worksheet(wid:str,mode:str='student',u=Depends(user)):
 r=fetchone('SELECT * FROM worksheets WHERE id=:i',{'i':wid})
 if not r:raise HTTPException(404)
 w=json.loads(r['payload'])
 if mode=='teacher':
  if u['role']!='teacher':raise HTTPException(403)
 else:w.pop('answers',None)
 return w

REFERENCES=[
 {'name':'Nhà xuất bản Giáo dục Việt Nam - SGK điện tử cập nhật 2026–2027','url':'https://taphuan.nxbgd.vn','type':'Nguồn SGK chính thức'},
 {'name':'SGK Hóa học KNTT lớp 10 (mục lục tham khảo)','url':CURR['reference_urls']['10'],'type':'Chương trình'},
 {'name':'SGK Hóa học KNTT lớp 11 (mục lục tham khảo)','url':CURR['reference_urls']['11'],'type':'Chương trình'},
 {'name':'SGK Hóa học KNTT lớp 12 (mục lục tham khảo)','url':CURR['reference_urls']['12'],'type':'Chương trình'},
 {'name':'PubChem - dữ liệu hóa chất NCBI','url':'https://pubchem.ncbi.nlm.nih.gov/','type':'Cơ sở dữ liệu khoa học'},
 {'name':'NIST Chemistry WebBook','url':'https://webbook.nist.gov/chemistry/','type':'Cơ sở dữ liệu khoa học'},
 {'name':'IUPAC Gold Book','url':'https://goldbook.iupac.org/','type':'Thuật ngữ khoa học'},
 {'name':'OpenStax Chemistry 2e','url':'https://openstax.org/details/books/chemistry-2e','type':'Sách tham khảo mở (CC BY 4.0)'},
 {'name':'ChemCollective - Virtual Lab','url':'https://chemcollective.org/','type':'Mô phỏng và học liệu'},
 {'name':'MIT OpenCourseWare Chemistry','url':'https://ocw.mit.edu/search/?d=Chemistry','type':'Chuyên đề nâng cao mở'},
 {'name':'Đề và đáp án HSG quốc gia THPT 2025–2026 - Cục Quản lý chất lượng','url':'https://vqa.moet.gov.vn/vi/news/tin-tuc-su-kien/de-thi-dap-an-ky-thi-chon-hoc-sinh-gioi-quoc-gia-thpt-nam-hoc-2025-2026-242.html','type':'Đề HSG quốc gia / Bộ GDĐT'},
 {'name':'Đề và đáp án HSG quốc gia THPT 2024–2025 - Cục Quản lý chất lượng','url':'https://vqa.moet.gov.vn/vi/news/tin-tuc-su-kien/de-thi-va-dap-an-ky-thi-chon-hoc-sinh-gioi-quoc-gia-thpt-nam-hoc-2024-2025-171.html','type':'Đề HSG quốc gia / Bộ GDĐT'},
 {'name':'Bồi dưỡng HSG Hóa học 10 theo chuyên đề - Nguyễn Xuân Trường và cộng sự, NXB ĐHQGHN','url':'https://khanhlinhbooks.vn/product/sach-boi-duong-hoc-sinh-gioi-hoa-hoc-10-theo-chuyen-de/','type':'Sách tham khảo có bản quyền'},
 {'name':'Bồi dưỡng HSG Hóa học 11 theo chuyên đề (tập 1) - NXB ĐHQGHN','url':'https://bennghe.com.vn/products/boi-duong-hoc-sinh-gioi-hoa-hoc-theo-chuyen-de-11-tap-1-hoa-hoc-dai-cuong-va-vo-co-dung-chung-cho-cac-bo-sgk-hien-hanh-nguyen-xuan-truong','type':'Sách tham khảo có bản quyền'},
 {'name':'Bồi dưỡng HSG Hóa học 12 theo chuyên đề - NXB ĐHQGHN','url':'https://khanhlinhbooks.vn/product/sach-boi-duong-hoc-sinh-gioi-hoa-hoc-12-theo-chuyen-de-dung-chung-cho-cac-bo-sgk/','type':'Sách tham khảo có bản quyền'},
 {'name':'Kỳ thi chọn HSG quốc gia - tra cứu Bộ GDĐT','url':'https://moet.gov.vn/','type':'Thông tin chính thức; cần kiểm tra năm và bản quyền'},
 {'name':'Thông tư 02/2025 - năng lực số người học','url':'https://chinhphu.vn/?classid=0&docid=212648&pageid=27160','type':'Văn bản quy phạm'}]
@APP.get('/api/references')
def references():return REFERENCES
@APP.get('/api/references/search')
async def references_search(q:str):
 if len(q.strip())<2:return {'results':[],'notice':'Nhập từ khóa cụ thể'}
 results=[]
 # Query Crossref openly for metadata, never scrape/reproduce copyrighted questions.
 try:
  async with httpx.AsyncClient(timeout=7,headers={'User-Agent':'CHEM-MAP-EDU/3.0 (educational research)'}) as client:
   resp=await client.get('https://api.crossref.org/works',params={'query.title':q,'rows':5,'select':'DOI,title,URL,author,published'})
   resp.raise_for_status()
   for x in resp.json().get('message',{}).get('items',[]):
    title=(x.get('title') or [''])[0]
    if title:results.append({'title':title[:230],'url':x.get('URL'),'doi':x.get('DOI'),'source':'Crossref (siêu dữ liệu; cần kiểm tra bản quyền toàn văn)'})
 except Exception:return {'results':[],'notice':'Nguồn trực tuyến tạm không phản hồi. Vui lòng dùng thư viện liên kết và bổ sung câu hỏi đã kiểm duyệt.'}
 return {'results':results,'notice':'Kết quả là liên kết tài liệu/siêu dữ liệu, KHÔNG tự động đưa câu hỏi vào đề khi chưa được giáo viên biên soạn và duyệt.'}
@APP.post('/api/assistant')
async def assistant(item:AssistantIn,u=Depends(user)):
 # Safe no-key tutor with honest limitations, optional server-side LLM.
 q=item.message.strip()
 api=os.getenv('OPENAI_API_KEY')
 if api:
  try:
   async with httpx.AsyncClient(timeout=18) as client:
    res=await client.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':'Bearer '+api},json={'model':os.getenv('AI_MODEL','gpt-4o-mini'),'temperature':0.2,'messages':[{'role':'system','content':'Bạn là trợ giảng Hóa THPT. Giải theo bước, kiểm tra cân bằng, số oxi hóa và dữ kiện. Trả lời bằng tiếng Việt. Nếu không chắc chắn, nói rõ; không bịa nguồn, không tạo ra hóa chất/thí nghiệm nguy hiểm. Gợi ý chứ không thay kết luận của giáo viên.'},{'role':'user','content':f'Lớp {item.grade}, chương {item.chapter}. Câu hỏi: {q}'}]})
    res.raise_for_status()
    return {'mode':'llm-server','answer':res.json()['choices'][0]['message']['content'],'verified':False,'disclaimer':'Nội dung AI cần giáo viên kiểm tra.'}
  except Exception:pass
 lines=[]
 qq=q.lower()
 if any(x in qq for x in ['hno3','nitric','nitrat']):lines=['HNO₃ có tính acid và tính oxi hóa mạnh.','Ví dụ với Cu và HNO₃ loãng: 3Cu + 8HNO₃ → 3Cu(NO₃)₂ + 2NO + 4H₂O.','Bẫy: không tự coi H₂ là sản phẩm khử của HNO₃ với Cu.']
 elif any(x in qq for x in ['oxi hóa','khử','electron']):lines=['Xác định số oxi hóa của nguyên tố trước và sau phản ứng.','Nguyên tố tăng số oxi hóa là chất khử; nguyên tố giảm số oxi hóa là chất oxi hóa.','Cân bằng electron nhường và nhận, sau đó kiểm tra số nguyên tử và điện tích.']
 elif any(x in qq for x in ['nh3','ammonia','amoni']):lines=['NH₃ là base yếu, trong nước: NH₃ + H₂O ⇌ NH₄⁺ + OH⁻.','NH₄⁺ phản ứng với OH⁻ khi đun nóng nhẹ tạo NH₃, dùng giấy quỳ ẩm nhận biết; không ngửi trực tiếp.']
 elif any(x in qq for x in ['h2so4','sulfuric','sulfate']):lines=['H₂SO₄ loãng có tính acid mạnh, H₂SO₄ đặc còn có tính háo nước và oxi hóa mạnh.','Ion sulfate có thể nhận biết bằng Ba²⁺: Ba²⁺ + SO₄²⁻ → BaSO₄↓.','Pha loãng H₂SO₄ đặc: rót từ từ acid vào nước.']
 else:lines=['Chế độ không API hỗ trợ các gợi ý HNO₃, NH₃, sulfuric acid, oxi hóa–khử và tra cứu học liệu.','Với bài toán khác, hãy nhập phương trình/dữ kiện và sử dụng mục tài liệu tham khảo; để hội thoại AI mở, cấu hình OPENAI_API_KEY trên máy chủ, không yêu cầu học sinh nhập khóa.']
 return {'mode':'rule-based','answer':'\n'.join(lines),'verified':False,'disclaimer':'Đây là trả lời từ bộ quy tắc chuyên môn giới hạn, không phải AI sinh nội dung.'}

APP.mount('/legacy',StaticFiles(directory=str(ROOT/'static/legacy'),html=True),name='legacy')
APP.mount('/assets',StaticFiles(directory=str(ROOT/'static'),html=False),name='assets')
@APP.get('/')
@APP.get('/index.html')
def index():return FileResponse(ROOT/'index.html')

# Secure DOCX export: authorization stays in HTTP header, never a URL query parameter.
from io import BytesIO
from fastapi.responses import StreamingResponse
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

@APP.get('/api/worksheets/{wid}/docx')
def worksheet_docx(wid:str,mode:str='student',u=Depends(user)):
 if mode not in ('student','teacher'):raise HTTPException(422,'mode: student / teacher')
 if mode=='teacher' and u['role']!='teacher':raise HTTPException(403)
 r=fetchone('SELECT * FROM worksheets WHERE id=:i',{'i':wid})
 if not r:raise HTTPException(404)
 w=json.loads(r['payload']);doc=Document()
 sec=doc.sections[0];sec.page_height=Cm(29.7);sec.page_width=Cm(21)
 sec.left_margin=sec.right_margin=Cm(2.25);sec.top_margin=sec.bottom_margin=Cm(2)
 styles=doc.styles
 normal=styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(12)
 normal.paragraph_format.space_after=Pt(7)
 for nm,size in [('Title',17),('Heading 1',14),('Heading 2',12)]:
  st=styles[nm];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(11,91,121)
 t=doc.add_paragraph(style='Title');t.alignment=WD_ALIGN_PARAGRAPH.CENTER;t.add_run(w['title'])
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.add_run('Lớp '+str(w['grade'])+' · '+w['chapter']+' · '+('BẢN GIÁO VIÊN' if mode=='teacher' else 'BẢN HỌC SINH')).bold=True
 if mode=='teacher':doc.add_paragraph('Tác giả giải pháp: Lê Bá Nhẫn – Trường THPT Hòn Đất')
 else:doc.add_paragraph('Họ tên: ........................................................   Lớp: ...................  Nhóm: ...........')
 doc.add_heading('I. MỤC TIÊU VÀ NHIỆM VỤ',level=1)
 doc.add_paragraph('Yêu cầu: nhận biết kiến thức cốt lõi; giải thích bản chất; vận dụng giải quyết câu hỏi phù hợp; đánh giá nguồn học liệu và làm việc nhóm.')
 if 'Jigsaw' in w['kind']:
  doc.add_paragraph('Jigsaw 6 nhóm – 2 nhiệm vụ A/B – 45 phút; 48 HS: nhóm 1, 3, 5 thực hiện A; nhóm 2, 4, 6 thực hiện B. Sau 12 phút chuyên gia, chuyển nhóm 2 phút và tạo 6 nhóm mới (4 A + 4 B/nhóm).')
  doc.add_paragraph('Tiến trình: Mở đầu 4 phút; chuyên gia 12 phút; chuyển nhóm 2 phút; mảnh ghép 12 phút; báo cáo và chuẩn hóa 4 phút; luyện tập 5 phút; vận dụng 6 phút.')
 else:doc.add_paragraph('Tiến trình gợi ý: Mở đầu 4 phút; hình thành kiến thức 30 phút; luyện tập 5 phút; vận dụng và đánh giá 6 phút.')
 doc.add_heading('II. TÍCH HỢP NĂNG LỰC SỐ (HỌC SINH)',level=1)
 tab=doc.add_table(rows=1,cols=3);tab.style='Light Shading Accent 1';tab.alignment=WD_TABLE_ALIGNMENT.CENTER
 for i,txt in enumerate(['Mã và năng lực','Nhiệm vụ học sinh','Minh chứng']):tab.rows[0].cells[i].text=txt
 for item in w['nls']:
  cells=tab.add_row().cells;cells[0].text=item['code']+' – '+item['name'];cells[1].text='Đánh giá, tạo hoặc kiểm chứng thông tin số phù hợp hoạt động';cells[2].text=item['evidence']
 doc.add_paragraph('Quy tắc: nêu nguồn, không đưa thông tin riêng tư lên công cụ AI; nếu thiếu Internet, thực hiện nhiệm vụ bằng bảng giấy hoặc tài liệu đã in.')
 doc.add_heading('III. PHIẾU NHIỆM VỤ',level=1)
 questions=w['questions']
 if not questions:doc.add_paragraph('Kho câu hỏi phù hợp đang trống. Giáo viên cần nhập và kiểm duyệt nội dung; chưa thể phát phiếu hoàn chỉnh.')
 half=(len(questions)+1)//2
 if 'Jigsaw' in w['kind']:
  groups=[('PHIẾU CHUYÊN GIA A',questions[:half]),('PHIẾU CHUYÊN GIA B',questions[half:])]
 else:groups=[('CÂU HỎI LUYỆN TẬP',questions)]
 answers={x['id']:x for x in w['answers']}
 for title,arr in groups:
  doc.add_heading(title,level=2)
  for i,q in enumerate(arr,1):
   head=doc.add_paragraph();head.add_run(f"Câu {i} – {q.get('level','Thông hiểu')} ({q['type']}). ").bold=True
   head.add_run(q.get('stem',''))
   if q['type']=='mcq':
    for j,opt in enumerate(q.get('options',[])):doc.add_paragraph('   '+chr(65+j)+'. '+opt)
   elif q['type']=='tf':
    for j,opt in enumerate(q.get('statements',[])):doc.add_paragraph('   '+chr(97+j)+') '+opt+'   ☐ Đúng    ☐ Sai')
   else:doc.add_paragraph('Bài làm: ..............................................................................................')
   if mode=='student':
    doc.add_paragraph('...............................................................................................................')
   else:
    ans=answers.get(q['id'],{})
    if q['type']=='mcq':correct='ABCD'[ans.get('correct',0)]
    elif q['type']=='tf':correct=', '.join('Đ' if x else 'S' for x in ans.get('correct',[]))
    elif q['type']=='essay':correct='Theo lời giải và tiêu chí giáo viên kiểm tra'
    else:correct=str(ans.get('correct',''))
    p=doc.add_paragraph();p.add_run('Đáp án: '+correct+'. ').bold=True;p.add_run(ans.get('explanation',''))
 if 'Jigsaw' in w['kind']:
  doc.add_heading('IV. NHÓM MẢNH GHÉP – TỔNG HỢP',level=1)
  doc.add_paragraph('Mỗi chuyên gia A/B thuyết trình 2–3 phút. Bạn cùng nhóm đặt câu hỏi kiểm tra chéo. Cùng giải quyết nhiệm vụ kết hợp kiến thức A và B; GV cần biên soạn tình huống tổng hợp theo bài trước khi in chính thức.')
  if mode=='student':
   doc.add_paragraph('Sơ đồ tư duy nhóm A: .................................................................................')
   doc.add_paragraph('Sơ đồ tư duy nhóm B: .................................................................................')
   doc.add_paragraph('Sơ đồ tư duy tổng hợp: .............................................................................')
  else:doc.add_paragraph('Giáo viên tổ chức chuẩn hóa kiến thức; tổng kết lỗi sai đã quan sát; đánh giá khả năng giải thích của từng cá nhân.')
 doc.add_heading('V. ĐÁNH GIÁ VÀ PHẢN HỒI',level=1)
 doc.add_paragraph('Kiến thức Hóa học: 60% · Hợp tác / thuyết trình: 25% · Năng lực số qua sản phẩm: 15%. Các tỉ lệ gợi ý, GV điều chỉnh phù hợp mục tiêu bài.')
 doc.add_paragraph('Tự đánh giá: Tôi đã hiểu ........................................ Tôi còn băn khoăn ........................................')
 p=doc.add_paragraph('Ghi chú: học liệu được tổng hợp từ ngân hàng câu hỏi dự án; cần giáo viên kiểm duyệt nội dung và công thức trước khi phát cho học sinh.');p.style='Caption'
 bf=BytesIO();doc.save(bf);bf.seek(0)
 filename='CHEM_MAP_Jigsaw_'+('GiaoVien' if mode=='teacher' else 'HocSinh')+'_'+wid+'.docx'
 return StreamingResponse(bf,media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',headers={'Content-Disposition':f'attachment; filename="{filename}"'})

class SourceQuestionIn(BaseModel):
 compound:str=Field(min_length=2,max_length=100)
 grade:int=Field(ge=10,le=12)
 chapter:str
 lesson_id:str|None=None

@APP.post('/api/questions/suggest-online')
async def source_question(item:SourceQuestionIn,u=Depends(teacher)):
 """Retrieve a chemical fact from PubChem and build a teacher-review draft.
 Do not copy any question bank or publish automatically.
 """
 from urllib.parse import quote
 target=quote(item.compound,safe='')
 url=f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{target}/property/MolecularFormula,MolecularWeight/JSON'
 try:
  async with httpx.AsyncClient(timeout=10,follow_redirects=False) as cli:
   res=await cli.get(url,headers={'User-Agent':'CHEM-MAP-TUTOR-EDU/3.0'})
   res.raise_for_status()
   row=res.json()['PropertyTable']['Properties'][0]
   formula=row['MolecularFormula']
   cid=row.get('CID')
 except Exception as ex:
  raise HTTPException(502,'Không lấy được dữ liệu PubChem; vui lòng thử lại hoặc bổ sung câu hỏi thủ công.')
 # Use a fixed bounded family of candidate distractors; do not assert their source chemistry.
 pool=['NH3','HNO3','H2SO4','SO2','CO2','H2O','C2H6O','C2H4O2','CH4','O2','N2','HCl','NaCl','C6H12O6','C2H4','H2O2']
 distractors=[f for f in pool if f!=formula][:3]
 answers=distractors+[formula];random.SystemRandom().shuffle(answers)
 correct=answers.index(formula)
 q={'id':uid('Q'),'grade':item.grade,'chapter':item.chapter,'lesson_id':item.lesson_id,'type':'mcq','level':'Nhận biết','stem':'Công thức phân tử của '+item.compound+' theo hồ sơ PubChem là gì?','options':answers,'correct':correct,'explanation':f'Theo dữ liệu PubChem CID {cid}, công thức phân tử: {formula}. Phải đối chiếu danh pháp, đồng phân và điều kiện khi chọn chất; đây là câu nhận biết dữ kiện, không thay câu vận dụng.','skill':'Khai thác và kiểm chứng dữ liệu hóa học số','source':'PubChem PUG REST; https://pubchem.ncbi.nlm.nih.gov/compound/'+str(cid),'status':'draft','distractors':{str(i):{'code':'K01','hypothesis':'Có thể nhầm lẫn công thức chất khác; cần phỏng vấn thêm.'} for i in range(4) if i!=correct},'license_note':'Câu hỏi tự biên soạn từ dữ liệu thực tế PubChem; cần giáo viên duyệt đáp án và bối cảnh.'}
 commit('INSERT INTO questions(id,grade,chapter,lesson_id,type,level,status,payload,created_at) VALUES (:id,:g,:c,:l,:t,:v,:s,:p,:at)',{'id':q['id'],'g':item.grade,'c':item.chapter,'l':item.lesson_id,'t':'mcq','v':'Nhận biết','s':'draft','p':json.dumps(q,ensure_ascii=False),'at':now()})
 return {'question':q,'message':'Đã lấy công thức phân tử từ PubChem và lưu câu hỏi bản nháp. Giáo viên kiểm duyệt trước khi đưa vào đề.'}

import csv
from fastapi.responses import Response
@APP.get('/api/analytics/export.csv')
def analytics_export(u=Depends(teacher)):
 rows=fetchall('SELECT p.name AS student,c.name AS class_name,e.title AS exam,a.score,a.graded,a.created_at FROM attempts a JOIN people p ON p.id=a.student_id JOIN exams e ON e.id=a.exam_id LEFT JOIN classes c ON c.id=a.class_id ORDER BY a.created_at DESC')
 s=__import__('io').StringIO();w=csv.writer(s);w.writerow(['student','class','exam','score_10','graded','submitted_at_utc'])
 for x in rows:w.writerow([x['student'],x['class_name'],x['exam'],x['score'],x['graded'],x['created_at']])
 return Response('\ufeff'+s.getvalue(),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="CHEM_MAP_results.csv"'})


# Student-first practice: no account required for practice; only teacher-approved or vetted demo items.
# Never expose answers in /pool; /check reveals the explanation only for the answered item.
class PracticeCheckIn(BaseModel):
 id:str=Field(min_length=3,max_length=90)
 answer:Any=None

def _optional_student(req:Request):
 if not req.headers.get('Authorization'):return None
 try:
  u=user(req)
  return u if u.get('role')=='student' else None
 except HTTPException:return None

def _scope_catalog(grade:int,chapter:str='all'):
 if grade not in (10,11,12):raise HTTPException(422,'Chỉ hỗ trợ lớp 10, 11, 12')
 matched=[c for c in CURR['grades'][str(grade)] if chapter=='all' or c['title']==chapter]
 if not matched:raise HTTPException(404,'Không có chương trong danh mục KNTT')
 with engine.connect() as con:
  records=[dict(r) for r in con.execute(text('SELECT id,chapter,lesson_id,type,level,status FROM questions WHERE grade=:g'),{'g':grade}).mappings()]
 result=[]
 for ch in matched:
  rows=[r for r in records if r['chapter']==ch['title']]
  live=[r for r in rows if r['status'] in ('approved','demo')]
  result.append({'id':ch['id'],'number':ch['number'],'title':ch['title'],
   'approved':len(live),'waiting':len([r for r in rows if r['status'] not in ('approved','demo')]),
   'chapter_only':len([r for r in rows if not r['lesson_id']]),
   'lessons':[{'id':l['id'],'number':l['number'],'title':l['title'],'review':l['review'],
    'approved':len([r for r in live if r['lesson_id']==l['id']]),
    'waiting':len([r for r in rows if r['lesson_id']==l['id'] and r['status'] not in ('approved','demo')])} for l in ch['lessons']]})
 return result

@APP.get('/api/study/catalog')
def study_catalog(grade:int=11,chapter:str='all'):
 return {'grade':grade,'chapters':_scope_catalog(grade,chapter),
  'notice':'Chỉ câu đã được giáo viên kiểm duyệt hoặc câu mẫu mới được tự luyện. Số đang chờ duyệt không phải câu khả dụng.'}

@APP.get('/api/study/availability')
def study_availability(grade:int=11,chapter:str='all',lesson_id:str='',level:str='all',kind:str='all'):
 # Counts reflect the actual active pool (never include ungraded essays).
 if grade not in (10,11,12):raise HTTPException(422,'Lớp không hợp lệ')
 if chapter=='all':return {'available':0,'waiting':0,'notice':'Hãy chọn một chương để tự luyện'}
 valid=[c for c in CURR['grades'][str(grade)] if c['title']==chapter]
 if not valid:raise HTTPException(422,'Chương không thuộc khối lớp đã chọn')
 if lesson_id and lesson_id not in {l['id'] for l in valid[0]['lessons']}:raise HTTPException(422,'Bài không thuộc chương đã chọn')
 if level not in ('all','Nhận biết','Thông hiểu','Vận dụng','Vận dụng cao'):raise HTTPException(422,'Mức độ chưa được hỗ trợ')
 if kind not in ('all','mcq','tf','short'):raise HTTPException(422,'Dạng câu hỏi chưa được hỗ trợ')
 approved=_filter(grade,chapter,lesson_id,approved=True)
 with engine.connect() as con:
  raw=[dict(z) for z in con.execute(text('SELECT lesson_id,type,level,status FROM questions WHERE grade=:g AND chapter=:ch'),{'g':grade,'ch':chapter}).mappings()]
 def eligible(q):return (not lesson_id or q['lesson_id']==lesson_id) and q['type'] in ('mcq','tf','short') and (level=='all' or q['level']==level) and (kind=='all' or q['type']==kind)
 return {'grade':grade,'chapter':chapter,'lesson_id':lesson_id,'level':level,'kind':kind,
  'available':len([q for q in approved if eligible(q)]),
  'waiting':len([q for q in raw if q['status'] not in ('demo','approved') and eligible(q)]),
  'note':'Số câu có thể luyện theo bài, mức độ và hình thức, không gồm tự luận chấm tay.'}

@APP.get('/api/study/pool')
def study_pool(grade:int=11,chapter:str='all',lesson_id:str='',level:str='all',kind:str='all',limit:int=Query(10,ge=1,le=30)):
 if grade not in (10,11,12):raise HTTPException(422,'Khối lớp không hợp lệ')
 if chapter!='all' and not any(ch['title']==chapter for ch in CURR['grades'][str(grade)]):raise HTTPException(422,'Chương không thuộc lớp')
 if level not in ('all','Nhận biết','Thông hiểu','Vận dụng','Vận dụng cao') or kind not in ('all','mcq','tf','short'):raise HTTPException(422,'Bộ lọc không hợp lệ')
 if lesson_id and not any(l['id']==lesson_id and (chapter=='all' or ch['title']==chapter)
  for ch in CURR['grades'][str(grade)] for l in ch['lessons']):raise HTTPException(422,'Bài học không thuộc chương/lớp')
 rows=_filter(grade,chapter,lesson_id,approved=True)
 if level!='all':rows=[r for r in rows if r['level']==level]
 if kind!='all':rows=[r for r in rows if r['type']==kind]
 # For active practice, essay items need manual evaluation, so exclude by default.
 if kind=='all':rows=[r for r in rows if r['type']!='essay']
 if not rows:return {'total_available':0,'questions':[],'notice':'Chưa có câu đã duyệt thuộc phạm vi này. Chọn Ôn tập cả chương hoặc đề nghị giáo viên kiểm duyệt.'}
 chosen=secrets.SystemRandom().sample(rows,min(limit,len(rows)))
 return {'total_available':len(rows),'questions':[_public_question(json.loads(r['payload'])) for r in chosen],
  'notice':'Tự luyện không phải kiểm tra chính thức. Trả lời từng câu để mở lời giải và hướng khắc phục.'}

@APP.post('/api/study/check')
def study_check(item:PracticeCheckIn,req:Request):
 r=fetchone('SELECT grade,chapter,lesson_id,level,status,payload FROM questions WHERE id=:id',{'id':item.id})
 if not r or r['status'] not in ('approved','demo'):raise HTTPException(404,'Câu hỏi chưa được phát hành để tự luyện')
 q=json.loads(r['payload']);ans=item.answer
 if q['type']=='essay':
  result={'correct':None,'pending':True,'right':None,'points':None,'diagnostics':[],
   'explanation':q.get('explanation','Cần giáo viên đánh giá bài tự luận.')}
 else:
  j=_judge(q,ans)
  result={'correct':j['correct'],'pending':False,'right':j.get('right'), 'points':j['points'],
   'diagnostics':j.get('diagnostics',[]),'explanation':q.get('explanation','Chưa có lời giải.')}
 student=_optional_student(req)
 if student and result['correct'] is not None:
  commit('INSERT INTO study_events (id,student_id,question_id,lesson_id,grade,chapter,level,is_correct,created_at) VALUES (:id,:s,:q,:l,:g,:c,:lv,:ok,:t)',
   {'id':uid('learn'),'s':student['sub'],'q':item.id,'l':r['lesson_id'],'g':r['grade'],'c':r['chapter'],'lv':r['level'],'ok':int(bool(result['correct'])),'t':now()})
 result['saved']=bool(student and result['correct'] is not None)
 return result

@APP.get('/api/study/progress')
def study_progress(u=Depends(user)):
 if u['role']!='student':raise HTTPException(403,'Chỉ dành cho học sinh')
 rows=fetchall('SELECT grade,chapter,lesson_id,COUNT(*) AS attempts,SUM(is_correct) AS correct FROM study_events WHERE student_id=:s GROUP BY grade,chapter,lesson_id ORDER BY grade,chapter',{'s':u['sub']})
 return {'total_attempts':sum(r['attempts'] for r in rows),'correct':sum(r['correct'] for r in rows),'by_topic':rows}
