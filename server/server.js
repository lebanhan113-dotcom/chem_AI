'use strict';
/* CHEM-MAP TUTOR AI V7.1 | Local/LAN server prototype (Node 22+). Not a managed production deployment. */
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {DatabaseSync}=require('node:sqlite');
const {init:initManagement,createRouter:createManagement}=require('./manage_routes');
const ROOT=path.resolve(__dirname,'..');const PORT=Number(process.env.PORT||8080);const HOST=process.env.HOST||'127.0.0.1';
const DATADIR=path.resolve(process.env.DATA_DIR||path.join(__dirname,'data'));
fs.mkdirSync(DATADIR,{recursive:true});const db=new DatabaseSync(path.join(DATADIR,'chemmap.db'));
db.exec('PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;');
db.exec(`CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('student','teacher')), created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (token_digest TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), expires_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS questions (id TEXT PRIMARY KEY, grade INTEGER NOT NULL, chapter TEXT NOT NULL, lesson TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS quiz_sessions (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), question_ids TEXT NOT NULL, created_at TEXT NOT NULL, submitted_at TEXT);
CREATE TABLE IF NOT EXISTS attempts (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), quiz_id TEXT NOT NULL UNIQUE, grade INTEGER NOT NULL, result TEXT NOT NULL, score REAL, max_score REAL NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS visits (id TEXT PRIMARY KEY, visitor_digest TEXT NOT NULL, user_id TEXT, visited_at TEXT NOT NULL);`);
// Non-destructive migration for existing V7 databases.
function hasColumn(table,col){return db.prepare(`PRAGMA table_info(${table})`).all().some(x=>x.name===col)}
if(!hasColumn('users','student_name'))db.exec("ALTER TABLE users ADD COLUMN student_name TEXT NOT NULL DEFAULT ''");
if(!hasColumn('users','class_name'))db.exec("ALTER TABLE users ADD COLUMN class_name TEXT NOT NULL DEFAULT ''");
if(!hasColumn('quiz_sessions','mode'))db.exec("ALTER TABLE quiz_sessions ADD COLUMN mode TEXT NOT NULL DEFAULT 'practice'");
initManagement(db);
db.exec('CREATE INDEX IF NOT EXISTS idx_visits_date ON visits(visited_at); CREATE INDEX IF NOT EXISTS idx_attempt_user ON attempts(user_id,created_at);');
// Keep anonymous visitor records for 90 days, rather than indefinitely.
db.prepare('DELETE FROM visits WHERE visited_at < ?').run(new Date(Date.now()-90*86400000).toISOString());
const seed=JSON.parse(fs.readFileSync(path.join(ROOT,'bank_questions.json'),'utf8'));
const upsert=db.prepare('INSERT OR IGNORE INTO questions (id,grade,chapter,lesson,type,status,body) VALUES (?,?,?,?,?,?,?)');
const fixSeed=db.prepare('UPDATE questions SET chapter=?,lesson=?,body=? WHERE id=? AND status=?');
for(const q of seed){
 upsert.run(q.id,q.grade,q.chapter,q.lesson,q.type,q.status||'sample',JSON.stringify(q));
 fixSeed.run(q.chapter,q.lesson,JSON.stringify(q),q.id,'sample');
}
const getuser=db.prepare('SELECT * FROM users WHERE username=?');
const getuserID=db.prepare('SELECT id,username,role,student_name AS studentName,class_name AS className,is_admin AS isAdmin FROM users WHERE id=?');
const now=()=>new Date().toISOString(),newid=()=>crypto.randomUUID();
const hash=(s)=>crypto.createHash('sha256').update(s).digest('hex');
const kdf=(password,salt)=>crypto.scryptSync(password,Buffer.from(salt,'hex'),64).toString('hex');
function createUser(username,password,role,studentName='',className=''){if(!/^[a-zA-Z0-9_.-]{3,40}$/.test(username))throw Error('Tên tài khoản: 3-40 ký tự ASCII (a-z, 0-9, _ . -)');if(password.length<10)throw Error('Mật khẩu tối thiểu 10 ký tự');const salt=crypto.randomBytes(16).toString('hex');const uid=newid();db.prepare('INSERT INTO users (id,username,salt,password_hash,role,created_at,student_name,class_name) VALUES (?,?,?,?,?,?,?,?)').run(uid,username,salt,kdf(password,salt),role,now(),studentName,className);return {id:uid,username,role,studentName,className}}
const currentUsers=db.prepare('SELECT COUNT(*) n FROM users').get().n;
if(!currentUsers){
 if(process.env.CHEMMAP_DEMO==='1'){
  const t='GV-'+crypto.randomBytes(6).toString('hex'),s='HS-'+crypto.randomBytes(6).toString('hex');createUser('gv-demo',t,'teacher');createUser('hs-demo',s,'student');
  console.log('================ CHEM-MAP DEMO LOCAL ONLY ================\nGiáo viên: gv-demo | mật khẩu: '+t+'\nHọc sinh : hs-demo | mật khẩu: '+s+'\nKHÔNG dùng tài khoản demo hoặc dữ liệu thật khi công khai mạng.\n==========================================================');
 } else if(process.env.TEACHER_USERNAME&&process.env.TEACHER_PASSWORD){
  createUser(process.env.TEACHER_USERNAME,process.env.TEACHER_PASSWORD,'teacher');
 } else {console.error('Chưa có tài khoản. Khởi tạo: CHEMMAP_DEMO=1 node server.js (chỉ để thử) hoặc đặt TEACHER_USERNAME và TEACHER_PASSWORD trong môi trường.');process.exit(2)}
}
initManagement(db);
const management=createManagement({db,response: (...args)=>response(...args),fail:(...args)=>fail(...args),sanitize,parseJsonQuestion,createUser});
const maxBody=950000;const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8'};
function response(res,status,obj,extra={}){const body=JSON.stringify(obj);res.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...extra});res.end(body)}
function readBody(req){return new Promise((resolve,reject)=>{let b='',bytes=0;req.on('data',d=>{bytes+=d.length;if(bytes>maxBody){reject(Object.assign(Error('Dữ liệu quá lớn'),{code:413}));req.destroy();return}b+=d});req.on('end',()=>{try{resolve(JSON.parse(b||'{}'))}catch{reject(Object.assign(Error('JSON không hợp lệ'),{code:400}))}});req.on('error',reject)})}
function userFromCookie(req){const val=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('chemmap_sid='))?.split('=')[1];if(!val||!/^[a-f0-9]{64}$/.test(val))return null;const row=db.prepare('SELECT user_id FROM sessions WHERE token_digest=? AND expires_at>?').get(hash(val),Date.now());return row?getuserID.get(row.user_id):null}
function setSession(res,user){const token=crypto.randomBytes(32).toString('hex');db.prepare('INSERT INTO sessions VALUES (?,?,?)').run(hash(token),user.id,Date.now()+8*3600e3);return {'Set-Cookie':`chemmap_sid=${token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800${process.env.HTTPS_ONLY==='1'?'; Secure':''}`}}
function clearSession(req,res){const cookie=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('chemmap_sid='))?.split('=')[1];if(cookie)db.prepare('DELETE FROM sessions WHERE token_digest=?').run(hash(cookie));return {'Set-Cookie':`chemmap_sid=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0${process.env.HTTPS_ONLY==='1'?'; Secure':''}`}}
function sanitize(q){const a={id:q.id,grade:q.grade,chapter:q.chapter,lesson:q.lesson,type:q.type,level:q.level,competency:q.competency,stem:q.stem,hint:q.hint,unit:q.unit};if(q.type==='mcq')a.options=q.options;if(q.type==='tf')a.statements=q.statements;return a}
function parseJsonQuestion(row){return JSON.parse(row.body)}
function scoreOne(q,submitted){const selected=submitted===undefined?null:submitted;
 if(q.type==='mcq'){const ok=Number.isInteger(selected)&&selected===q.answer;return {points:ok?1:0,maxPoints:1,errors:ok?[]:[q.misconceptions?.[String(selected)]||'Cần đối chiếu lại kiến thức và lời giải.']};}
 if(q.type==='tf'){let points=0,errors=[];q.answer.forEach((correct,i)=>{const v=Array.isArray(selected)?selected[i]:null;if((v==='T'||v==='F')&&((v==='T')===correct))points+=.25;else errors.push('Ý '+('abcd'[i])+': chưa đúng.');});return {points,maxPoints:1,errors};}
 if(q.type==='short'){const s=typeof selected==='string'?selected.trim().replace(',','.'):String(selected??'');const num=/^-?(?:\d+(?:\.\d*)?|\.\d+)$/.test(s)?Number(s):NaN;const ok=Number.isFinite(num)&&Math.abs(num-q.answer)<=Number(q.tolerance||0)+1e-12;return {points:ok?1:0,maxPoints:1,errors:ok?[]:['Kiểm tra đơn vị, phương trình, thứ tự tính toán.']};}
 return {points:0,maxPoints:0,errors:[],pendingTeacher:true};}
const fail=(res,msg,status=400)=>response(res,status,{error:msg});
const requests=new Map();function limited(req){let ip=req.socket.remoteAddress||'?';let a=requests.get(ip)||[];const t=Date.now();a=a.filter(x=>t-x<60000);a.push(t);requests.set(ip,a);return a.length>100}
const staticFiles={'/live':'live.html','/live.css':'live.css','/live.js':'live.js','/portal':'portal.html','/portal.js':'portal.js','/portal.css':'portal.css'};
const server=http.createServer(async(req,res)=>{
 res.setHeader('X-Frame-Options','DENY');res.setHeader('Referrer-Policy','no-referrer');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'");
 if(limited(req))return fail(res,'Quá nhiều yêu cầu',429);
 let u;try{u=new URL(req.url,'http://localhost')}catch{return fail(res,'Đường dẫn không hợp lệ')};const url=u.pathname;
 if(req.method==='GET'&&(url==='/'||staticFiles[url])){const filename=url==='/'?'portal.html':staticFiles[url];const buf=fs.readFileSync(path.join(__dirname,filename));res.writeHead(200,{'Content-Type':mime[path.extname(filename)]||'application/octet-stream','Cache-Control':'no-store'});return res.end(buf)}
 if(!url.startsWith('/api/'))return fail(res,'Không tìm thấy',404);
 if(req.method!=='GET'&&req.headers.origin){try{const origin=new URL(req.headers.origin);if(origin.host!==req.headers.host)return fail(res,'Nguồn truy cập không hợp lệ',403)}catch{return fail(res,'Origin không hợp lệ',403)}}
 let body={};if(req.method==='POST'){try{body=await readBody(req)}catch(e){return fail(res,e.message,e.code||400)}}
 // Count each actual page load once; no IP address or user-agent fingerprint stored.
 if(url==='/api/visit'&&req.method==='POST'){
  const cookie=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('chemmap_vid='))?.slice(12);
  const raw=cookie&&/^[a-f0-9]{48}$/.test(cookie)?cookie:crypto.randomBytes(24).toString('hex');
  const extra=cookie===raw?{}:{'Set-Cookie':`chemmap_vid=${raw}; HttpOnly; SameSite=Lax; Path=/; Max-Age=7776000${process.env.HTTPS_ONLY==='1'?'; Secure':''}`};
  const current=userFromCookie(req);
  db.prepare('DELETE FROM visits WHERE visited_at < ?').run(new Date(Date.now()-90*86400000).toISOString());
  db.prepare('INSERT INTO visits (id,visitor_digest,user_id,visited_at) VALUES (?,?,?,?)').run(newid(),hash(raw),current?.id||null,now());
  return response(res,200,{ok:true},extra);
 }
 if(url==='/api/login'&&req.method==='POST'){
  const username=String(body.username||'').trim(),pw=String(body.password||'');const row=getuser.get(username);if(!row)return fail(res,'Tên đăng nhập hoặc mật khẩu không đúng',401);
  const digest=kdf(pw,row.salt);if(!crypto.timingSafeEqual(Buffer.from(digest,'hex'),Buffer.from(row.password_hash,'hex')))return fail(res,'Tên đăng nhập hoặc mật khẩu không đúng',401);
  const safe={id:row.id,username:row.username,role:row.role,studentName:row.student_name,className:row.class_name,isAdmin:!!row.is_admin};return response(res,200,{user:safe},setSession(res,safe));
 }
 const user=userFromCookie(req);if(!user)return fail(res,'Cần đăng nhập',401);
 if(management.handle(req,res,u,body,user))return;
 if(url==='/api/logout'&&req.method==='POST')return response(res,200,{ok:true},clearSession(req,res));
 if(url==='/api/me'&&req.method==='GET')return response(res,200,{user});
 if(url==='/api/profile'&&req.method==='POST'){
  if(user.role!=='student')return fail(res,'Chỉ học sinh cập nhật thông tin trong bản thử nghiệm',403);
  const studentName=String(body.studentName||'').trim().replace(/\s+/g,' ');
  const className=String(body.className||'').trim().replace(/\s+/g,' ');
  if(studentName.length<2||studentName.length>70||className.length<2||className.length>18||!(/^[\p{L}\p{N} ._\-]+$/u.test(studentName)&&/^[\p{L}\p{N} ._\-]+$/u.test(className)))return fail(res,'Vui lòng điền họ tên (2–70 ký tự) và lớp (2–18 ký tự) hợp lệ');
  const registered=db.prepare('SELECT c.name FROM class_students cs JOIN classrooms c ON c.id=cs.class_id WHERE cs.student_id=? LIMIT 1').get(user.id);
  const actualClass=registered?.name||className;
  db.prepare('UPDATE users SET student_name=?,class_name=? WHERE id=?').run(studentName,actualClass,user.id);
  return response(res,200,{user:{...user,studentName,className:actualClass}});
 }
 if(url==='/api/analytics'&&req.method==='GET'&&user.role==='teacher'){
  if(!user.isAdmin)return fail(res,'Hãy xem Thống kê lớp được phân công tại /portal',403);
  const visits=db.prepare('SELECT COUNT(*) n FROM visits').get().n;
  const visitors=db.prepare('SELECT COUNT(DISTINCT visitor_digest) n FROM visits').get().n;
  const accounts=db.prepare("SELECT COUNT(*) n FROM users WHERE role='student'").get().n;
  const quizStats=db.prepare(`SELECT
    COUNT(DISTINCT CASE WHEN s.mode IN ('test','midterm','final') THEN s.user_id END) AS test_started,
    COUNT(DISTINCT CASE WHEN s.mode NOT IN ('test','midterm','final') THEN s.user_id END) AS practice_started,
    COUNT(DISTINCT CASE WHEN s.mode IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN s.user_id END) AS test_students,
    COUNT(DISTINCT CASE WHEN s.mode NOT IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN s.user_id END) AS practice_students,
    SUM(CASE WHEN s.mode IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN 1 ELSE 0 END) AS test_attempts,
    SUM(CASE WHEN s.mode NOT IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN 1 ELSE 0 END) AS practice_attempts,
    COUNT(*) AS starts FROM quiz_sessions s`).get();
  const byClass=db.prepare(`SELECT u.class_name AS className,
    COUNT(DISTINCT CASE WHEN s.submitted_at IS NOT NULL THEN s.user_id END) AS students,
    COUNT(DISTINCT CASE WHEN s.mode IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN s.user_id END) AS testStudents,
    COUNT(DISTINCT CASE WHEN s.mode NOT IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN s.user_id END) AS practiceStudents,
    SUM(CASE WHEN s.mode IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN 1 ELSE 0 END) AS testAttempts,
    SUM(CASE WHEN s.mode NOT IN ('test','midterm','final') AND s.submitted_at IS NOT NULL THEN 1 ELSE 0 END) AS practiceAttempts
    FROM quiz_sessions s JOIN users u ON u.id=s.user_id GROUP BY u.class_name ORDER BY u.class_name`).all();
  const recent=db.prepare(`SELECT a.created_at AS at,u.student_name AS studentName,u.class_name AS className,s.mode,
    a.score,a.max_score,a.grade FROM attempts a JOIN users u ON u.id=a.user_id JOIN quiz_sessions s ON s.id=a.quiz_id
    ORDER BY a.created_at DESC LIMIT 100`).all();
  const daily=db.prepare("SELECT substr(visited_at,1,10) AS day,COUNT(*) AS visits,COUNT(DISTINCT visitor_digest) AS visitors FROM visits GROUP BY day ORDER BY day DESC LIMIT 30").all();
  return response(res,200,{visits,uniqueVisitors:visitors,studentAccounts:accounts,testStarted:quizStats.test_started||0,practiceStarted:quizStats.practice_started||0,testStudents:quizStats.test_students||0,practiceStudents:quizStats.practice_students||0,testAttempts:quizStats.test_attempts||0,practiceAttempts:quizStats.practice_attempts||0,starts:quizStats.starts||0,byClass,recent,daily,windowDays:90});
 }

 if(url==='/api/catalog'&&req.method==='GET')return response(res,200,JSON.parse(fs.readFileSync(path.join(ROOT,'catalog.json'),'utf8')));
 if(url==='/api/stats'&&req.method==='GET'){const count=db.prepare("SELECT COUNT(*) n FROM questions").get().n;const approved=db.prepare("SELECT COUNT(*) n FROM questions WHERE status='approved'").get().n;const attempts=user.role==='teacher'?(user.isAdmin?db.prepare('SELECT COUNT(*) n FROM attempts').get().n:db.prepare('SELECT COUNT(DISTINCT a.id) n FROM attempts a JOIN class_students cs ON cs.student_id=a.user_id JOIN class_teachers ct ON ct.class_id=cs.class_id WHERE ct.teacher_id=?').get(user.id).n):db.prepare('SELECT COUNT(*) n FROM attempts WHERE user_id=?').get(user.id).n;return response(res,200,{questionCount:count,approved,attempts});}
 if(url==='/api/quiz/start'&&req.method==='POST'){
  if(user.role!=='student')return fail(res,'Giáo viên không thể tạo lượt làm bài học sinh',403);
  if(!user.studentName||!user.className)return fail(res,'Cần cập nhật họ tên và lớp trước khi làm bài',400);
  const mode=String(body.mode||'practice');if(!['diagnostic','practice','remedial','transfer','test','midterm','final'].includes(mode))return fail(res,'Mục tiêu làm bài không hợp lệ');
  const grade=Number(body.grade),count=Number(body.count);if(![10,11,12].includes(grade)||![5,10,15].includes(count))return fail(res,'Lớp hoặc số câu không hợp lệ');
  const chapter=String(body.chapter||'all'),lesson=String(body.lesson||'all'),official=body.official===true;
  if(chapter.length>200||lesson.length>200)return fail(res,'Tên bài quá dài');
  const rows=db.prepare(`SELECT id,chapter,lesson FROM questions WHERE grade=? AND status IN (${official?"'approved'":"'sample','approved','published'"})`).all(grade);
  const available=rows.filter(q=>(chapter==='all'||q.chapter===chapter)&&(lesson==='all'||q.lesson===lesson));
  if(available.length<count)return fail(res,`Chỉ có ${available.length} câu phù hợp, cần ${count}. ${official?'Giáo viên cần duyệt thêm câu.':''}`);
  available.sort(()=>Math.random()-.5);const ids=available.slice(0,count).map(q=>q.id),quizId=newid();db.prepare('INSERT INTO quiz_sessions (id,user_id,question_ids,created_at,submitted_at,mode) VALUES (?,?,?,?,NULL,?)').run(quizId,user.id,JSON.stringify(ids),now(),mode);
  const find=db.prepare('SELECT body FROM questions WHERE id=?');return response(res,201,{quizId,questions:ids.map(id=>sanitize(parseJsonQuestion(find.get(id))))});
 }
 if(url==='/api/quiz/submit'&&req.method==='POST'){
  const quiz=db.prepare('SELECT * FROM quiz_sessions WHERE id=? AND user_id=?').get(String(body.quizId||''),user.id);if(!quiz)return fail(res,'Không tồn tại bài làm',404);if(quiz.submitted_at)return fail(res,'Bài đã nộp; không thể nộp lại',409);
  const answers=body.answers&&typeof body.answers==='object'&&!Array.isArray(body.answers)?body.answers:{};
  const ids=JSON.parse(quiz.question_ids);const find=db.prepare('SELECT body FROM questions WHERE id=?');const records=ids.map(id=>{const q=parseJsonQuestion(find.get(id)),selected=answers[id]??null;return {questionId:id,selected,...scoreOne(q,selected),solution:{stem:q.stem,explanation:q.explanation,answer:q.answer,options:q.options||null,sampleAnswer:q.sampleAnswer||null,referenceUrl:q.referenceUrl||null}}});
  const counted=records.filter(r=>r.maxPoints),points=counted.reduce((s,r)=>s+r.points,0),max=counted.reduce((s,r)=>s+r.maxPoints,0),grade=parseJsonQuestion(find.get(ids[0])).grade;
  const attempt={id:newid(),grade,at:now(),studentName:user.studentName,className:user.className,mode:quiz.mode,records,points,maxPoints:max,accuracy:max?Math.round(100*points/max):null};
  db.exec('BEGIN');try{db.prepare('UPDATE quiz_sessions SET submitted_at=? WHERE id=? AND submitted_at IS NULL').run(attempt.at,quiz.id);db.prepare('INSERT INTO attempts VALUES (?,?,?,?,?,?,?,?)').run(attempt.id,user.id,quiz.id,grade,JSON.stringify(attempt),points,max,attempt.at);db.exec('COMMIT')}catch(e){db.exec('ROLLBACK');throw e}
  const assignment=quiz.assignment_id?db.prepare('SELECT mode,closes_at FROM assignments WHERE id=?').get(quiz.assignment_id):null;
  if(assignment?.mode==='test'&&assignment.closes_at&&now()<assignment.closes_at)return response(res,200,{attempt:{id:attempt.id,at:attempt.at,withheld:true,records:[],message:'Đã nộp bài. Đáp án và điểm sẽ hiển thị sau thời điểm đóng bài kiểm tra.'}});
  return response(res,200,{attempt});
 }
 if(url==='/api/attempts'&&req.method==='GET'){
  const rows=(user.role==='teacher'?(user.isAdmin?db.prepare('SELECT a.*,u.username FROM attempts a JOIN users u ON a.user_id=u.id ORDER BY a.created_at DESC LIMIT 200').all():db.prepare('SELECT DISTINCT a.*,u.username FROM attempts a JOIN users u ON a.user_id=u.id JOIN quiz_sessions qz ON qz.id=a.quiz_id LEFT JOIN assignments ass ON ass.id=qz.assignment_id JOIN class_students cs ON cs.student_id=u.id JOIN class_teachers ct ON ct.class_id=cs.class_id WHERE ct.teacher_id=? AND (ass.id IS NULL OR ass.class_id=ct.class_id) ORDER BY a.created_at DESC LIMIT 200').all(user.id)):db.prepare('SELECT * FROM attempts WHERE user_id=? ORDER BY created_at DESC LIMIT 100').all(user.id));
  return response(res,200,{attempts:rows.map(x=>({id:x.id,student:JSON.parse(x.result).studentName||x.username||user.studentName||user.username,className:JSON.parse(x.result).className||'',mode:JSON.parse(x.result).mode||'practice',grade:x.grade,createdAt:x.created_at,score:(()=>{const a=db.prepare('SELECT t.mode,t.closes_at FROM quiz_sessions q JOIN assignments t ON t.id=q.assignment_id WHERE q.id=?').get(x.quiz_id);return user.role==='student'&&a?.mode==='test'&&a.closes_at&&now()<a.closes_at?null:x.score})(),maxScore:x.max_score,accuracy:(()=>{const a=db.prepare('SELECT t.mode,t.closes_at FROM quiz_sessions q JOIN assignments t ON t.id=q.assignment_id WHERE q.id=?').get(x.quiz_id);return user.role==='student'&&a?.mode==='test'&&a.closes_at&&now()<a.closes_at?null:(x.max_score?Math.round(100*x.score/x.max_score):null)})(),result:(()=>{const aid=db.prepare('SELECT assignment_id FROM quiz_sessions WHERE id=?').get(x.quiz_id)?.assignment_id;const a=aid?db.prepare('SELECT mode,closes_at FROM assignments WHERE id=?').get(aid):null;if(user.role==='student'&&a?.mode==='test'&&a.closes_at&&now()<a.closes_at)return {id:x.id,withheld:true,records:[],message:'Lời giải được mở sau hạn đóng bài kiểm tra.'};return JSON.parse(x.result)})()}))});
 }

 if(url==='/api/essay/pending'&&req.method==='GET'&&user.role==='teacher'){
  const rows=(user.isAdmin?db.prepare('SELECT a.id,a.result,u.username FROM attempts a JOIN users u ON a.user_id=u.id ORDER BY a.created_at DESC LIMIT 300').all():db.prepare('SELECT DISTINCT a.id,a.result,u.username FROM attempts a JOIN users u ON a.user_id=u.id JOIN quiz_sessions qz ON qz.id=a.quiz_id LEFT JOIN assignments ass ON ass.id=qz.assignment_id JOIN class_students cs ON cs.student_id=u.id JOIN class_teachers ct ON ct.class_id=cs.class_id WHERE ct.teacher_id=? AND (ass.id IS NULL OR ass.class_id=ct.class_id) ORDER BY a.created_at DESC LIMIT 300').all(user.id));
  const pending=[];
  for(const row of rows){const a=JSON.parse(row.result);for(const r of a.records||[])if(r.pendingTeacher){
   const qrow=db.prepare('SELECT body FROM questions WHERE id=?').get(r.questionId);if(!qrow)continue;
   const q=JSON.parse(qrow.body);pending.push({attemptId:row.id,questionId:r.questionId,student:row.username,stem:q.stem,answer:r.selected,sampleAnswer:q.sampleAnswer||'',rubric:q.rubric||[]});
  }}
  return response(res,200,{pending:pending.slice(0,100)});
 }
 if(url==='/api/essay/grade'&&req.method==='POST'&&user.role==='teacher'){
  const attemptId=String(body.attemptId||''),questionId=String(body.questionId||'');
  const points=Number(body.points),feedback=String(body.feedback||'').trim();
  if(!Number.isFinite(points)||points<0||points>1||Math.round(points*4)!==points*4||feedback.length>800)return fail(res,'Điểm tự luận phải là 0; 0,25; 0,5; 0,75 hoặc 1, nhận xét tối đa 800 ký tự');
  const row=db.prepare('SELECT * FROM attempts WHERE id=?').get(attemptId);if(!row||!management.canAccessStudent(user,row.user_id))return fail(res,'Không có quyền chấm lượt làm này',403);
  const gradingAssignment=db.prepare('SELECT ass.class_id FROM quiz_sessions qz JOIN assignments ass ON ass.id=qz.assignment_id WHERE qz.id=?').get(row.quiz_id);
  if(gradingAssignment&&!management.classAccess(user,gradingAssignment.class_id))return fail(res,'Bài thuộc lớp không được phân công',403);
  const a=JSON.parse(row.result),r=(a.records||[]).find(x=>x.questionId===questionId);
  if(!r||r.pendingTeacher!==true)return fail(res,'Không có bài tự luận đang chờ chấm',409);
  const qrow=db.prepare('SELECT type FROM questions WHERE id=?').get(questionId);if(!qrow||qrow.type!=='essay')return fail(res,'Không phải câu tự luận',400);
  r.pendingTeacher=false;r.points=points;r.maxPoints=1;r.teacherFeedback=feedback;r.gradedBy=user.username;r.gradedAt=now();
  a.points=a.records.reduce((t,x)=>t+Number(x.points||0),0);a.maxPoints=a.records.reduce((t,x)=>t+Number(x.maxPoints||0),0);
  a.accuracy=a.maxPoints?Math.round(100*a.points/a.maxPoints):null;
  db.prepare('UPDATE attempts SET result=?,score=?,max_score=? WHERE id=?').run(JSON.stringify(a),a.points,a.maxPoints,attemptId);
  return response(res,200,{ok:true,score:a.points,maxScore:a.maxPoints});
 }
 if(url==='/api/questions'&&req.method==='GET'&&user.role==='teacher'){
  const offset=Math.max(0,Math.min(10000,Number(u.searchParams.get('offset')||0)||0)),search=String(u.searchParams.get('search')||'').slice(0,100);
  const rows=db.prepare('SELECT id,grade,chapter,lesson,type,status,body FROM questions WHERE id LIKE ? OR chapter LIKE ? OR lesson LIKE ? ORDER BY grade,id LIMIT 60 OFFSET ?').all(...Array(3).fill('%'+search+'%'),offset);
  return response(res,200,{questions:rows.map(q=>{const body=JSON.parse(q.body);return {id:q.id,grade:q.grade,chapter:q.chapter,lesson:q.lesson,type:q.type,status:q.status,stem:body.stem,answer:body.answer,explanation:body.explanation}})});
 }
 if(url==='/api/questions/import'&&req.method==='POST'&&user.role==='teacher'){
  const arr=body.questions;if(!Array.isArray(arr)||!arr.length||arr.length>50)return fail(res,'Mỗi lần nhập cần 1 đến 50 câu trong {questions:[...]}');
  const titles=JSON.parse(fs.readFileSync(path.join(ROOT,'catalog.json'),'utf8'));
  const validType=['mcq','tf','short','essay'],level=['NB','TH','VD','VDC'],competency=['HH1','HH2','HH3'];
  const seen=new Set(),existingStems=new Set(db.prepare('SELECT grade,body FROM questions').all().map(r=>r.grade+'|'+JSON.parse(r.body).stem.trim().toLowerCase()));
  for(const [i,q] of arr.entries()){
    const failq=message=>fail(res,'Câu '+(i+1)+': '+message);
    if(!q||!/^[a-zA-Z0-9_.-]{4,85}$/.test(q.id||''))return failq('Mã không hợp lệ');
    if(seen.has(q.id)||db.prepare('SELECT id FROM questions WHERE id=?').get(q.id))return failq('Mã trùng');seen.add(q.id);
    if(![10,11,12].includes(q.grade)||!titles[String(q.grade)]?.some(c=>c.name===q.chapter&&c.lessons.includes(q.lesson)))return failq('Chương/bài không khớp danh mục');
    if(!validType.includes(q.type)||!level.includes(q.level)||!competency.includes(q.competency))return failq('Sai dạng/mức độ/năng lực');
    if(typeof q.stem!=='string'||q.stem.trim().length<10||q.stem.length>4000||typeof q.explanation!=='string'||!q.explanation.trim()||q.explanation.length>5000)return failq('Cần nội dung và lời giải hợp lệ');
    const sig=q.grade+'|'+q.stem.trim().toLowerCase();if(existingStems.has(sig))return failq('Trùng nội dung nguyên văn');existingStems.add(sig);
    if(q.type==='mcq'&&(!(Array.isArray(q.options)&&q.options.length===4&&q.options.every(x=>typeof x==='string'&&x.trim()))||!Number.isInteger(q.answer)||q.answer<0||q.answer>3))return failq('Cần MCQ 4 lựa chọn và đáp án 0-3');
    if(q.type==='tf'&&(!(Array.isArray(q.statements)&&q.statements.length===4&&q.statements.every(x=>typeof x==='string'))||!(Array.isArray(q.answer)&&q.answer.length===4&&q.answer.every(x=>typeof x==='boolean'))))return failq('Cần 4 nhận định và 4 đáp án đúng/sai');
    if(q.type==='short'&&(!Number.isFinite(q.answer)||!Number.isFinite(Number(q.tolerance||0))||Number(q.tolerance||0)<0))return failq('Đáp án ngắn phải là số hữu hạn');
    if(q.type==='essay'&&(!Array.isArray(q.rubric)||!q.rubric.length||typeof q.sampleAnswer!=='string'))return failq('Cần rubric và lời giải tự luận');
  }
  db.exec('BEGIN');try{for(const q of arr){const item={...q,status:'draft',sourceMode:'teacher_upload',version:Number(q.version)||1};db.prepare('INSERT INTO questions VALUES (?,?,?,?,?,?,?)').run(item.id,item.grade,item.chapter,item.lesson,item.type,'draft',JSON.stringify(item))}db.exec('COMMIT')}catch(e){db.exec('ROLLBACK');return fail(res,'Không nhập được: '+e.message)}
  return response(res,201,{inserted:arr.length,status:'draft'});
 }
 if(url==='/api/approve'&&req.method==='POST'&&user.role==='teacher'){
  const id=String(body.id||'');const r=db.prepare("UPDATE questions SET status='approved' WHERE id=?").run(id);return r.changes?response(res,200,{ok:true}):fail(res,'Không có mã câu',404);
 }
 if(url==='/api/users'&&req.method==='POST'&&user.role==='teacher'){
  return fail(res,'V7.2: tạo tài khoản học sinh từ danh sách lớp trong /portal',403);
  try{const name=String(body.studentName||'').trim(),cl=String(body.className||'').trim();
  if(name.length<2||name.length>70||cl.length<2||cl.length>18)return fail(res,'Cần họ tên và lớp hợp lệ cho học sinh');
  const next=createUser(String(body.username||'').trim(),String(body.password||''),'student',name,cl);return response(res,201,{user:next})}catch(e){return fail(res,e.message,e.message.includes('UNIQUE')?409:400)}
 }
 return fail(res,'Không có quyền hoặc đường dẫn không hợp lệ',user.role==='teacher'?404:403);
});
server.listen(PORT,HOST,()=>console.log(`CHEM-MAP LIVE local: http://${HOST}:${PORT}\nNgân hàng: ${seed.length} bản ghi. Sử dụng dữ liệu thử nghiệm, chưa đưa lên mạng công khai.`));
