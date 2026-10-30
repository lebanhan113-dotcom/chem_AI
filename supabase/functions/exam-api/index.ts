import { createClient } from 'npm:@supabase/supabase-js@2';
import { gradeAttempt,validateQuestion,publicQuestion } from './scoring.mjs';
const url = Deno.env.get('SUPABASE_URL')!;
function key(name:string, legacy:string) { const v=Deno.env.get(name);if(v){ try{return JSON.parse(v).default as string}catch{} } return Deno.env.get(legacy)||''; }
const publicKey=key('SUPABASE_PUBLISHABLE_KEYS','SUPABASE_ANON_KEY');
const secretKey=key('SUPABASE_SECRET_KEYS','SUPABASE_SERVICE_ROLE_KEY');
if(!url||!secretKey||!publicKey) throw Error('Chưa cấu hình khóa Supabase');
const admin=createClient(url,secretKey,{auth:{persistSession:false,autoRefreshToken:false}});
const userClient=createClient(url,publicKey,{auth:{persistSession:false,autoRefreshToken:false}});
const cors={'Access-Control-Allow-Origin': Deno.env.get('ALLOWED_ORIGIN')||'*','Access-Control-Allow-Headers':'authorization,apikey,content-type','Access-Control-Allow-Methods':'POST,OPTIONS'};
const send=(v:unknown,status=200)=>new Response(JSON.stringify(v),{status,headers:{...cors,'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}});
const fail=(message:string,status=400)=>{throw Object.assign(new Error(message),{status});};
function err(q:any){if(q.error) fail('Lỗi cơ sở dữ liệu: '+q.error.message,500);return q.data;}
function needed(v:any,label:string){if(typeof v!=='string'||!v.trim())fail('Thiếu '+label);return v.trim();}
async function teacher(req:Request){
 const bearer=req.headers.get('Authorization')?.replace(/^Bearer\s+/i,'').trim();
 if(!bearer)fail('Giáo viên chưa đăng nhập',401);
 const r=await userClient.auth.getUser(bearer);
 if(r.error||!r.data.user)fail('Phiên đăng nhập không hợp lệ',401);
 const profile=err(await admin.from('app_profiles').select('role').eq('id',r.data.user.id).maybeSingle());
 if(!profile||!['teacher','admin'].includes(profile.role))fail('Tài khoản chưa được cấp quyền giáo viên',403);
 return r.data.user.id;
}
function uuid(s:any){return typeof s==='string'&&/^[0-9a-f-]{36}$/i.test(s);}
function randHex(size=24){let b=new Uint8Array(size);crypto.getRandomValues(b);return [...b].map(x=>x.toString(16).padStart(2,'0')).join('');}
async function digest(s:string){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))].map(x=>x.toString(16).padStart(2,'0')).join('');}
const now=()=>Date.now();
async function questionRows(examId:string){return err(await admin.from('exam_questions').select('*').eq('exam_id',examId).order('position'));}
function cleanAnswer(q:any,a:any) {
 if(a===null||a===undefined) return null;
 if(q.type==='mcq') return q.options?.some((o:any)=>o.id===a)?String(a):null;
 if(q.type==='short'||q.type==='essay')return typeof a==='string'?a.slice(0,q.type==='essay'?20000:500):null;
 if(q.type==='tf'&&a&&typeof a==='object'&&!Array.isArray(a)){
   const out:any={};for(const s of q.statements||[])if(typeof a[s.id]==='boolean')out[s.id]=a[s.id];return out;
 }
 return null;
}
async function attempt(token:any){
 const t=needed(token,'token bài làm');if(!/^[a-f0-9]{48}$/.test(t))fail('Token bài làm không hợp lệ',401);
 const row=err(await admin.from('exam_attempts').select('*').eq('token_hash',await digest(t)).maybeSingle());
 if(!row)fail('Không tìm thấy bài làm',404);
 const room=err(await admin.from('exam_rooms').select('*').eq('id',row.room_id).single());
 return {row,room};
}
async function submit(row:any, room:any, answers:any) {
 const questions=await questionRows(room.exam_id);
 const clean:any={};for(const q of questions)if(Object.hasOwn(answers||{},q.id))clean[q.id]=cleanAnswer(q,answers[q.id]);
 const score=gradeAttempt(questions,clean);
 const saved=err(await admin.from('exam_attempts').update({status:'submitted',submitted_at:new Date().toISOString(),answers:clean,
   auto_score:score.auto_score, final_score:score.final_score,grading_details:score}).eq('id',row.id).eq('status','active').select('id,submitted_at').maybeSingle());
 return {ok:true,submitted_at:saved?.submitted_at||row.submitted_at||new Date().toISOString()};
}
async function reconcile(roomId:string){
 const room=err(await admin.from('exam_rooms').select('*').eq('id',roomId).single());
 const active=err(await admin.from('exam_attempts').select('*').eq('room_id',roomId).eq('status','active').lte('deadline_at',new Date().toISOString()));
 for(const row of active)await submit(row,room,row.answers);
}
Deno.serve(async(req)=>{
 if(req.method==='OPTIONS')return new Response(null,{headers:cors});
 if(req.method!=='POST')return send({error:'Chỉ hỗ trợ POST'},405);
 try{
   const raw=await req.text();if(raw.length>8500000)fail('Dữ liệu vượt quá giới hạn 8.5 MB',413);
   const payload=JSON.parse(raw), action=needed(payload.action,'action'), data=payload.data||{};
   if(action==='health')return send({ok:true,server_time:new Date().toISOString(), online:true});
   // Safe profile check: authenticated user sees only their OWN teacher role.
   if(action==='auth.status'){
     const bearer=req.headers.get('Authorization')?.replace(/^Bearer\s+/i,'').trim();
     if(!bearer)fail('Chưa đăng nhập',401);
     const r=await userClient.auth.getUser(bearer);
     if(r.error||!r.data.user)fail('Phiên đăng nhập không hợp lệ',401);
     const profile=err(await admin.from('app_profiles').select('role').eq('id',r.data.user.id).maybeSingle());
     return send({email:r.data.user.email||'',role:profile?.role||'pending',confirmed:Boolean(r.data.user.email_confirmed_at)});
   }
   if(action==='admin.inviteTeacher' || action==='admin.teacherInvites'){
     const uid=await teacher(req);
     const profile=err(await admin.from('app_profiles').select('role').eq('id',uid).single());
     if(profile.role!=='admin')fail('Chỉ quản trị viên được mời giáo viên',403);
     if(action==='admin.teacherInvites'){
       const invites=err(await admin.from('teacher_invites').select('email,display_name,active,created_at,expires_at,claimed_at').order('created_at',{ascending:false}).limit(200));
       return send({invites});
     }
     const email=needed(data.email,'email giáo viên').toLowerCase();
     if(email.length>254||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))fail('Email không hợp lệ');
     const displayName=String(data.display_name||'').trim().slice(0,120);
     const expires_at=new Date(Date.now()+30*86400000).toISOString();
     // Existing claimed invites cannot be silently reassigned to a new account.
     const existing=err(await admin.from('teacher_invites').select('claimed_by').eq('email',email).maybeSingle());
     if(existing?.claimed_by)fail('Email này đã kích hoạt quyền giáo viên. Không thể dùng lời mời để cấp cho tài khoản khác.');
     err(await admin.from('teacher_invites').upsert({email,display_name:displayName,invited_by:uid,active:true,expires_at},{onConflict:'email'}));
     // If the person already has a verified account, activate immediately.
     const activated=err(await admin.rpc('activate_teacher_by_invite',{p_email:email}));
     return send({ok:true,email,activated:Boolean(activated),expires_at});
   }
   if(action==='student.room'){
     const code=needed(data.code,'mã phòng').toUpperCase();
     const room=err(await admin.from('exam_rooms').select('id,code,starts_at,ends_at,duration_minutes,active,exam_id').eq('code',code).maybeSingle());
     if(!room||!room.active)fail('Phòng thi không tồn tại hoặc đã đóng',404);
     const exam=err(await admin.from('exams').select('title,subject,grade').eq('id',room.exam_id).single());
     return send({room:{code:room.code,starts_at:room.starts_at,ends_at:room.ends_at,duration_minutes:room.duration_minutes},exam,server_time:new Date().toISOString()});
   }
   if(action==='student.join'){
     const code=needed(data.code,'mã phòng').toUpperCase();
     const room=err(await admin.from('exam_rooms').select('*').eq('code',code).maybeSingle());
     if(!room||!room.active)fail('Phòng thi không khả dụng',404);
     if(now()<new Date(room.starts_at).getTime()||now()>=new Date(room.ends_at).getTime())fail('Chưa đến hoặc đã hết thời gian mở phòng');
     const name=needed(data.name,'họ tên').slice(0,130), className=needed(data.className,'lớp').slice(0,40);
     const t=randHex(), deadline=new Date(Math.min(now()+room.duration_minutes*60000,new Date(room.ends_at).getTime())).toISOString();
     const row=err(await admin.from('exam_attempts').insert({room_id:room.id,student_name:name,student_class:className,
       token_hash:await digest(t),deadline_at:deadline}).select('id,deadline_at').single());
     const qs=await questionRows(room.exam_id);
     return send({token:t, attempt_id:row.id,deadline_at:deadline, questions:qs.map(publicQuestion),server_time:new Date().toISOString()});
   }
   if(['student.resume','student.save','student.submit'].includes(action)){
     const {row,room}=await attempt(data.token);
     if(action==='student.resume'){
       if(row.status==='submitted')return send({submitted:true,server_time:new Date().toISOString()});
       if(now()>=new Date(row.deadline_at).getTime())return send({...await submit(row,room,row.answers),submitted:true});
       const qs=await questionRows(room.exam_id);
       return send({submitted:false,attempt_id:row.id,deadline_at:row.deadline_at,answers:row.answers,questions:qs.map(publicQuestion),server_time:new Date().toISOString()});
     }
     if(row.status!=='active')return send({submitted:true,ok:true});
     if(now()>=new Date(row.deadline_at).getTime())return send({...await submit(row,room,row.answers),submitted:true});
     const qs=await questionRows(room.exam_id),a:any={};
     for(const q of qs)if(Object.hasOwn(data.answers||{},q.id))a[q.id]=cleanAnswer(q,data.answers[q.id]);
     // save replaces draft but only valid question identifiers are persisted
     if(action==='student.save'){
       err(await admin.from('exam_attempts').update({answers:a}).eq('id',row.id).eq('status','active'));
       return send({ok:true,server_time:new Date().toISOString()});
     }
     return send({...await submit(row,room,a),submitted:true});
   }
   // All remaining actions: require Supabase Auth and explicitly granted teacher/admin.
   const uid=await teacher(req);
   if(action==='teacher.exams'){
     const exams=err(await admin.from('exams').select('*').eq('owner_uid',uid).order('created_at',{ascending:false}));return send({exams});
   }
   if(action==='teacher.get'){
     if(!uuid(data.exam_id))fail('Mã đề không hợp lệ');
     const exam=err(await admin.from('exams').select('*').eq('id',data.exam_id).eq('owner_uid',uid).maybeSingle());
     if(!exam)fail('Không tìm thấy đề',404);
     return send({exam,questions:await questionRows(exam.id)});
   }
   if(action==='teacher.save'){
     const meta=data.meta||{},qs=data.questions;
     if(!Array.isArray(qs)||!qs.length||qs.length>300)fail('Đề phải có từ 1 đến 300 câu');
     needed(meta.title,'tên đề');
     for(let i=0;i<qs.length;i++){
       const q=qs[i];if(!uuid(q.id))fail('Câu '+(i+1)+' thiếu UUID');
       if(!['mcq','tf','short','essay'].includes(q.type))fail('Dạng câu '+(i+1)+' không hợp lệ');
       if(!String(q.body||'').trim())fail('Câu '+(i+1)+' thiếu nội dung');
       if(q.approved){const problems=validateQuestion(q);if(problems.length)fail('Câu '+(i+1)+': '+problems.join('; '));}
       q.position=i+1;
     }
     const id=err(await admin.rpc('save_exam_revision',{p_owner:uid,p_exam_id:data.exam_id||null,p_meta:meta,p_questions:qs}));
     return send({ok:true,exam_id:id});
   }
   if(action==='teacher.history'){
     const exam=err(await admin.from('exams').select('id').eq('id',data.exam_id).eq('owner_uid',uid).maybeSingle());
     if(!exam)fail('Không có quyền xem lịch sử',403);
     const versions=err(await admin.from('exam_versions').select('id,revision,created_at').eq('exam_id',exam.id).order('revision',{ascending:false}));
     return send({versions});
   }
   if(action==='teacher.restore'){
     const exam=err(await admin.from('exams').select('id').eq('id',data.exam_id).eq('owner_uid',uid).maybeSingle());
     if(!exam)fail('Không có quyền khôi phục',403);
     if(err(await admin.from('exam_rooms').select('id').eq('exam_id',exam.id)).length)fail('Đề đã tạo phòng thi; cần nhân bản để chỉnh sửa');
     const snapshot=err(await admin.from('exam_versions').select('snapshot').eq('exam_id',exam.id).eq('revision',data.revision).maybeSingle());
     if(!snapshot)fail('Không tìm thấy phiên bản');
     const id=err(await admin.rpc('save_exam_revision',{p_owner:uid,p_exam_id:exam.id,p_meta:snapshot.snapshot.meta,p_questions:snapshot.snapshot.questions}));
     return send({ok:true,exam_id:id});
   }
   if(action==='teacher.source.upload'){
     const exam=err(await admin.from('exams').select('id').eq('id',data.exam_id).eq('owner_uid',uid).maybeSingle());
     if(!exam)fail('Không có quyền lưu file gốc',403);
     const b64=needed(data.base64,'nội dung file Word');
     if(b64.length>8200000||!/^[A-Za-z0-9+/=]+$/.test(b64))fail('File quá lớn hoặc nội dung không hợp lệ');
     const raw=atob(b64);const bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
     if(bytes.length<4||String.fromCharCode(...bytes.slice(0,2))!=='PK')fail('Không phải tệp DOCX hợp lệ');
     const sourceName=needed(data.name,'tên file').replace(/[\\/]/g,'_').slice(0,120);
     if(!/\.docx$/i.test(sourceName))fail('Chỉ cho phép .docx');
     const path=uid+'/'+exam.id+'/'+randHex(8)+'_'+sourceName;
     const file=await admin.storage.from('exam-sources').upload(path,bytes,{contentType:'application/vnd.openxmlformats-officedocument.wordprocessingml.document',upsert:false});
     if(file.error)fail('Không lưu được file Word gốc: '+file.error.message,500);
     err(await admin.from('exams').update({source_storage_path:path}).eq('id',exam.id));return send({ok:true,path});
   }
   if(action==='teacher.createRoom'){
     const id=needed(data.exam_id,'mã đề');
     const exam=err(await admin.from('exams').select('*').eq('id',id).eq('owner_uid',uid).maybeSingle());
     if(!exam)fail('Không tìm thấy đề',404);
     const qs=await questionRows(id); if(!qs.length)fail('Đề chưa có câu hỏi');
     const issues=qs.flatMap((q:any,i:number)=>validateQuestion(q).map((v:string)=>`Câu ${i+1}: ${v}`));
     if(issues.length)fail('Chưa thể phát hành: '+issues.slice(0,5).join('; '));
     const duration=Number(data.duration_minutes),start=new Date(data.starts_at),end=new Date(data.ends_at);
     if(!Number.isInteger(duration)||duration<1||duration>300)fail('Thời gian làm bài không hợp lệ');
     if(!Number.isFinite(start.getTime())||!Number.isFinite(end.getTime())||end<=start)fail('Thời gian mở phòng không hợp lệ');
     if(end.getTime()<now())fail('Thời gian đóng phòng đã qua');
     let room:any;
     for(let i=0;i<5;i++){
       const code=randHex(5).toUpperCase();const r=await admin.from('exam_rooms').insert({exam_id:id,owner_uid:uid,code,starts_at:start.toISOString(),ends_at:end.toISOString(),duration_minutes:duration}).select('*').maybeSingle();
       if(!r.error){room=r.data;break;}if(r.error.code!=='23505')fail('Không thể tạo phòng: '+r.error.message,500);
     }
     if(!room)fail('Không thể tạo mã phòng',500);
     err(await admin.from('exams').update({status:'published'}).eq('id',id));
     return send({room});
   }
   if(action==='teacher.rooms'){
     const rooms=err(await admin.from('exam_rooms').select('*,exams(title,subject)').eq('owner_uid',uid).order('created_at',{ascending:false}));return send({rooms});
   }
   if(action==='teacher.results'){
     const room=err(await admin.from('exam_rooms').select('*').eq('id',data.room_id).eq('owner_uid',uid).maybeSingle());
     if(!room)fail('Không có quyền truy cập phòng',403);
     await reconcile(room.id);
     const attempts=err(await admin.from('exam_attempts').select('id,student_name,student_class,started_at,deadline_at,submitted_at,status,answers,auto_score,final_score,grading_details,teacher_notes').eq('room_id',room.id).order('started_at'));
     return send({room,attempts,questions:await questionRows(room.exam_id)});
   }
   if(action==='teacher.essay'){
     const attemptId=needed(data.attempt_id,'bài làm');
     const a=err(await admin.from('exam_attempts').select('*,exam_rooms!inner(owner_uid,exam_id)').eq('id',attemptId).maybeSingle());
     if(!a||a.exam_rooms?.owner_uid!==uid)fail('Không có quyền chấm bài này',403);
     if(a.status!=='submitted')fail('Bài chưa nộp');
     const qs=await questionRows(a.exam_rooms.exam_id),essays=qs.filter((q:any)=>q.type==='essay');
     const marks=data.marks||{},details=a.grading_details||gradeAttempt(qs,a.answers),graded=new Map(details.details.map((d:any)=>[d.question_id,d]));
     for(const q of essays){
       if(Object.hasOwn(marks,q.id)){
         const score=Number(marks[q.id]);if(!Number.isFinite(score)||score<0||score>Number(q.points))fail('Điểm tự luận ngoài thang điểm');
         const detail=graded.get(q.id);detail.score=score;detail.status='teacher_graded';
       }
     }
     const allDone=essays.every((q:any)=>graded.get(q.id)?.status==='teacher_graded');
     const partial=details.details.reduce((n:number,d:any)=>n+Number(d.score||0),0);
     details.pending=essays.filter((q:any)=>graded.get(q.id)?.status!=='teacher_graded').length;
     details.final_score=allDone?Math.round(partial*10000)/10000:null;
     err(await admin.from('exam_attempts').update({grading_details:details,final_score:details.final_score,teacher_notes:String(data.notes||'').slice(0,2000)}).eq('id',a.id));
     return send({ok:true,final_score:details.final_score,pending:details.pending});
   }
   if(action==='teacher.qr'){
     const room=err(await admin.from('exam_rooms').select('id').eq('id',data.room_id).eq('owner_uid',uid).maybeSingle());
     if(!room)fail('Không có quyền tạo mã QR',403);
     const link=needed(data.link,'link phòng thi');
     if(!/^https:\/\/[^\s]{8,500}$/.test(link))fail('Link phòng thi phải dùng HTTPS');
     const QRCode=await import('npm:qrcode@1.5.4');
     const svg=await QRCode.default.toString(link,{type:'svg',margin:2,width:240,errorCorrectionLevel:'M'});
     const bytes=new TextEncoder().encode(svg);let bin='';for(const b of bytes)bin+=String.fromCharCode(b);
     return send({svg_base64:btoa(bin)});
   }
   if(action==='teacher.closeRoom'){
     const room=err(await admin.from('exam_rooms').select('id').eq('id',data.room_id).eq('owner_uid',uid).maybeSingle());if(!room)fail('Không có quyền');
     err(await admin.from('exam_rooms').update({active:false}).eq('id',room.id));return send({ok:true});
   }
   return send({error:'Chức năng chưa được định nghĩa'},404);
 }catch(e){
   const status=Number((e as any).status)||400;
   console.error('[exam-api]',String(e));
   return send({error:status===500?'Lỗi hệ thống. Kiểm tra nhật ký Edge Function.':String((e as Error).message||e)},status);
 }
});
