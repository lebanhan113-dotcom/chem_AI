'use strict';
/* CHEM-MAP TUTOR AI V7.2 - server-side class, assignment and school reporting. */
const crypto=require('node:crypto');
const newid=()=>crypto.randomUUID();
const now=()=>new Date().toISOString();
const validateText=(s,min,max)=>typeof s==='string'&&s.trim().length>=min&&s.trim().length<=max&&!/[<>\x00-\x1f]/.test(s);
const safeName=(s)=>String(s||'').trim().replace(/\s+/g,' ');
const qMarks=(n)=>Array(n).fill('?').join(',');
function init(db){
 function has(t,c){return db.prepare(`PRAGMA table_info(${t})`).all().some(r=>r.name===c)}
 if(!has('users','is_admin'))db.exec('ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0');
 if(!has('quiz_sessions','assignment_id'))db.exec('ALTER TABLE quiz_sessions ADD COLUMN assignment_id TEXT');
 db.exec(`CREATE TABLE IF NOT EXISTS classrooms (
   id TEXT PRIMARY KEY, name TEXT NOT NULL, grade INTEGER NOT NULL CHECK(grade IN (10,11,12)),
   school_year TEXT NOT NULL, created_by TEXT NOT NULL REFERENCES users(id), created_at TEXT NOT NULL,
   UNIQUE(name,school_year));
 CREATE TABLE IF NOT EXISTS class_teachers (class_id TEXT NOT NULL REFERENCES classrooms(id),teacher_id TEXT NOT NULL REFERENCES users(id),PRIMARY KEY(class_id,teacher_id));
 CREATE TABLE IF NOT EXISTS class_students (class_id TEXT NOT NULL REFERENCES classrooms(id),student_id TEXT NOT NULL REFERENCES users(id),joined_at TEXT NOT NULL,PRIMARY KEY(class_id,student_id));
 CREATE TABLE IF NOT EXISTS assignments (
   id TEXT PRIMARY KEY,class_id TEXT NOT NULL REFERENCES classrooms(id),created_by TEXT NOT NULL REFERENCES users(id),
   title TEXT NOT NULL,mode TEXT NOT NULL CHECK(mode IN ('practice','test')),
   grade INTEGER NOT NULL,chapter TEXT NOT NULL,lesson TEXT NOT NULL,question_ids TEXT NOT NULL,
   opens_at TEXT,closes_at TEXT,question_status TEXT NOT NULL,created_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'published');
 CREATE INDEX IF NOT EXISTS idx_class_students_class ON class_students(class_id);
 CREATE INDEX IF NOT EXISTS idx_quiz_assignment ON quiz_sessions(assignment_id,user_id);
 CREATE INDEX IF NOT EXISTS idx_assignments_class ON assignments(class_id);`);
 const teachers=db.prepare("SELECT id FROM users WHERE role='teacher' ORDER BY created_at").all();
 if(teachers.length&&!db.prepare('SELECT COUNT(*) n FROM users WHERE is_admin=1').get().n)
  db.prepare('UPDATE users SET is_admin=1 WHERE id=?').run(teachers[0].id);
 // One-time upgrade of historical student accounts; never changes credentials or scores.
 const old=db.prepare("SELECT id,class_name FROM users WHERE role='student' AND class_name<>''").all();
 for(const student of old){
  if(db.prepare('SELECT COUNT(*) n FROM class_students WHERE student_id=?').get(student.id).n)continue;
  const name=student.class_name.trim(),match=name.match(/^\s*(10|11|12)/),grade=match?Number(match[1]):10;
  let classroom=db.prepare('SELECT id FROM classrooms WHERE name=? AND school_year=?').get(name,'2026-2027');
  if(!classroom&&teachers[0]){const id=newid();db.prepare('INSERT INTO classrooms VALUES (?,?,?,?,?,?)').run(id,name,grade,'2026-2027',teachers[0].id,now());db.prepare('INSERT OR IGNORE INTO class_teachers VALUES (?,?)').run(id,teachers[0].id);classroom={id}}
  if(classroom)db.prepare('INSERT OR IGNORE INTO class_students VALUES (?,?,?)').run(classroom.id,student.id,now());
 }
}
function createRouter(c){const {db,response,fail,sanitize,parseJsonQuestion,createUser}=c;
 const classAccess=(user,id)=>{
  const room=db.prepare('SELECT * FROM classrooms WHERE id=?').get(String(id||''));
  if(!room)return null;
  if(user.isAdmin)return room;
  if(user.role==='teacher'&&db.prepare('SELECT 1 FROM class_teachers WHERE class_id=? AND teacher_id=?').get(room.id,user.id))return room;
  return null;
 };
 const teacherRooms=user=>{
  if(user.isAdmin)return db.prepare('SELECT c.* FROM classrooms c ORDER BY c.grade,c.name').all();
  if(user.role==='teacher')return db.prepare('SELECT c.* FROM classrooms c JOIN class_teachers t ON t.class_id=c.id WHERE t.teacher_id=? ORDER BY c.grade,c.name').all(user.id);
  return db.prepare('SELECT c.* FROM classrooms c JOIN class_students s ON s.class_id=c.id WHERE s.student_id=? ORDER BY c.grade,c.name').all(user.id);
 };
 const canAccessStudent=(user,studentId)=>user.isAdmin||db.prepare('SELECT 1 FROM class_students s JOIN class_teachers t ON s.class_id=t.class_id WHERE s.student_id=? AND t.teacher_id=?').get(studentId,user.id);
 const isManager=user=>user.role==='teacher';
 const getAssignment=id=>db.prepare('SELECT a.*,c.name class_name,c.school_year FROM assignments a JOIN classrooms c ON c.id=a.class_id WHERE a.id=?').get(String(id||''));
 const studentEnrolled=(classId,studentId)=>!!db.prepare('SELECT 1 FROM class_students WHERE class_id=? AND student_id=?').get(classId,studentId);
 const assignmentSummary=a=>({...a,questionIds:undefined,questionCount:JSON.parse(a.question_ids).length});
 const attemptsForAssignment=id=>db.prepare(`SELECT s.user_id,s.id quiz_id,s.created_at started_at,s.submitted_at,a.score,a.max_score,a.result
  FROM quiz_sessions s LEFT JOIN attempts a ON a.quiz_id=s.id WHERE s.assignment_id=? ORDER BY s.created_at DESC`).all(id);
 const reply=(res,code,body)=>response(res,code,body);
 const bad=(res,msg,status=400)=>fail(res,msg,status);
 function handle(req,res,u,body,user){const url=u.pathname,method=req.method;
  if(!url.startsWith('/api/manage/'))return false;
  const manager=isManager(user);
  if(url==='/api/manage/classes'&&method==='GET'){
   const classrooms=teacherRooms(user).map(room=>({id:room.id,name:room.name,grade:room.grade,schoolYear:room.school_year,
    studentCount:db.prepare('SELECT COUNT(*) n FROM class_students WHERE class_id=?').get(room.id).n,
    assignmentCount:db.prepare('SELECT COUNT(*) n FROM assignments WHERE class_id=?').get(room.id).n}));
   reply(res,200,{classrooms});return true;
  }
  if(url==='/api/manage/classes'&&method==='POST'){
   if(!manager){bad(res,'Chỉ giáo viên hoặc quản trị viên được tạo lớp',403);return true}
   const name=safeName(body.name),grade=Number(body.grade),year=safeName(body.schoolYear||'2026-2027');
   if(!validateText(name,2,24)||![10,11,12].includes(grade)||!/^20\d{2}-20\d{2}$/.test(year)){bad(res,'Tên lớp, khối hoặc năm học không hợp lệ');return true}
   const id=newid();try{
    db.exec('BEGIN');db.prepare('INSERT INTO classrooms VALUES (?,?,?,?,?,?)').run(id,name,grade,year,user.id,now());
    db.prepare('INSERT INTO class_teachers VALUES (?,?)').run(id,user.id);db.exec('COMMIT');
   }catch(e){db.exec('ROLLBACK');bad(res,'Lớp đã tồn tại trong năm học',409);return true}
   reply(res,201,{classroom:{id,name,grade,schoolYear:year}});return true;
  }
  if(url==='/api/manage/teachers'&&method==='GET'){
   if(!user.isAdmin){bad(res,'Chỉ quản trị viên được xem danh sách giáo viên',403);return true}
   reply(res,200,{teachers:db.prepare("SELECT id,username,student_name AS name,is_admin AS isAdmin FROM users WHERE role='teacher' ORDER BY username").all()});return true;
  }
  if(url==='/api/manage/teachers'&&method==='POST'){
   if(!user.isAdmin){bad(res,'Chỉ quản trị viên được tạo tài khoản giáo viên',403);return true}
   try{const username=safeName(body.username),name=safeName(body.name),password=String(body.password||'');
    if(!validateText(name,2,70)){bad(res,'Tên giáo viên không hợp lệ');return true}
    const next=createUser(username,password,'teacher',name,'');reply(res,201,{teacher:next});
   }catch(e){bad(res,e.message,e.message.includes('UNIQUE')?409:400)}return true;
  }
  if(url==='/api/manage/classes/teachers'&&method==='POST'){
   if(!user.isAdmin){bad(res,'Chỉ quản trị viên được phân công giáo viên',403);return true}
   const r=db.prepare("SELECT id FROM users WHERE id=? AND role='teacher'").get(String(body.teacherId||''));
   const room=classAccess(user,body.classId);if(!r||!room){bad(res,'Không tìm thấy giáo viên hoặc lớp',404);return true}
   db.prepare('INSERT OR IGNORE INTO class_teachers VALUES (?,?)').run(room.id,r.id);reply(res,200,{ok:true});return true;
  }
  if(url==='/api/manage/students'&&method==='GET'){
   const room=classAccess(user,u.searchParams.get('classId'));if(!room){bad(res,'Không có quyền xem lớp này',403);return true}
   const students=db.prepare(`SELECT u.id,u.username,u.student_name AS studentName,u.class_name AS className,u.created_at AS createdAt,
    COUNT(DISTINCT a.id) AS submitted, MAX(a.created_at) AS lastSubmitted
    FROM class_students s JOIN users u ON u.id=s.student_id LEFT JOIN attempts a ON a.user_id=u.id
    WHERE s.class_id=? GROUP BY u.id ORDER BY u.student_name,u.username`).all(room.id);
   reply(res,200,{classroom:{name:room.name,grade:room.grade},students});return true;
  }
  if(url==='/api/manage/students'&&method==='POST'){
   const room=classAccess(user,body.classId);if(!manager||!room){bad(res,'Không có quyền thêm học sinh vào lớp',403);return true}
   const name=safeName(body.studentName),username=safeName(body.username),password=String(body.password||'');
   if(!validateText(name,2,70)){bad(res,'Họ tên học sinh không hợp lệ');return true}
   try{db.exec('BEGIN');const student=createUser(username,password,'student',name,room.name);
    db.prepare('INSERT INTO class_students VALUES (?,?,?)').run(room.id,student.id,now());db.exec('COMMIT');
    reply(res,201,{student});
   }catch(e){db.exec('ROLLBACK');bad(res,e.message,e.message.includes('UNIQUE')?409:400)}return true;
  }
  if(url==='/api/manage/students/enroll'&&method==='POST'){
   const room=classAccess(user,body.classId);if(!manager||!room){bad(res,'Không có quyền ghi danh',403);return true}
   const student=db.prepare("SELECT id FROM users WHERE username=? AND role='student'").get(safeName(body.username));
   if(!student){bad(res,'Không tìm thấy tài khoản học sinh',404);return true}
   db.prepare('INSERT OR IGNORE INTO class_students VALUES (?,?,?)').run(room.id,student.id,now());
   // Display name is updated for current class; authorization never depends on this text.
   db.prepare('UPDATE users SET class_name=? WHERE id=?').run(room.name,student.id);
   reply(res,200,{ok:true});return true;
  }
  if(url==='/api/manage/assignments'&&method==='POST'){
   const room=classAccess(user,body.classId);if(!manager||!room){bad(res,'Không có quyền giao bài cho lớp này',403);return true}
   const title=safeName(body.title),mode=body.mode,grade=room.grade,count=Number(body.count),chapter=String(body.chapter||'all'),lesson=String(body.lesson||'all');
   if(!validateText(title,4,120)||!['test','practice'].includes(mode)||![5,10,15].includes(count)||chapter.length>200||lesson.length>200){bad(res,'Thông số giao bài không hợp lệ');return true}
   let opensAt=null,closesAt=null;
   if(body.opensAt){const t=new Date(body.opensAt);if(!Number.isFinite(t.getTime())){bad(res,'Ngày mở bài không hợp lệ');return true}opensAt=t.toISOString()}
   if(body.closesAt){const t=new Date(body.closesAt);if(!Number.isFinite(t.getTime())){bad(res,'Hạn nộp không hợp lệ');return true}closesAt=t.toISOString()}
   if(opensAt&&closesAt&&opensAt>=closesAt){bad(res,'Hạn đóng phải sau ngày mở');return true}
   if(mode==='test'&&!closesAt){bad(res,'Bài kiểm tra phải có hạn đóng để bảo vệ đáp án',400);return true}
   const status=(mode==='test'||body.allowSamples!==true)?'approved':'sample';
   const all=db.prepare("SELECT id,chapter,lesson FROM questions WHERE grade=? AND status IN ('approved','sample','published') ORDER BY id").all(grade);
   const match=all.filter(q=>(chapter==='all'||q.chapter===chapter)&&(lesson==='all'||q.lesson===lesson)&&
      (status==='sample'||db.prepare("SELECT status FROM questions WHERE id=?").get(q.id).status==='approved'));
   if(match.length<count){bad(res,`Chỉ có ${match.length} câu ${status==='approved'?'đã được duyệt':'minh họa'} phù hợp; cần ${count} câu.`,409);return true}
   const shuffled=match.slice();for(let i=shuffled.length-1;i>0;i--){const j=crypto.randomInt(i+1);[shuffled[i],shuffled[j]]=[shuffled[j],shuffled[i]]};
   const ids=shuffled.slice(0,count).map(q=>q.id);
   const id=newid();db.prepare('INSERT INTO assignments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)').run(id,room.id,user.id,title,mode,grade,chapter,lesson,JSON.stringify(ids),opensAt,closesAt,status,now(),'published');
   reply(res,201,{assignment:{id,title,classId:room.id,count,mode,questionStatus:status}});return true;
  }
  if(url==='/api/manage/assignments'&&method==='GET'){
   const rooms=teacherRooms(user),allowed=new Set(rooms.map(c=>c.id));const filter=u.searchParams.get('classId');
   if(filter&&!allowed.has(filter)){bad(res,'Không có quyền xem lớp này',403);return true}
   const raw=db.prepare('SELECT a.*,c.name AS class_name,c.school_year FROM assignments a JOIN classrooms c ON c.id=a.class_id ORDER BY a.created_at DESC').all();
   const assignments=raw.filter(a=>allowed.has(a.class_id)&&(!filter||filter===a.class_id)).map(a=>{
    if(user.role==='student'){
     const quiz=db.prepare('SELECT submitted_at FROM quiz_sessions WHERE assignment_id=? AND user_id=? LIMIT 1').get(a.id,user.id);
     return {...assignmentSummary(a),studentStatus:!quiz?'not_started':quiz.submitted_at?'submitted':'in_progress',started:undefined,submitted:undefined};
    }
    const started=db.prepare('SELECT COUNT(DISTINCT user_id) n FROM quiz_sessions WHERE assignment_id=?').get(a.id).n;
    const submitted=db.prepare('SELECT COUNT(DISTINCT user_id) n FROM quiz_sessions WHERE assignment_id=? AND submitted_at IS NOT NULL').get(a.id).n;
    return {...assignmentSummary(a),started,submitted};
   });reply(res,200,{assignments});return true;
  }
  if(url==='/api/manage/assignments/start'&&method==='POST'){
   if(user.role!=='student'){bad(res,'Chỉ học sinh được bắt đầu bài',403);return true}
   const a=getAssignment(body.assignmentId);
   if(!a||a.status!=='published'||!studentEnrolled(a.class_id,user.id)){bad(res,'Không được giao bài này',403);return true}
   const current=now();if((a.opens_at&&current<a.opens_at)||(a.closes_at&&current>a.closes_at)){bad(res,'Chưa đến thời gian làm bài hoặc đã hết hạn',409);return true}
   let quiz=db.prepare('SELECT * FROM quiz_sessions WHERE user_id=? AND assignment_id=? ORDER BY created_at DESC LIMIT 1').get(user.id,a.id);
   if(quiz?.submitted_at){bad(res,'Em đã nộp bài này, không thể làm lại',409);return true}
   if(!quiz){const quizId=newid();db.prepare('INSERT INTO quiz_sessions (id,user_id,question_ids,created_at,submitted_at,mode,assignment_id) VALUES (?,?,?,?,NULL,?,?)').run(quizId,user.id,a.question_ids,current,a.mode,a.id);
    quiz={id:quizId,question_ids:a.question_ids};}
   const ids=JSON.parse(quiz.question_ids),find=db.prepare('SELECT body FROM questions WHERE id=?');
   reply(res,201,{quizId:quiz.id,assignment:{id:a.id,title:a.title,mode:a.mode,className:a.class_name},questions:ids.map(id=>sanitize(parseJsonQuestion(find.get(id))))});return true;
  }
  if(url==='/api/manage/assignments/report'&&method==='GET'){
   const a=getAssignment(u.searchParams.get('assignmentId'));
   if(!a||!classAccess(user,a.class_id)||!manager){bad(res,'Không có quyền xem kết quả bài giao',403);return true}
   const students=db.prepare('SELECT u.id,u.username,u.student_name AS name FROM class_students s JOIN users u ON u.id=s.student_id WHERE s.class_id=? ORDER BY u.student_name').all(a.class_id);
   const byStudent=new Map();for(const attempt of attemptsForAssignment(a.id))if(!byStudent.has(attempt.user_id))byStudent.set(attempt.user_id,attempt);
   const rows=students.map(s=>{const t=byStudent.get(s.id);return {id:s.id,username:s.username,name:s.name,status:!t?'not_started':t.submitted_at?'submitted':'in_progress',startedAt:t?.started_at||null,submittedAt:t?.submitted_at||null,score:t?.score??null,maxScore:t?.max_score??null,accuracy:t&&t.max_score?Math.round(t.score/t.max_score*100):null}});
   const graded=rows.filter(x=>x.accuracy!==null);reply(res,200,{assignment:assignmentSummary(a),totalStudents:rows.length,started:rows.filter(x=>x.status!=='not_started').length,submitted:rows.filter(x=>x.status==='submitted').length,averageAccuracy:graded.length?Math.round(graded.reduce((sum,s)=>sum+s.accuracy,0)/graded.length):null,students:rows});return true;
  }
  if(url==='/api/manage/overview'&&method==='GET'){
   if(!manager){bad(res,'Chỉ giáo viên và quản trị viên xem thống kê',403);return true}
   const rooms=teacherRooms(user),ids=rooms.map(x=>x.id);let students=[],assignments=[];
   if(ids.length){students=db.prepare(`SELECT COUNT(DISTINCT student_id) n FROM class_students WHERE class_id IN (${qMarks(ids.length)})`).get(...ids).n;
    assignments=db.prepare(`SELECT COUNT(*) n FROM assignments WHERE class_id IN (${qMarks(ids.length)})`).get(...ids).n;
   }else{students=0;assignments=0}
   const byClass=rooms.map(r=>{const enrolled=db.prepare('SELECT COUNT(*) n FROM class_students WHERE class_id=?').get(r.id).n;
    const all=db.prepare(`SELECT s.mode,s.submitted_at,s.user_id,a.score,a.max_score FROM class_students x JOIN quiz_sessions s ON s.user_id=x.student_id LEFT JOIN attempts a ON a.quiz_id=s.id WHERE x.class_id=?`).all(r.id);
    const distinct=filter=>new Set(all.filter(filter).map(x=>x.user_id)).size;
    return {classId:r.id,className:r.name,grade:r.grade,enrolled,practiceStudents:distinct(x=>x.submitted_at&&!['test','midterm','final'].includes(x.mode)),testStudents:distinct(x=>x.submitted_at&&['test','midterm','final'].includes(x.mode)),submitted:all.filter(x=>x.submitted_at).length,assignmentCount:db.prepare('SELECT COUNT(*) n FROM assignments WHERE class_id=?').get(r.id).n};
   });
   const totalVisits=user.isAdmin?db.prepare('SELECT COUNT(*) n FROM visits').get().n:null;
   const uniqueVisitors=user.isAdmin?db.prepare('SELECT COUNT(DISTINCT visitor_digest) n FROM visits').get().n:null;
   const results={scope:user.isAdmin?'school':'assigned_classes',classrooms:rooms.length,students,assignments,visits90d:totalVisits,uniqueBrowsers90d:uniqueVisitors,byClass};
   reply(res,200,{overview:results});return true;
  }
  if(url==='/api/manage/export'&&method==='GET'){
   if(!manager){bad(res,'Không có quyền xuất dữ liệu',403);return true}
   const a=getAssignment(u.searchParams.get('assignmentId'));
   if(!a||!classAccess(user,a.class_id)){bad(res,'Không có quyền xuất bài này',403);return true}
   const students=db.prepare('SELECT u.id,u.username,u.student_name FROM class_students s JOIN users u ON u.id=s.student_id WHERE s.class_id=? ORDER BY u.student_name').all(a.class_id);
   const byStudent=new Map();for(const t of attemptsForAssignment(a.id))if(!byStudent.has(t.user_id))byStudent.set(t.user_id,t);
   const cells=[['Họ tên','Tài khoản','Lớp','Bài giao','Trạng thái','Điểm','Điểm tối đa','Nộp lúc']];
   for(const s of students){const t=byStudent.get(s.id);cells.push([s.student_name,s.username,a.class_name,a.title,!t?'Chưa bắt đầu':t.submitted_at?'Đã nộp':'Đang làm',t?.score??'',t?.max_score??'',t?.submitted_at??''])}
   const csv='\uFEFF'+cells.map(r=>r.map(v=>'"'+String(v).replace(/^[=+@\-\t\r]/,"'").replace(/"/g,'""')+'"').join(',')).join('\r\n');
   res.writeHead(200,{'Content-Type':'text/csv; charset=utf-8','Content-Disposition':'attachment; filename="chemmap-v72-assignment.csv"','Cache-Control':'no-store'});res.end(csv);return true;
  }
  bad(res,'Đường dẫn quản trị không tồn tại hoặc phương thức không hỗ trợ',404);return true;
 }
 return {handle,classAccess,teacherRooms,canAccessStudent,studentEnrolled};
}
module.exports={init,createRouter};
