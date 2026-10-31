import { randomBytes, scryptSync, timingSafeEqual, createHmac, createHash } from 'node:crypto';

export const id = () => randomBytes(12).toString('hex');
export const roomCode = () => randomBytes(6).toString('base64url').replace(/[-_]/g,'').slice(0,8).toUpperCase();
export const normEmail = v => String(v||'').trim().toLowerCase();
export const emailKey = v => createHash('sha256').update(normEmail(v)).digest('hex');
export const hashToken = v => createHash('sha256').update(String(v)).digest('hex');
export const fail = (message,status=400) => Object.assign(new Error(message),{status});
export const secureEquals = (a,b) => {const x=createHash('sha256').update(String(a)).digest();const y=createHash('sha256').update(String(b)).digest();return timingSafeEqual(x,y)};
export function hashPassword(v){const salt=randomBytes(16).toString('hex');return `scrypt:${salt}:${scryptSync(String(v),salt,64).toString('hex')}`;}
export function verifyPassword(v,hash){try{const [,salt,hashed]=String(hash).split(':');return timingSafeEqual(scryptSync(String(v),salt,64),Buffer.from(hashed,'hex'));}catch{return false}}
export function makeSession(user,secret){const data=Buffer.from(JSON.stringify({email:user.email,role:user.role,exp:Date.now()+12*3600*1000})).toString('base64url');const sig=createHmac('sha256',secret).update(data).digest('base64url');return `${data}.${sig}`;}
export function readSession(session,secret){try{const [data,sig]=String(session||'').split('.');if(!data||!sig||!secret)return null;const expected=createHmac('sha256',secret).update(data).digest('base64url');if(!secureEquals(sig,expected))return null;const u=JSON.parse(Buffer.from(data,'base64url').toString());return u.exp>Date.now()?u:null}catch{return null}}
export const mimeSafe = v => /^data:image\/(png|jpeg|jpg|gif|webp);base64,[a-zA-Z0-9+/=]+$/.test(String(v));
export function publicQuestion(q){return {id:q.id,position:q.position,number:q.number,section:q.section,type:q.type,body:q.body,points:q.points,options:(q.options||[]).map(({id,text,media})=>({id,text,media})),statements:(q.statements||[]).map(({id,text,media})=>({id,text,media})),media:q.media||[]};}
export function checkQuestion(q){const issues=[];if(!String(q?.body||'').trim())issues.push('Thiếu nội dung câu hỏi');if(!(Number(q?.points)>0))issues.push('Thiếu biểu điểm');if(q?.issues?.length)issues.push('Cảnh báo từ Word chưa được xử lý');if(!q?.approved)issues.push('Chưa được giáo viên duyệt');if(q.type==='mcq'){if((q.options||[]).length<2)issues.push('Thiếu phương án');if(!(q.options||[]).some(o=>o.id===q.answer))issues.push('Thiếu đáp án đúng');}else if(q.type==='tf'){if(!(q.statements||[]).length)issues.push('Thiếu các ý Đúng–Sai');if((q.statements||[]).some(s=>typeof q.answer?.[s.id]!=='boolean'))issues.push('Thiếu đáp án Đúng–Sai');if(!['all_or_nothing','per_statement','score_by_correct_count'].includes(q.grading?.mode))issues.push('Thiếu quy tắc chấm Đúng–Sai');if(q.grading?.mode==='score_by_correct_count')for(let k=0;k<=(q.statements||[]).length;k++)if(!Number.isFinite(+q.grading.scores?.[k]))issues.push(`Thiếu mức điểm ${k} ý`);}else if(q.type==='short'){if(q.answer===undefined||q.answer===null||String(q.answer).trim()==='')issues.push('Thiếu đáp án ngắn');}else if(q.type==='essay'){if(!String(q.rubric||'').trim())issues.push('Thiếu hướng dẫn chấm tự luận');}else issues.push('Loại câu chưa hỗ trợ');return issues;}
function nonBlank(answer){if(answer===null||answer===undefined)return false;if(typeof answer==='object'&&!Array.isArray(answer))return Object.values(answer).some(x=>x!==null&&x!==undefined&&x!=='');return String(answer).trim().length>0;}
export function gradeExam(questions,answers={},essayScores={}){
 let total=0,max=0,pending=0,correct=0,wrong=0,unanswered=0;const details=[];
 for(const q of questions){const points=Number(q.points)||0;max+=points;const a=answers[q.id];let scored=0,state='wrong';
  if(q.type==='essay'){
   if(!nonBlank(a)){state='unanswered';unanswered++;}
   else if(Number.isFinite(Number(essayScores[q.id]))&&essayScores[q.id]!==''&&essayScores[q.id]!==null){scored=Math.min(points,Math.max(0,Number(essayScores[q.id])));state='graded';}
   else{state='pending';pending++;}
  } else if(!nonBlank(a)){state='unanswered';unanswered++;}
  else if(q.type==='mcq'){if(a===q.answer){scored=points;state='correct';correct++;}else wrong++;}
  else if(q.type==='tf'){
   const list=q.statements||[];const n=list.length;const count=list.filter(s=>a?.[s.id]===q.answer?.[s.id]).length;
   if(q.grading?.mode==='score_by_correct_count')scored=Number(q.grading.scores[count])||0;
   else if(q.grading?.mode==='per_statement'&&n)scored=points*count/n;
   else scored=count===n?points:0;
   if(count===n){state='correct';correct++;}else{state='wrong';wrong++;}
  } else if(q.type==='short'){
   const rules=q.grading||{};const norm=v=>String(v).trim().replace(/\s+/g,' ').toLowerCase().replace(',', '.');
   const expected=(Array.isArray(q.acceptedAnswers)?q.acceptedAnswers:[q.answer]).map(norm);
   const value=norm(a);let valid=expected.includes(value);
   if(!valid&&Number.isFinite(+rules.tolerance)&&rules.tolerance!==''&&rules.tolerance!==null){const valueNum=Number(value);valid=value!==''&&Number.isFinite(valueNum)&&expected.some(x=>x!==''&&Number.isFinite(Number(x))&&Math.abs(valueNum-Number(x))<=Number(rules.tolerance));}
   if(valid){scored=points;state='correct';correct++;}else wrong++;
  }
  scored=Math.min(points,Math.max(0,scored));total+=scored;details.push({id:q.id,number:q.number,section:q.section,state,score:Math.round(scored*10000)/10000,max:points});
 }
 return {score:Math.round(total*10000)/10000,maxScore:Math.round(max*10000)/10000,status:pending?'pending_essay':'official',correct,wrong,unanswered,pending,details};
}
