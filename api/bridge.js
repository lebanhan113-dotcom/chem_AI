import {read,write,scan} from '../lib/storage.js';
import {id,roomCode,normEmail,emailKey,hashToken,secureEquals,hashPassword,verifyPassword,makeSession,readSession,publicQuestion,checkQuestion,gradeExam,fail} from '../lib/core.js';
import {randomBytes} from 'node:crypto';

const json=(data,status=200,cookie)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',...(cookie?{'Set-Cookie':cookie}:{})}});
const getCookie=req=>{const raw=req.headers.get('cookie')||'';return raw.split(';').map(x=>x.trim()).find(x=>x.startsWith('pt_session='))?.split('=')[1]||''};
const cookie=(value,maxAge=43200)=>`pt_session=${value}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
const secret=()=>process.env.SESSION_SECRET||'';
const hasStorage=()=>Boolean(process.env.BLOB_READ_WRITE_TOKEN||process.env.BLOB_STORE_ID);
const adminEmail=()=>normEmail(process.env.ADMIN_EMAIL);
function auth(req){return readSession(getCookie(req),secret());}
async function required(req){const u=auth(req);if(!u)throw fail('Hãy đăng nhập giáo viên.',401);if(u.role==='teacher'){const staff=await read(staffPath(u.email));if(!staff?.active)throw fail('Tài khoản giáo viên đã bị vô hiệu hóa.',403);}return u;}
function admin(req){const u=auth(req);if(!u||u.role!=='admin')throw fail('Chỉ quản trị viên thực hiện được thao tác này.',403);return u;}
function owner(u,entity){if(u.role!=='admin'&&entity.owner!==u.email)throw fail('Không có quyền truy cập dữ liệu này.',403);}
const maxLength=(v,n=1000)=>String(v??'').trim().slice(0,n);
const pending=(exam)=>!Array.isArray(exam.questions)||exam.questions.length===0||exam.questions.some(q=>checkQuestion(q).length);
function sanitizeExam(payload){
 if(!payload||!Array.isArray(payload.questions)||!payload.questions.length||payload.questions.length>250)throw fail('Đề thi phải có từ 1 đến 250 câu.');
 const questions=payload.questions.map((q,i)=>({id:maxLength(q.id||id(),70),position:i+1,number:Number(q.number)||i+1,section:maxLength(q.section||'I',4),type:q.type,body:maxLength(q.body,16000),points:Number(q.points)||0,
 options:(q.options||[]).slice(0,20).map(o=>({id:maxLength(o.id,5),text:maxLength(o.text,8000),media:(o.media||[]).filter(x=>typeof x==='string'&&x.startsWith('data:image/')&&x.length<1200000)})),
 statements:(q.statements||[]).slice(0,20).map(o=>({id:maxLength(o.id,5),text:maxLength(o.text,8000),media:(o.media||[]).filter(x=>typeof x==='string'&&x.startsWith('data:image/')&&x.length<1200000)})),
 media:(q.media||[]).filter(x=>typeof x==='string'&&x.startsWith('data:image/')&&x.length<1200000),
 answer:q.answer??null,acceptedAnswers:Array.isArray(q.acceptedAnswers)?q.acceptedAnswers.slice(0,20):undefined,grading:q.grading||{},rubric:maxLength(q.rubric,16000),approved:q.approved===true,issues:Array.isArray(q.issues)?q.issues.map(x=>maxLength(x,500)).slice(0,30):[]
 }));
 const unique=new Set(questions.map(q=>q.id));if(unique.size!==questions.length)throw fail('Mã câu hỏi bị trùng.');
 return {title:maxLength(payload.title,200)||'Đề chưa đặt tên',subject:maxLength(payload.subject||'Hóa học',100),grade:maxLength(payload.grade,40),topic:maxLength(payload.topic,200),questions};
}
const examPath=id=>`exams/${id}.json`;
const roomPath=code=>`rooms/${code}.json`;
const atPath=(code,aid)=>`attempts/${code}/${aid}.json`;
const staffPath=email=>`staff/${emailKey(email)}.json`;
const pwMin=s=>String(s||'').length>=10;
function studentResponse(room,attempt,exam){return {ok:true,attemptId:attempt.id,token:undefined,room:{code:room.code,title:exam.title,subject:exam.subject},deadline:attempt.deadline,serverTime:Date.now(),submitted:!!attempt.submittedAt,answers:attempt.answers,questions:exam.questions.map(publicQuestion)};}
const safeAnswers=(exam,answers)=>{
 const values={};for(const q of exam.questions){const a=answers?.[q.id];if(a===undefined||a===null)continue;
  if(q.type==='mcq'){if(typeof a==='string'&&q.options.some(x=>x.id===a))values[q.id]=a;}
  else if(q.type==='tf'){if(typeof a==='object'&&!Array.isArray(a)){values[q.id]={};for(const s of q.statements){if(typeof a[s.id]==='boolean')values[q.id][s.id]=a[s.id];}}}
  else if(['short','essay'].includes(q.type)){values[q.id]=String(a).slice(0,q.type==='essay'?20000:500);}
 }return values;
};
async function loadAttempt(data){const code=maxLength(data.code,30).toUpperCase(),aid=maxLength(data.attemptId,70);const a=await read(atPath(code,aid));if(!a||!secureEquals(hashToken(data.token||''),a.tokenHash))throw fail('Phiên làm bài không hợp lệ hoặc đã hết hạn.',401);const room=await read(roomPath(code));const exam=room?await read(examPath(room.examId)):null;if(!exam||!room)throw fail('Không tìm thấy phòng thi.',404);return {a,room,exam};}
async function submit(a,exam,code,answers){if(a.submittedAt)return a;a.answers=safeAnswers(exam,answers||a.answers);a.submittedAt=Date.now();a.result=gradeExam(exam.questions,a.answers,a.essayScores||{});await write(atPath(code,a.id),a);return a;}
async function router(req){
 if(!['POST','GET'].includes(req.method))throw fail('Phương thức không được hỗ trợ.',405);
 if(req.method==='POST'){
  const origin=req.headers.get('origin');if(origin&&origin!==new URL(req.url).origin)throw fail('Nguồn truy cập không hợp lệ.',403);
 }
 let body={};if(req.method==='POST'){const raw=await req.text();if(raw.length>3000000)throw fail('Dữ liệu quá lớn, giảm kích thước hình ảnh trước khi gửi.',413);try{body=JSON.parse(raw||'{}');}catch{throw fail('JSON không hợp lệ.')}}
 const action=body.action|| (req.method==='GET'?'health':'');const data=body.data||{};
 if(action==='health')return json({ok:true,online:!!(hasStorage()&&process.env.SESSION_SECRET&&process.env.ADMIN_EMAIL&&process.env.ADMIN_PASSWORD),backend:'Vercel Functions + Vercel Private Blob',serverTime:Date.now()},hasStorage()&&process.env.SESSION_SECRET&&process.env.ADMIN_EMAIL&&process.env.ADMIN_PASSWORD?200:503);
 if(!hasStorage()||!secret()||!adminEmail()||!process.env.ADMIN_PASSWORD)throw fail('Chưa cấu hình đủ Vercel Blob và 3 biến quản trị.',503);
 if(action==='auth.login'){
  const email=normEmail(data.email),password=String(data.password||'');let u=null;
  if(email===adminEmail()&&secureEquals(password,process.env.ADMIN_PASSWORD))u={email,role:'admin'};
  else {const s=await read(staffPath(email));if(s?.active&&verifyPassword(password,s.passwordHash))u={email,role:'teacher'};}
  if(!u)throw fail('Email hoặc mật khẩu không chính xác.',401);
  return json({ok:true,user:u},200,cookie(makeSession(u,secret())));
 }
 if(action==='auth.me'){const u=auth(req);if(u?.role==='teacher'){const staff=await read(staffPath(u.email));if(!staff?.active)return json({ok:true,user:null},200,cookie('',0));}return json({ok:true,user:u||null});}
 if(action==='auth.logout')return json({ok:true},200,cookie('',0));
 if(action==='auth.changePassword'){
  const u=await required(req);if(u.role==='admin')throw fail('Để đổi mật khẩu admin, cập nhật ADMIN_PASSWORD trong Vercel.',400);
  if(!pwMin(data.newPassword))throw fail('Mật khẩu mới phải có ít nhất 10 ký tự.');const staff=await read(staffPath(u.email));if(!staff||!verifyPassword(data.currentPassword||'',staff.passwordHash))throw fail('Mật khẩu hiện tại không đúng.',401);
  staff.passwordHash=hashPassword(data.newPassword);await write(staffPath(u.email),staff);return json({ok:true},200,cookie('',0));
 }
 if(action==='admin.staff') {admin(req);return json({ok:true,staff:(await scan('staff/')).map(({email,name,active})=>({email,name,active}))});}
 if(action==='admin.createTeacher'){
  admin(req);const email=normEmail(data.email);if(!/^\S+@\S+\.\S+$/.test(email)||!pwMin(data.password))throw fail('Cần email hợp lệ và mật khẩu ít nhất 10 ký tự.');if(email===adminEmail())throw fail('Không được thay thế tài khoản quản trị.');
  const existing=await read(staffPath(email));if(existing&&!data.reset)throw fail('Giáo viên đã tồn tại. Dùng Đặt lại mật khẩu nếu cần.');
  await write(staffPath(email),{email,name:maxLength(data.name||existing?.name,120),active:existing?.active??true,passwordHash:hashPassword(data.password)});return json({ok:true});
 }
 if(action==='admin.disableTeacher'){admin(req);const email=normEmail(data.email),s=await read(staffPath(email));if(!s)throw fail('Không tìm thấy giáo viên.',404);s.active=!s.active;await write(staffPath(email),s);return json({ok:true,active:s.active});}
 if(action==='teacher.exams'){
  const u=await required(req);const all=await scan('exams/');return json({ok:true,exams:all.filter(e=>u.role==='admin'||e.owner===u.email).map(({id,title,subject,grade,topic,owner,published,updatedAt,revision,questions})=>({id,title,subject,grade,topic,owner,published,updatedAt,revision,count:questions?.length||0}))});
 }
 if(action==='teacher.get'){const u=await required(req);const e=await read(examPath(maxLength(data.id,70)));if(!e)throw fail('Không tìm thấy đề thi.',404);owner(u,e);return json({ok:true,exam:e});}
 if(action==='teacher.save'){
  const u=await required(req);const input=sanitizeExam(data.exam);const existing=data.id?await read(examPath(maxLength(data.id,70))):null;if(data.id&&!existing)throw fail('Đề thi không tồn tại.',404);if(existing)owner(u,existing);
  if(existing?.published)throw fail('Đề đã phát hành. Hãy nhân bản trước khi chỉnh sửa.');
  const eid=existing?.id||id();const e={...input,id:eid,owner:existing?.owner||u.email,published:false,revision:(existing?.revision||0)+1,createdAt:existing?.createdAt||Date.now(),updatedAt:Date.now()};await write(examPath(eid),e);return json({ok:true,id:eid,revision:e.revision});
 }
 if(action==='teacher.publish'){
  const u=await required(req);const e=await read(examPath(maxLength(data.id,70)));if(!e)throw fail('Đề không tồn tại.',404);owner(u,e);
  const errors=e.questions.map((q,i)=>({question:i+1,issues:checkQuestion(q)})).filter(x=>x.issues.length);if(errors.length)throw fail('Chưa đủ điều kiện phát hành: '+JSON.stringify(errors.slice(0,5)));
  e.published=true;e.updatedAt=Date.now();await write(examPath(e.id),e);return json({ok:true});
 }
 if(action==='teacher.rooms'){
  const u=await required(req);const rooms=(await scan('rooms/')).filter(r=>u.role==='admin'||r.owner===u.email);return json({ok:true,rooms});
 }
 if(action==='teacher.createRoom'){
  const u=await required(req);const e=await read(examPath(maxLength(data.examId,70)));if(!e||!e.published)throw fail('Đề chưa được phát hành.',400);owner(u,e);
  const duration=Math.trunc(Number(data.durationMinutes));if(!Number.isFinite(duration)||duration<1||duration>300)throw fail('Thời gian thi phải từ 1–300 phút.');
  let code=roomCode();for(let i=0;i<5&&await read(roomPath(code));i++)code=roomCode();if(await read(roomPath(code)))throw fail('Không thể tạo mã phòng, hãy thử lại.');
  const now=Date.now(),r={code,examId:e.id,owner:u.email,title:e.title,createdAt:now,durationMinutes:duration,closeAt:now+Math.max(1,Math.min(30,Number(data.openHours)||24))*3600000};await write(roomPath(code),r,false);return json({ok:true,room:r});
 }
 if(action==='teacher.results'){
  const u=await required(req);const code=maxLength(data.code,30).toUpperCase(),room=await read(roomPath(code));if(!room)throw fail('Không tìm thấy phòng.',404);owner(u,room);
  const at=(await scan(`attempts/${code}/`,1000)).map(a=>({id:a.id,name:a.name,klass:a.klass,createdAt:a.createdAt,submittedAt:a.submittedAt,result:a.result||null,essayScores:a.essayScores||{}}));return json({ok:true,attempts:at,room});
 }
 if(action==='teacher.detail'){
  const u=await required(req);const code=maxLength(data.code,30).toUpperCase(),room=await read(roomPath(code));if(!room)throw fail('Không tìm thấy phòng.',404);owner(u,room);const a=await read(atPath(code,maxLength(data.attemptId,70)));const e=await read(examPath(room.examId));if(!a||!e)throw fail('Không tìm thấy bài làm.',404);const {tokenHash,...clean}=a;return json({ok:true,attempt:clean,exam:e});
 }
 if(action==='teacher.gradeEssay'){
  const u=await required(req);const code=maxLength(data.code,30).toUpperCase(),room=await read(roomPath(code));if(!room)throw fail('Không tìm thấy phòng.',404);owner(u,room);const e=await read(examPath(room.examId)),a=await read(atPath(code,maxLength(data.attemptId,70)));
  if(!a||!e||!a.submittedAt)throw fail('Chỉ chấm bài đã nộp.',400);const q=e.questions.find(q=>q.id===data.questionId&&q.type==='essay');if(!q)throw fail('Không tìm thấy câu tự luận.',404);
  const score=Number(data.score);if(!Number.isFinite(score)||score<0||score>q.points)throw fail('Điểm phải nằm trong thang điểm của câu.');a.essayScores={...(a.essayScores||{}),[q.id]:score};a.result=gradeExam(e.questions,a.answers,a.essayScores);await write(atPath(code,a.id),a);return json({ok:true,result:a.result});
 }
 if(action==='student.join'){
  const code=maxLength(data.code,30).toUpperCase(),room=await read(roomPath(code));if(!room)throw fail('Mã phòng không tồn tại.',404);if(Date.now()>room.closeAt)throw fail('Phòng thi đã đóng.',400);const e=await read(examPath(room.examId));if(!e?.published)throw fail('Đề thi chưa phát hành.',400);
  const name=maxLength(data.name,120),klass=maxLength(data.klass,60);if(name.length<2||!klass)throw fail('Nhập họ tên và lớp trước khi thi.');
  const token=randomBytes(32).toString('base64url'),attempt={id:id(),code,name,klass,createdAt:Date.now(),deadline:Math.min(Date.now()+room.durationMinutes*60000,room.closeAt),submittedAt:null,tokenHash:hashToken(token),answers:{},essayScores:{}};
  await write(atPath(code,attempt.id),attempt,false);return json({...studentResponse(room,attempt,e),token});
 }
 if(['student.resume','student.save','student.submit'].includes(action)){
  const {a,room,exam}=await loadAttempt(data);if(!a.submittedAt&&Date.now()>a.deadline){await submit(a,exam,room.code,a.answers);}
  if(action==='student.resume')return json(studentResponse(room,a,exam));
  if(a.submittedAt){return json({ok:true,submitted:true});}
  const ans=safeAnswers(exam,data.answers||{});
  if(action==='student.save'){a.answers=ans;await write(atPath(room.code,a.id),a);return json({ok:true,saved:true,serverTime:Date.now()});}
  await submit(a,exam,room.code,ans);return json({ok:true,submitted:true});
 }
 throw fail('Chức năng không tồn tại.',404);
}
export default {async fetch(req){try{return await router(req)}catch(e){const s=e.status||500;console.error('bridge error',s,String(e.message));return json({ok:false,error:s>=500?'Lỗi máy chủ: '+String(e.message).slice(0,150):e.message},s)}}};
