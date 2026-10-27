"""EduPlan school workflow: persistent class/course/assignment/online/paper grading & analytics.
Runs locally with SQLite. Keep teacher private keys only in teacher-authenticated responses.
"""
from __future__ import annotations
import csv, io, json, os, secrets, hashlib, random, sqlite3, time
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, Response, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

DB_PATH=Path(os.environ.get('EDUPLAN_DATA_DIR',str(Path(__file__).resolve().parent)))/'edup_education.sqlite3'
SESSIONS={}   # student bearer tokens expire after 8h; restart requires re-login
LOGIN_FAILURES={}  # in-memory IP throttling to limit code guessing
CTX={}

def db():
    conn=sqlite3.connect(str(DB_PATH),timeout=20)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=20000')
    return conn

def initialize():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS classes(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, grade INTEGER NOT NULL, school_year TEXT DEFAULT '2026-2027', created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER NOT NULL REFERENCES classes(id), full_name TEXT NOT NULL, access_code TEXT NOT NULL UNIQUE, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER NOT NULL REFERENCES classes(id), title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS assignments(id INTEGER PRIMARY KEY AUTOINCREMENT, class_id INTEGER NOT NULL REFERENCES classes(id), course_id INTEGER REFERENCES courses(id), title TEXT NOT NULL, kind TEXT NOT NULL, grade INTEGER NOT NULL, chapter INTEGER, lesson INTEGER, part TEXT NOT NULL DEFAULT 'II', level TEXT, competency TEXT, count INTEGER NOT NULL, duration_minutes INTEGER NOT NULL DEFAULT 0, due_at INTEGER, seed TEXT NOT NULL, question_ids TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY AUTOINCREMENT, assignment_id INTEGER NOT NULL REFERENCES assignments(id), student_id INTEGER NOT NULL REFERENCES students(id), method TEXT NOT NULL, question_ids TEXT NOT NULL, started_at INTEGER NOT NULL, submitted_at INTEGER, answers TEXT, score INTEGER, possible INTEGER, UNIQUE(assignment_id,student_id));
        CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
        CREATE INDEX IF NOT EXISTS idx_attempt_assign ON attempts(assignment_id);
        CREATE INDEX IF NOT EXISTS idx_assign_class ON assignments(class_id);
        ''')

def dt_epoch(v):
    if not v:return None
    try:
        dt=datetime.fromisoformat(v.replace('Z','+00:00'))
        if not dt.tzinfo: dt=dt.replace(tzinfo=timezone(timedelta(hours=7)))
        return int(dt.timestamp())
    except Exception:raise HTTPException(400,'Ngày hạn nộp phải là định dạng ISO 8601.')

def obj(row):return dict(row) if row is not None else None

def student_auth(authorization:str|None=Header(default=None)):
    if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Học sinh cần đăng nhập bằng mã truy cập riêng.')
    tok=authorization[7:];entry=SESSIONS.get(tok)
    if not entry or entry['expires']<time.time():raise HTTPException(401,'Phiên đăng nhập hết hạn. Hãy đăng nhập lại.')
    return entry['student_id']

class ClassCreate(BaseModel):
    title:str=Field(min_length=2,max_length=120)
    grade:int
    school_year:str='2026-2027'
class StudentCreate(BaseModel):
    class_id:int
    names:list[str]=Field(min_length=1,max_length=100)
class CourseCreate(BaseModel):
    class_id:int
    title:str=Field(min_length=2,max_length=150)
    description:str=''
class LoginReq(BaseModel):
    access_code:str
class AssignmentCreate(BaseModel):
    class_id:int
    course_id:int|None=None
    title:str=Field(min_length=2,max_length=160)
    kind:str='homework'
    grade:int
    chapter:int|None=None
    lesson:int|None=None
    level:str|None=None
    competency:str|None=None
    count:int=Field(default=5,ge=1,le=30)
    duration_minutes:int=Field(default=0,ge=0,le=240)
    due_at:str|None=None
class OnlineStart(BaseModel):
    assignment_id:int
class OnlineSubmit(BaseModel):
    assignment_id:int
    answers:dict[str,list[bool|None]]
class PaperSubmit(BaseModel):
    assignment_id:int
    student_id:int
    answers:dict[str,list[bool|None]]


def assign_json(row):
    d=obj(row)
    if not d:return None
    d.pop('seed',None);d.pop('question_ids',None)
    return d

def key_fingerprint(assignment_id, student_id, seed):
    return int(hashlib.sha256(f'{assignment_id}:{student_id}:{seed}'.encode()).hexdigest(),16)

def pick_for_student(assignment, student_id):
    selected=json.loads(assignment['question_ids'])
    random.Random(key_fingerprint(assignment['id'],student_id,assignment['seed'])).shuffle(selected)
    return selected[:assignment['count']]

def read_result(assignment,ids,answers):
    with CTX['lock']:
        bank={q['id']:q for q in CTX['questions']}
    points=0;max_points=0;detail=[];wrong=[]
    for pos,ident in enumerate(ids):
        q=bank.get(ident)
        if not q or not CTX['gradeable'](q):raise HTTPException(409,'Ngân hàng đã thay đổi hoặc câu hỏi mất khóa; cần khôi phục dữ liệu trước khi chấm.')
        submitted=answers.get(ident)
        if not isinstance(submitted,list) or len(submitted)!=4 or any(type(a)!=bool for a in submitted):raise HTTPException(400,f'Câu {pos+1} chưa trả lời đủ bốn ý Đúng/Sai.')
        rows=[];p=0
        for i in range(4):
            correct=q['correct'][i];yes=correct==submitted[i];p+=int(yes)
            rows.append({'label':'abcd'[i],'text':CTX['safe_html'](q['statements'][i]),'selected':submitted[i],'correct':correct,'isCorrect':yes,'explanation':CTX['safe_html'](q['explanations'][i])})
        points+=p;max_points+=4
        if p<4:wrong.append(ident)
        detail.append({'id':ident,'number':pos+1,'sourceNumber':q.get('sourceNumber'),'lessonName':q.get('lessonName'),'stemHtml':CTX['safe_html'](q.get('stemHtml')),'mediaHtml':CTX['safe_html'](q.get('mediaHtml')),'solutionIntroHtml':CTX['safe_html'](q.get('solutionIntroHtml')),'points':p,'items':rows})
    return {'correct':points,'total':max_points,'percent':round(100*points/max_points,1) if max_points else 0,'questions':detail,'wrongIds':wrong}


def setup(app, teacher_dep, questions, gradeable, public, lock, safe_html):
    CTX.update({'questions':questions,'gradeable':gradeable,'public':public,'lock':lock,'safe_html':safe_html})
    initialize()
    router=APIRouter(prefix='/api/workflow',tags=['EduPlan workflows'])

    @router.get('/teacher/classes')
    def teacher_classes(_=Depends(teacher_dep)):
        with db() as c:
            return {'classes':[dict(r) for r in c.execute('SELECT c.*, (SELECT COUNT(*) FROM students s WHERE s.class_id=c.id) student_count FROM classes c ORDER BY c.id DESC')]}

    @router.post('/teacher/classes')
    def create_class(req:ClassCreate,_=Depends(teacher_dep)):
        if req.grade not in (10,11,12):raise HTTPException(400,'Lớp chỉ được thuộc khối 10, 11 hoặc 12.')
        with db() as c:
            cur=c.execute('INSERT INTO classes(title,grade,school_year,created_at) VALUES(?,?,?,?)',(req.title.strip(),req.grade,req.school_year,int(time.time())))
            return {'id':cur.lastrowid,'title':req.title}

    @router.get('/teacher/students')
    def teacher_students(class_id:int|None=None,_=Depends(teacher_dep)):
        with db() as c:
            rows=c.execute('SELECT s.*,c.title AS class_title FROM students s JOIN classes c ON c.id=s.class_id WHERE (? IS NULL OR s.class_id=?) ORDER BY s.id DESC',(class_id,class_id)).fetchall()
        return {'students':[dict(r) for r in rows]}

    @router.post('/teacher/students')
    def create_students(req:StudentCreate,_=Depends(teacher_dep)):
        names=[s.strip() for s in req.names if 1<len(s.strip())<=120]
        if not names:raise HTTPException(400,'Cần tên học sinh hợp lệ.')
        with db() as c:
            if not c.execute('SELECT id FROM classes WHERE id=?',(req.class_id,)).fetchone():raise HTTPException(404,'Lớp không tồn tại.')
            users=[]
            for name in names:
                code=secrets.token_hex(10).upper() # random 80-bit student access code
                c.execute('INSERT INTO students(class_id,full_name,access_code,created_at) VALUES(?,?,?,?)',(req.class_id,name,code,int(time.time())))
                users.append({'id':c.execute('SELECT last_insert_rowid()').fetchone()[0],'name':name,'access_code':code})
            return {'created':len(users),'students':users}

    @router.get('/teacher/courses')
    def list_courses(class_id:int|None=None,_=Depends(teacher_dep)):
        with db() as c:rows=c.execute('SELECT * FROM courses WHERE (? IS NULL OR class_id=?) ORDER BY id DESC',(class_id,class_id)).fetchall()
        return {'courses':[dict(r) for r in rows]}

    @router.post('/teacher/courses')
    def create_course(req:CourseCreate,_=Depends(teacher_dep)):
        with db() as c:
            if not c.execute('SELECT id FROM classes WHERE id=?',(req.class_id,)).fetchone():raise HTTPException(404,'Không tìm thấy lớp.')
            n=c.execute('INSERT INTO courses(class_id,title,description,created_at) VALUES(?,?,?,?)',(req.class_id,req.title.strip(),req.description.strip(),int(time.time())))
            return {'id':n.lastrowid,'title':req.title}

    @router.get('/teacher/assignments')
    def assignments(class_id:int|None=None,_=Depends(teacher_dep)):
        with db() as c:
            rows=c.execute('''SELECT a.*,c.title class_title,co.title course_title,
             (SELECT COUNT(*) FROM attempts t WHERE t.assignment_id=a.id AND t.submitted_at IS NOT NULL) submitted,
             (SELECT COUNT(*) FROM students s WHERE s.class_id=a.class_id) student_count
             FROM assignments a JOIN classes c ON a.class_id=c.id LEFT JOIN courses co ON co.id=a.course_id
             WHERE (? IS NULL OR a.class_id=?) ORDER BY a.id DESC''',(class_id,class_id)).fetchall()
        return {'assignments':[assign_json(x) for x in rows]}

    @router.post('/teacher/assignments')
    def create_assignment(req:AssignmentCreate,_=Depends(teacher_dep)):
        if req.kind not in ('homework','quiz','exam','review'):raise HTTPException(400,'Loại bài không hợp lệ.')
        with db() as c:
            cl=c.execute('SELECT * FROM classes WHERE id=?',(req.class_id,)).fetchone()
            if not cl:raise HTTPException(404,'Lớp không tồn tại.')
            if cl['grade']!=req.grade:raise HTTPException(400,'Khối lớp của đề phải trùng với khối của lớp được giao.')
            if req.course_id is not None and not c.execute('SELECT 1 FROM courses WHERE id=? AND class_id=?',(req.course_id,req.class_id)).fetchone():raise HTTPException(400,'Khóa học không thuộc lớp đã chọn.')
        with lock:
            pool=[q for q in questions if gradeable(q) and q.get('grade')==req.grade and (req.chapter is None or q.get('chapter')==req.chapter) and (req.lesson is None or q.get('lesson')==req.lesson) and (not req.level or q.get('levelSuggested')==req.level) and (not req.competency or q.get('competencySuggested')==req.competency)]
        if len(pool)<req.count:raise HTTPException(400,f'Phạm vi chọn chỉ có {len(pool)} câu Đúng/Sai đủ khóa. Hãy giảm số lượng hoặc mở rộng chương/bài/mức độ.')
        # Snapshot ids are stable for the assignment; order varies by student deterministically
        seed=secrets.token_urlsafe(16)
        base_ids=[x['id'] for x in sorted(pool,key=lambda q:q['id'])]
        random.Random(seed).shuffle(base_ids)
        chosen=base_ids[:req.count]
        with db() as c:
            n=c.execute('''INSERT INTO assignments(class_id,course_id,title,kind,grade,chapter,lesson,level,competency,count,duration_minutes,due_at,seed,question_ids,created_at)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(req.class_id,req.course_id,req.title.strip(),req.kind,req.grade,req.chapter,req.lesson,req.level,req.competency,req.count,req.duration_minutes,dt_epoch(req.due_at),seed,json.dumps(chosen),int(time.time())))
            return {'id':n.lastrowid,'count':req.count,'question_pool':len(pool),'mixed':True}

    @router.get('/teacher/assignment/{assignment_id}/preview')
    def preview(assignment_id:int,_=Depends(teacher_dep)):
        with db() as c:a=c.execute('SELECT * FROM assignments WHERE id=?',(assignment_id,)).fetchone()
        if not a:raise HTTPException(404,'Không thấy đề.')
        with lock:idx={q['id']:q for q in questions}
        return {'assignment':assign_json(a),'questions':[public(idx[i]) for i in json.loads(a['question_ids']) if i in idx],'note':'Đề mẫu; khi học sinh tham gia hệ thống sẽ trộn thứ tự theo mã học sinh.'}

    @router.post('/student/login')
    def student_login(req:LoginReq,request:Request):
        # One process, basic per-IP throttle. Use a platform firewall for larger deployments.
        ip=request.client.host if request.client else 'unknown'
        now=time.time();attempts=[x for x in LOGIN_FAILURES.get(ip,[]) if now-x<600]
        if len(attempts)>=15:raise HTTPException(429,'Có quá nhiều lần đăng nhập sai; thử lại sau 10 phút.')
        LOGIN_FAILURES[ip]=attempts
        with db() as c:
            s=c.execute('SELECT s.id,s.full_name,s.class_id,c.title class_title,c.grade FROM students s JOIN classes c ON c.id=s.class_id WHERE s.access_code=?',(req.access_code.strip().upper(),)).fetchone()
        if not s:
            LOGIN_FAILURES[ip].append(now)
            raise HTTPException(401,'Mã học sinh không đúng.')
        LOGIN_FAILURES.pop(ip,None)
        token=secrets.token_urlsafe(32);SESSIONS[token]={'student_id':s['id'],'expires':time.time()+8*3600}
        return {'token':token,'profile':dict(s)}

    @router.get('/student/dashboard')
    def student_dashboard(student_id:int=Depends(student_auth)):
        with db() as c:
            s=c.execute('SELECT s.id,s.full_name,s.class_id,c.title class_title,c.grade FROM students s JOIN classes c ON c.id=s.class_id WHERE s.id=?',(student_id,)).fetchone()
            courses=[dict(r) for r in c.execute('SELECT * FROM courses WHERE class_id=?',(s['class_id'],))]
            rows=c.execute('''SELECT a.id,a.course_id,a.title,a.kind,a.grade,a.chapter,a.lesson,a.count,a.duration_minutes,a.due_at,
              t.started_at,t.submitted_at,t.score,t.possible, t.method
              FROM assignments a LEFT JOIN attempts t ON a.id=t.assignment_id AND t.student_id=?
              WHERE a.class_id=? ORDER BY a.created_at DESC''',(student_id,s['class_id'])).fetchall()
            return {'profile':dict(s),'courses':courses,'assignments':[dict(r) for r in rows]}

    @router.post('/student/start')
    def student_start(req:OnlineStart,student_id:int=Depends(student_auth)):
        with db() as c:
            a=c.execute('SELECT * FROM assignments WHERE id=?',(req.assignment_id,)).fetchone()
            s=c.execute('SELECT * FROM students WHERE id=?',(student_id,)).fetchone()
            if not a or a['class_id']!=s['class_id']:raise HTTPException(403,'Bài giao không thuộc lớp của học sinh.')
            t=c.execute('SELECT * FROM attempts WHERE assignment_id=? AND student_id=?',(a['id'],student_id)).fetchone()
            if t and t['submitted_at']:raise HTTPException(409,'Học sinh đã hoàn thành bài giao này.')
            if a['due_at'] and int(time.time())>a['due_at']:raise HTTPException(403,'Bài đã hết hạn nộp.')
            if not t:
                ids=pick_for_student(a,student_id)
                c.execute('INSERT INTO attempts(assignment_id,student_id,method,question_ids,started_at) VALUES(?,?,?,?,?)',(a['id'],student_id,'online',json.dumps(ids),int(time.time())))
                started=int(time.time())
            else:
                if t['method']!='online':raise HTTPException(409,'Bài đã thực hiện bằng phiếu giấy.')
                ids=json.loads(t['question_ids']);started=t['started_at']
            if a['duration_minutes'] and time.time()>started+a['duration_minutes']*60:raise HTTPException(403,'Đã hết thời gian làm bài.')
        with lock:idx={q['id']:q for q in questions}
        return {'assignment':assign_json(a),'questions':[public(idx[i]) for i in ids if i in idx],'started_at':started,'server_time':int(time.time())}

    @router.post('/student/submit')
    def student_submit(req:OnlineSubmit,student_id:int=Depends(student_auth)):
        with db() as c:
            a=c.execute('SELECT * FROM assignments WHERE id=?',(req.assignment_id,)).fetchone()
            t=c.execute('SELECT * FROM attempts WHERE assignment_id=? AND student_id=?',(req.assignment_id,student_id)).fetchone()
            if not a or not t or t['submitted_at'] or t['method']!='online':raise HTTPException(409,'Phiên làm bài không tồn tại hoặc đã nộp.')
            if a['due_at'] and time.time()>a['due_at']:raise HTTPException(403,'Đã quá hạn nộp bài.')
            # 2min network tolerance; no auto-expiration submission for paper grading
            if a['duration_minutes'] and time.time()>t['started_at']+a['duration_minutes']*60+120:raise HTTPException(403,'Bài đã hết thời gian làm.')
            ids=json.loads(t['question_ids'])
            out=read_result(a,ids,req.answers)
            c.execute('''UPDATE attempts SET submitted_at=?,answers=?,score=?,possible=? WHERE id=? AND submitted_at IS NULL''',(int(time.time()),json.dumps(req.answers),out['correct'],out['total'],t['id']))
            return {'assignment':assign_json(a),**out}

    @router.get('/student/result/{assignment_id}')
    def student_result(assignment_id:int,student_id:int=Depends(student_auth)):
        with db() as c:
            a=c.execute('SELECT * FROM assignments WHERE id=?',(assignment_id,)).fetchone()
            t=c.execute('SELECT * FROM attempts WHERE assignment_id=? AND student_id=?',(assignment_id,student_id)).fetchone()
        if not a or not t or not t['submitted_at']:raise HTTPException(404,'Chưa có kết quả bài này.')
        return {'assignment':assign_json(a),'method':t['method'],**read_result(a,json.loads(t['question_ids']),json.loads(t['answers']))}

    @router.get('/teacher/paper/{assignment_id}')
    def paper_template(assignment_id:int, _=Depends(teacher_dep)):
        with db() as c:a=c.execute('SELECT * FROM assignments WHERE id=?',(assignment_id,)).fetchone()
        if not a:raise HTTPException(404,'Không tìm thấy đề.')
        import html
        questions_count=a['count']
        rows=''.join(f'<tr><td>{i}</td>'+''.join('<td>○ Đ &nbsp; ○ S</td>' for k in 'abcd')+'</tr>' for i in range(1,questions_count+1))
        body=f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Phiếu trả lời · {html.escape(a['title'])}</title>
        <style>body{{font-family:'Times New Roman',serif;margin:22mm;color:#111}}h1,h2{{text-align:center}}table{{border-collapse:collapse;width:100%;margin-top:20px}}td,th{{border:1px solid #333;padding:9px 5px;text-align:center}}@media print{{button{{display:none}}}}</style></head><body>
        <h2>PHIẾU TRẢ LỜI ĐÚNG / SAI – HÓA HỌC</h2><h3>{html.escape(a['title'])} · Mã đề {assignment_id}</h3>
        <p>Họ và tên: ............................................. Mã học sinh: ..................... Lớp: ......................</p>
        <p>Khoanh 1 ô Đ hoặc S cho mỗi ý. Đây là phiếu đánh dấu để giáo viên nhập chấm; KHÔNG hỗ trợ nhận dạng ảnh tự động.</p>
        <table><tr><th>Câu</th><th>a)</th><th>b)</th><th>c)</th><th>d)</th></tr>{rows}</table><p>Chữ ký học sinh: ......................................</p><button onclick="window.print()">In phiếu</button></body></html>'''
        return HTMLResponse(body)

    @router.get('/teacher/paper/exam/{assignment_id}/{student_id}')
    def printable_exam(assignment_id:int,student_id:int,_=Depends(teacher_dep)):
        import html
        from bs4 import BeautifulSoup
        with db() as c:
            a=c.execute('SELECT * FROM assignments WHERE id=?',(assignment_id,)).fetchone()
            student=c.execute('SELECT * FROM students WHERE id=?',(student_id,)).fetchone()
        if not a or not student or a['class_id']!=student['class_id']:
            raise HTTPException(404,'Không tìm thấy mã đề hoặc học sinh hợp lệ.')
        ids=pick_for_student(a,student_id)
        with lock: idx={q['id']:q for q in questions}
        allowed={'p','b','strong','i','em','u','sub','sup','br','table','thead','tbody','tr','th','td','ul','ol','li','div','span','img'}
        def clean_html(raw):
            soup=BeautifulSoup(str(raw or ''),'html.parser')
            for tag in list(soup.find_all(True)):
                if tag.name not in allowed:
                    tag.unwrap()
                    continue
                for attr in list(tag.attrs):
                    val=tag.get(attr)
                    if tag.name=='img' and attr=='src' and isinstance(val,str) and val.startswith('/media/') and '/' not in val[len('/media/'):]:continue
                    if attr in ('colspan','rowspan') and str(val).isdigit():continue
                    del tag.attrs[attr]
                if tag.name=='img' and not tag.get('src'):tag.decompose()
            return str(soup)
        blocks=[]
        for i,ident in enumerate(ids):
            q=idx.get(ident)
            if not q:continue
            content=clean_html(q.get('stemHtml'))+clean_html(q.get('mediaHtml'))
            statements=''.join(f'<p><b>{"abcd"[k]})</b> {clean_html(st)}</p>' for k,st in enumerate(q.get('statements',[])))
            blocks.append(f'<section class="question"><h3>Câu {i+1}.</h3>{content}{statements}</section>')
        title=html.escape(a['title'])
        student_name=html.escape(student['full_name'])
        markup=f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Đề kiểm tra - {title}</title>
        <style>body{{font-family:'Times New Roman',serif;max-width:190mm;margin:12mm auto;font-size:13pt;line-height:1.36}}
        h1{{text-align:center;font-size:20pt}}h2{{text-align:center;font-size:14pt}}h3{{font-size:13pt}}
        .question{{margin:18px 0;break-inside:avoid}}img{{max-width:100%;height:auto}}table{{border-collapse:collapse;max-width:100%}}
        td,th{{border:1px solid #888;padding:5px}}.tools{{margin:12px}}
        @media print{{.tools{{display:none}}body{{margin:0}}}}</style></head>
        <body><button class="tools" onclick="window.print()">In đề</button><h1>ĐỀ KIỂM TRA HÓA HỌC</h1><h2>{title}</h2>
        <p>Học sinh: <b>{student_name}</b> · Mã đề: {assignment_id}-{student_id} · Số câu: {a['count']}</p>
        <p><i>Hãy đánh dấu Đúng hoặc Sai cho từng ý trên phiếu trả lời.</i></p>{''.join(blocks)}</body></html>'''
        return HTMLResponse(markup)

    @router.post('/teacher/paper/grade')
    def paper_grade(req:PaperSubmit,_=Depends(teacher_dep)):
        with db() as c:
            a=c.execute('SELECT * FROM assignments WHERE id=?',(req.assignment_id,)).fetchone()
            s=c.execute('SELECT * FROM students WHERE id=?',(req.student_id,)).fetchone()
            if not a or not s or a['class_id']!=s['class_id']:raise HTTPException(403,'Học sinh không thuộc lớp được giao.')
            if c.execute('SELECT id FROM attempts WHERE assignment_id=? AND student_id=?',(a['id'],s['id'])).fetchone():raise HTTPException(409,'Học sinh đã có lượt làm bài; không ghi đè kết quả.')
            ids=pick_for_student(a,s['id'])
            result=read_result(a,ids,req.answers)
            c.execute('INSERT INTO attempts(assignment_id,student_id,method,question_ids,started_at,submitted_at,answers,score,possible) VALUES(?,?,?,?,?,?,?,?,?)',(a['id'],s['id'],'paper',json.dumps(ids),int(time.time()),int(time.time()),json.dumps(req.answers),result['correct'],result['total']))
        return result

    @router.get('/teacher/paper/keys/{assignment_id}/{student_id}')
    def paper_keys(assignment_id:int,student_id:int,_=Depends(teacher_dep)):
        with db() as c:
            a=c.execute('SELECT * FROM assignments WHERE id=?',(assignment_id,)).fetchone()
            s=c.execute('SELECT * FROM students WHERE id=?',(student_id,)).fetchone()
            if not a or not s or a['class_id']!=s['class_id']:raise HTTPException(404,'Không tìm thấy mã đề / học sinh.')
        ids=pick_for_student(a,student_id)
        with lock:idx={q['id']:q for q in questions}
        return {'assignment_id':assignment_id,'student_id':student_id,'question_ids':ids,'keys':[idx[i]['correct'] for i in ids]}

    @router.get('/teacher/analytics')
    def analytics(class_id:int|None=None,assignment_id:int|None=None,_=Depends(teacher_dep)):
        with db() as c:
            base='''SELECT t.*,s.full_name,s.class_id,a.title assignment_title,a.chapter,a.lesson,a.grade
                    FROM attempts t JOIN students s ON s.id=t.student_id JOIN assignments a ON a.id=t.assignment_id
                    WHERE t.submitted_at IS NOT NULL AND (? IS NULL OR s.class_id=?) AND (? IS NULL OR a.id=?)'''
            data=[dict(r) for r in c.execute(base,(class_id,class_id,assignment_id,assignment_id))]
            total_students=c.execute('SELECT COUNT(*) FROM students WHERE (? IS NULL OR class_id=?)',(class_id,class_id)).fetchone()[0]
            total_tasks=c.execute('SELECT COUNT(*) FROM assignments WHERE (? IS NULL OR class_id=?)',(class_id,class_id)).fetchone()[0]
        wrong={}; per_student={}
        with lock:idx={q['id']:q for q in questions}
        for t in data:
            sid=t['student_id'];pt=t['score']/t['possible']*100 if t['possible'] else 0
            r=per_student.setdefault(sid,{'student_id':sid,'name':t['full_name'],'submissions':0,'score_percent_total':0,'last_score':0})
            r['submissions']+=1;r['score_percent_total']+=pt;r['last_score']=pt
            answers=json.loads(t['answers']);ids=json.loads(t['question_ids'])
            for ident in ids:
                q=idx.get(ident)
                if not q or not gradeable(q):continue
                m=wrong.setdefault(ident,{'id':ident,'stem':q.get('stemHtml',''),'sourceNumber':q.get('sourceNumber'),'lessonName':q.get('lessonName'),'wrong':0,'total':0})
                for i,ans in enumerate(answers.get(ident,[])):
                    if i<4:
                        m['total']+=1;m['wrong']+=int(ans!=q['correct'][i])
        summary=[{'id':v['student_id'],'name':v['name'],'submissions':v['submissions'],'average':round(v['score_percent_total']/v['submissions'],1),'last_score':round(v['last_score'],1)} for v in per_student.values()]
        summary.sort(key=lambda x:x['average'])
        bad=sorted(({**v,'wrong_rate':round(v['wrong']/v['total']*100,1)} for v in wrong.values() if v['total']),key=lambda v:v['wrong_rate'],reverse=True)
        valid_scores=[t['score']/t['possible']*100 for t in data if t['possible']]
        mean=round(sum(valid_scores)/len(valid_scores),1) if valid_scores else None
        return {'student_count':total_students,'assignment_count':total_tasks,'submissions':len(data),'average':mean,'students':summary,'frequent_errors':bad[:20]}

    @router.get('/teacher/analytics.csv')
    def analytics_csv(class_id:int|None=None,_=Depends(teacher_dep)):
        with db() as c:
            rows=c.execute('''SELECT c.title,s.full_name,a.title,t.method,t.score,t.possible,t.submitted_at
                  FROM attempts t JOIN students s ON s.id=t.student_id JOIN classes c ON c.id=s.class_id JOIN assignments a ON a.id=t.assignment_id
                  WHERE t.submitted_at IS NOT NULL AND (? IS NULL OR c.id=?) ORDER BY t.submitted_at DESC''',(class_id,class_id)).fetchall()
        stream=io.StringIO();writer=csv.writer(stream);writer.writerow(['Lớp','Họ tên','Bài giao','Hình thức','Số ý đúng','Tổng ý','Điểm thang 10','Thời điểm nộp'])
        def safe_csv(value):
            v=str(value)
            return "'"+v if v.lstrip().startswith(('=','+','-','@','\t','\r')) else v
        for r in rows:writer.writerow([safe_csv(r[0]),safe_csv(r[1]),safe_csv(r[2]),r[3],r[4],r[5],round(r[4]/r[5]*10,2) if r[5] else 0,datetime.fromtimestamp(r[6]).strftime('%Y-%m-%d %H:%M')])
        out='\ufeff'+stream.getvalue()
        return Response(out,media_type='text/csv; charset=utf-8',headers={'Content-Disposition':'attachment; filename="EduPlan_diem_hoc_sinh.csv"'})

    # Dashboard quan tri va theo doi nop bai theo tung hoc sinh; khong tiet lo khoa dap an.
    def assignment_matrix_data(assignment_id):
        with db() as conn:
            a=conn.execute('SELECT a.*,c.title AS class_title FROM assignments a JOIN classes c ON c.id=a.class_id WHERE a.id=?',(assignment_id,)).fetchone()
            if a is None:raise HTTPException(404,'Không tìm thấy bài giao.')
            records=[dict(r) for r in conn.execute('''SELECT s.id AS student_id,s.full_name,s.class_id,t.started_at,t.submitted_at,t.score,t.possible,t.method
               FROM students s LEFT JOIN attempts t ON t.student_id=s.id AND t.assignment_id=?
               WHERE s.class_id=? ORDER BY s.full_name COLLATE NOCASE,s.id''',(assignment_id,a['class_id']))]
        now=int(time.time());counts={'submitted':0,'not_started':0,'in_progress':0,'overdue':0}
        scores=[]
        for row in records:
            if row['submitted_at'] is not None:
                row['status']='submitted';counts['submitted']+=1
                row['percent']=round(row['score']/row['possible']*100,1) if row['possible'] else None
                if row['percent'] is not None:scores.append(row['percent'])
            elif a['due_at'] and now>a['due_at']:
                row['status']='overdue';counts['overdue']+=1;row['percent']=None
            elif row['started_at'] is not None:
                row['status']='in_progress';counts['in_progress']+=1;row['percent']=None
            else:
                row['status']='not_started';counts['not_started']+=1;row['percent']=None
        return {'assignment':assign_json(a),'students':records,'counts':counts,'total':len(records),
                'completion_rate':round(100*counts['submitted']/len(records),1) if records else 0,
                'average':round(sum(scores)/len(scores),1) if scores else None}

    @router.get('/teacher/assignment/{assignment_id}/matrix')
    def assignment_matrix(assignment_id:int,_=Depends(teacher_dep)):
        return assignment_matrix_data(assignment_id)

    @router.get('/teacher/assignment/{assignment_id}/matrix.csv')
    def assignment_matrix_csv(assignment_id:int,_=Depends(teacher_dep)):
        mat=assignment_matrix_data(assignment_id)
        stream=io.StringIO();w=csv.writer(stream)
        w.writerow(['Học sinh','Trạng thái','Điểm (%)','Số ý đúng','Tổng ý','Bắt đầu','Nộp lúc','Hình thức'])
        # Ngăn formula injection khi mở CSV bằng Excel.
        def excel_safe(value):
            raw=str(value if value is not None else '')
            return "'"+raw if raw.lstrip().startswith(('=','+','-','@','\t','\r')) else raw
        for r in mat['students']:
            w.writerow([excel_safe(r['full_name']),r['status'],r['percent'] if r['percent'] is not None else '',
                r['score'] if r['score'] is not None else '',r['possible'] if r['possible'] is not None else '',
                datetime.fromtimestamp(r['started_at']).strftime('%d/%m/%Y %H:%M') if r['started_at'] else '',
                datetime.fromtimestamp(r['submitted_at']).strftime('%d/%m/%Y %H:%M') if r['submitted_at'] else '',r['method'] or ''])
        return Response('\ufeff'+stream.getvalue(),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="EduPlan_bang_theo_doi_de_{assignment_id}.csv"'})

    @router.get('/teacher/availability')
    def question_availability(grade:int,chapter:int|None=None,lesson:int|None=None,level:str|None=None,competency:str|None=None,_=Depends(teacher_dep)):
        if grade not in (10,11,12):raise HTTPException(400,'Khối lớp không hợp lệ.')
        with lock:
            pool=[q for q in questions if gradeable(q) and q.get('grade')==grade and (chapter is None or q.get('chapter')==chapter) and (lesson is None or q.get('lesson')==lesson)]
        by_level={};by_comp={};by_chapter={}
        for q in pool:
            x=q.get('levelSuggested') or 'Chưa gắn mức độ';by_level[x]=by_level.get(x,0)+1
            x=q.get('competencySuggested') or 'Chưa gắn năng lực';by_comp[x]=by_comp.get(x,0)+1
            x=str(q.get('chapter'))+' · '+str(q.get('chapterName') or '');by_chapter[x]=by_chapter.get(x,0)+1
        matching=[q for q in pool if (not level or q.get('levelSuggested')==level) and (not competency or q.get('competencySuggested')==competency)]
        return {'total_graded':len(pool),'matching':len(matching),'by_level':by_level,'by_competency':by_comp,'by_chapter':by_chapter}

    @router.get('/teacher/overview')
    def teacher_overview(class_id:int|None=None,_=Depends(teacher_dep)):
        with db() as conn:
            all_classes=[dict(r) for r in conn.execute('SELECT id,title,grade,school_year FROM classes WHERE (? IS NULL OR id=?) ORDER BY grade,title',(class_id,class_id))]
            if class_id is not None and not all_classes:raise HTTPException(404,'Lớp không tồn tại.')
            assignments=[dict(r) for r in conn.execute('''SELECT a.id,a.title,a.kind,a.class_id,a.grade,a.chapter,a.lesson,a.due_at,a.count,c.title AS class_title
               FROM assignments a JOIN classes c ON c.id=a.class_id
               WHERE (? IS NULL OR a.class_id=?) ORDER BY a.created_at DESC,a.id DESC''',(class_id,class_id))]
            completed=[dict(r) for r in conn.execute('''SELECT t.student_id,t.assignment_id,t.question_ids,t.answers,t.score,t.possible,t.submitted_at
               FROM attempts t JOIN assignments a ON a.id=t.assignment_id
               WHERE t.submitted_at IS NOT NULL AND (? IS NULL OR a.class_id=?)''',(class_id,class_id))]
            total_students=conn.execute('SELECT COUNT(*) FROM students WHERE (? IS NULL OR class_id=?)',(class_id,class_id)).fetchone()[0]
            sizes={r['class_id']:r['n'] for r in conn.execute('SELECT class_id,COUNT(*) n FROM students GROUP BY class_id')}
        counts={};means={};now=int(time.time())
        for r in completed:
            aid=r['assignment_id'];counts[aid]=counts.get(aid,0)+1
            if r['possible']:
                means.setdefault(aid,[]).append(100*r['score']/r['possible'])
        task_rows=[]
        for a in assignments:
            size=sizes.get(a['class_id'],0);done=counts.get(a['id'],0)
            task_rows.append({**a,'students':size,'submitted':done,'pending':max(0,size-done),
               'completion_rate':round(100*done/size,1) if size else 0,
               'average':round(sum(means[a['id']])/len(means[a['id']]),1) if means.get(a['id']) else None,
               'overdue':bool(a['due_at'] and a['due_at']<now and done<size)})
        with lock:bank={q['id']:q for q in questions}
        errors={}
        for r in completed:
            try:ids=json.loads(r['question_ids']);answers=json.loads(r['answers'])
            except (TypeError,ValueError):continue
            for ident in ids:
                q=bank.get(ident)
                if not q or not gradeable(q):continue
                selected=answers.get(ident) or []
                if len(selected)!=4:continue
                key=(q.get('grade'),q.get('chapter'),q.get('chapterName'),q.get('lesson'),q.get('lessonName'))
                v=errors.setdefault(key,{'grade':key[0],'chapter':key[1],'chapter_name':key[2],'lesson':key[3],'lesson_name':key[4],'wrong':0,'total':0,'questions':set()})
                v['total']+=4;v['wrong']+=sum(x!=y for x,y in zip(selected,q['correct']));v['questions'].add(ident)
        weak=[]
        for item in errors.values():
            if item['total']<4:continue
            weak.append({**{k:v for k,v in item.items() if k!='questions'},'wrong_rate':round(100*item['wrong']/item['total'],1),'question_count':len(item['questions'])})
        weak.sort(key=lambda x:(x['wrong_rate'],x['total']),reverse=True)
        averages=[100*r['score']/r['possible'] for r in completed if r['possible']]
        return {'classes':all_classes,'student_count':total_students,'assignment_count':len(assignments),
          'submitted_count':len(completed),'expected_submissions':sum(x['students'] for x in task_rows),
          'overall_average':round(sum(averages)/len(averages),1) if averages else None,
          'tasks':task_rows[:100],'weak_lessons':weak[:12],
          'attention':{'overdue_tasks':sum(t['overdue'] for t in task_rows),'pending_submissions':sum(t['pending'] for t in task_rows)}}

    app.include_router(router)
    return router
