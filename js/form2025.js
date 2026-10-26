/* EduPlan AI 7.9 – Form 2025 and common, post-submission question review.
   Source bank is immutable. The server grades only catalogued questions.
   Official exam: 18 MCQ + 4 four-statement true/false + 6 short answers (50 minutes).
   Optional school examination adds essay section and is NOT the official graduation format. */
(function(){
'use strict';
const PARTS=[['mcq','PHẦN I. TRẮC NGHIỆM NHIỀU PHƯƠNG ÁN',18],['tf4','PHẦN II. TRẮC NGHIỆM ĐÚNG/SAI – 4 Ý MỖI CÂU',4],['short','PHẦN III. CÂU HỎI TRẢ LỜI NGẮN',6],['essay','PHẦN IV. TỰ LUẬN – MỞ RỘNG NHÀ TRƯỜNG',4]];
const getSafe=q=>q&&String(q.stem||'').trim();
function parseTF(q){
 const text=String(q?.stem||'');
 const source=Object.entries(q?.statements||{}).filter(([k,v])=>/^[abcd]$/i.test(k)&&String(v).trim());
 if(source.length===4)return {stem:text,items:source.map(([k,t])=>({k:k.toLowerCase(),text:String(t)}))};
 const re=/(?<![A-Za-z0-9])([a-d])\s*[.)]\s*/gi;let m,found=[];
 while((m=re.exec(text))!==null){const letter=m[1].toLowerCase();if(letter==='abcd'[found.length])found.push({letter,at:m.index,start:re.lastIndex});if(found.length===4)break;}
 if(found.length!==4)return null;
 const items=found.map((x,i)=>({k:x.letter,text:text.slice(x.start,i===3?text.length:found[i+1].at).trim()}));
 if(items.some(x=>!x.text)||/(?:^|[\n\r\t])\s*a\s*[.)]/i.test(items[0].text))return null;
 return {stem:text.slice(0,found[0].at).trim(),items};
}
const valid=q=>getSafe(q) && (q.kind!=='mcq'||['A','B','C','D'].every(c=>String(q.options?.[c]||'').trim())) && (q.kind!=='tf4'||!!parseTF(q));
const qById=id=>bank.find(q=>q.id===id);
function qSection(q){return PARTS.find(x=>x[0]===q.kind)?.[1]||'CÂU HỎI';}
function questionBody(q,i,answer,editable=false,partNo=''){
 if(!q)return '';
 const kind=q.kind;
 const parsed=kind==='tf4'?parseTF(q):null;
 const label=`Câu ${i+1}${partNo?' (Phần '+partNo+')':''}`;
 let extra='';
 if(kind==='mcq')extra='<div class="answers">'+['A','B','C','D'].filter(c=>q.options?.[c]!=null).map(c=>`<label class="answer form-choice"><input ${editable?'':'disabled'} type="radio" name="f25-${e(q.id)}" value="${c}" ${answer===c?'checked':''} onchange="EduPlanForm.setAnswer(${JSON.stringify(q.id).replace(/"/g,'&quot;')})"><span><b>${c}.</b> ${chem(q.options[c])}</span></label>`).join('')+'</div>';
 if(kind==='tf4')extra=parsed?'<div class="f25-tf">'+parsed.items.map(({k,text},j)=>`<div class="f25-statement"><span><b>${k})</b> ${chem(text)}</span><select aria-label="Chọn đúng sai ý ${k}" class="f25-tf-option" data-q="${e(q.id)}" data-i="${j}" ${editable?'':'disabled'} onchange="EduPlanForm.setAnswer(${JSON.stringify(q.id).replace(/"/g,'&quot;')})"><option value="">Chọn Đ/S</option><option value="D" ${answer?.split(',')[j]==='D'?'selected':''}>Đúng</option><option value="S" ${answer?.split(',')[j]==='S'?'selected':''}>Sai</option></select></div>`).join('')+'</div>':'<p class="notice alert">Không tách được 4 nhận định. Câu đang chờ kiểm tra nguồn.</p>';
 if(['short','essay'].includes(kind))extra=`<label class="field"><b>Trả lời của em</b><textarea class="f25-text" data-q="${e(q.id)}" ${editable?'':'readonly'} rows="${kind==='essay'?5:2}" oninput="EduPlanForm.setAnswer(${JSON.stringify(q.id).replace(/"/g,'&quot;')})" placeholder="Nhập câu trả lời hoặc cách giải">${e(answer||'')}</textarea></label>`;
 const shownStem=(parsed?.stem||q.stem);
 const media=typeof safeMedia==='function'?safeMedia(q):'';
 return `<article class="f25-question" id="f25-${e(q.id)}"><div class="f25-qtitle"><b>${label}.</b> <span class="muted">${e(q.id)} · ${e(q.lesson||q.chapter||'')}</span></div>${q.needs_review?'<p class="help">Câu nguồn chưa được xác minh đầy đủ; chỉ dùng để tự ôn cho đến khi kiểm duyệt.</p>':''}<div class="f25-stem">${chem(shownStem)}</div>${media}${extra}</article>`;
}
function answerOf(session,id){return session?.answers?.[id]??'';}
function reviewOne(q,result,answer,i){
 if(!q)return '';
 const checked=result?.status==='checked';
 const hint=checked?`<div class="f25-feedback ${result.correct?'right':'wrong'}"><b>${result.correct?'✓ Đúng':'✕ Cần ôn lại'}</b><p>Em chọn: <b>${e(answer||'Chưa trả lời')}</b></p><p>Đáp án đúng: <b>${e(result.correctAnswer||'')}</b></p>${result.explanation?`<div><b>Lời giải / giải thích đã được lưu:</b> ${chem(result.explanation)}</div>`:'<p>Ngân hàng chưa có lời giải chi tiết đã xác nhận cho câu này.</p>'}</div>`:
 `<div class="notice alert">Câu này chưa có đáp án và lời giải được kiểm chứng để công bố. Em đã trả lời: <b>${e(answer||'Chưa trả lời')}</b>. Cần giáo viên kiểm duyệt.</div>`;
 return `<details class="f25-review" ${i===0?'open':''}><summary>Câu ${i+1} · ${e(qSection(q).replace('PHẦN ','').slice(0,42))} ${checked?(result.correct?'✓':'✗'):'· Chờ duyệt'}</summary>${questionBody(q,i,answer,false)}${hint}</details>`;
}
function resultsView(session){
 const data=session?.grading||{};const byId=new Map((data.results||[]).map(x=>[x.id,x]));
 const reviewed=session?.ids||[];const count=(data.results||[]).filter(r=>r.status==='checked').length;
 const info=data.status==='ready'?`<div class="notice success"><b>Đã nộp bài.</b> ${data.correct||0}/${count} câu trả lời đúng trong số câu có thể chấm; ${reviewed.length-count} câu cần giáo viên kiểm duyệt. Đây là kết quả tự học, không phải điểm thi chính thức.</div>`:
 `<div class="notice alert">Đã lưu toàn bộ bài làm. Chưa nhận được đáp án từ máy chủ chấm; giữ nguyên nội dung câu hỏi và câu trả lời để em xem lại. Không tự tạo đáp án.</div>`;
 return `<section class="card f25-reviews"><h2>Đã nộp bài – Nội dung câu hỏi, đáp án và lời giải</h2>${info}<div class="actions"><button class="btn primary" onclick="EduPlanForm.word(true)">Tải bài làm và lời giải .docx</button><button class="btn" onclick="EduPlanForm.retry()">Kiểm tra lại đáp án</button><button class="btn" onclick="EduPlanForm.reset()">Tạo bài khác</button></div>${reviewed.map((id,i)=>reviewOne(qById(id),byId.get(id),answerOf(session,id),i)).join('')}</section>`;
}
function formQuestionsPool(kind){return bank.filter(q=>q.grade===Number(app.grade)&&(!app.chapter||q.chapter===app.chapter)&&(!app.lesson||q.lesson===app.lesson)&&q.kind===kind&&valid(q));}
function infoCounts(){return PARTS.map(([kind,title,n])=>({kind,title,n,items:formQuestionsPool(kind)}));}
function setting(){const s=app.form2025Config||{};return {mode:s.mode||'official',minutes:Number(s.minutes)||50,scope:s.scope||'all',publishOnly:!!s.publishOnly};}
function setMode(mode){const s=setting();app.form2025Config={...s,mode,minutes:mode==='official'?50:60};persist();}
function availability(){const s=setting(),parts=infoCounts().filter(x=>s.mode==='school'||x.kind!=='essay');
return `<div class="card"><h2>Số câu đủ dữ liệu trong phạm vi đã chọn</h2><div class="f25-counts">${parts.map(({title,n,items})=>`<div class="stat-row"><span>${e(title)}</span><strong class="${items.length<n?'f25-shortage':''}">${items.length}/${n} cần</strong></div>`).join('')}</div>${parts.some(x=>x.items.length<x.n)?'<p class="notice alert">Chưa đủ câu đúng dạng để tạo đề chuẩn. Hãy chọn phạm vi rộng hơn hoặc bổ sung câu đã kiểm định. Không tự ý lấy câu sai bài hoặc thay câu thiếu bằng dạng khác.</p>':'<p class="notice success">Đủ số câu theo cấu trúc được chọn. Đáp án và lời giải chỉ hiển thị sau nộp nếu máy chủ có khóa đã kiểm chứng.</p>'}</div>`;}
function formSelectors(){return `<div class="fields">${field('Khối lớp','grade',[[10,'Hóa học 10'],[11,'Hóa học 11'],[12,'Hóa học 12']],app.grade)}${field('Chương KNTT','chapter',[['','Tất cả chương'],...chapters().map(ch=>[ch.name,`Chương ${ch.no}. ${ch.name}`])],app.chapter)}${field('Bài học','lesson',[['','Tất cả bài của phạm vi'],...lessons().map(l=>[l.name,`Bài ${l.no}. ${l.name}`])],app.lesson)}</div>`;}
function setup(){const s=setting();return hero('ĐỀ HÓA HỌC · CHƯƠNG TRÌNH GDPT 2018','Làm bài theo Form 2025','Làm trực tiếp theo từng phần, lưu tự động và xem lại toàn bộ nội dung sau nộp. Câu chưa đủ điều kiện chấm sẽ được ghi rõ.')+
`<div class="grid"><div class="card"><h2>Thiết lập đề</h2>${typeof userDataForm==='function'?userDataForm():''}${formSelectors()}<label class="field">Cấu trúc đề<select onchange="EduPlanForm.mode(this.value)"><option value="official" ${s.mode==='official'?'selected':''}>Form 2025 chính thức: 18 + 4 + 6 (28 câu; 50 phút)</option><option value="school" ${s.mode==='school'?'selected':''}>Mở rộng nhà trường: 18 + 4 + 6 + 4 tự luận</option></select></label><p class="help">Phần IV tự luận là mở rộng dùng ở trường, không phải cấu trúc thi tốt nghiệp THPT chính thức.</p><div class="actions"><button class="btn primary" onclick="EduPlanForm.start()">Bắt đầu làm đề</button><button class="btn" onclick="EduPlanForm.word(false)">Tải đề Word .docx</button></div></div>${availability()}</div>`;}
function start(){const s=setting(),sections=infoCounts().filter(x=>s.mode==='school'||x.kind!=='essay');let lacks=sections.filter(x=>x.items.length<x.n);
 if(lacks.length){notify('Chưa đủ câu: '+lacks.map(x=>`${x.kind} cần ${x.n}, có ${x.items.length}`).join('; ')+'. Hãy mở rộng phạm vi.');return;}
 const used=new Set(),qs=[];for(const sec of sections){let candidates=seededShuffle(sec.items).filter(q=>!used.has(q.id));for(const q of candidates.slice(0,sec.n)){used.add(q.id);qs.push(q);}}
 const now=Date.now();app.form2025Session={id:'form2025-'+now,ids:qs.map(q=>q.id),answers:{},submitted:false,started:now,finishedAt:null,mode:s.mode,minutes:s.mode==='official'?50:60,scope:{grade:app.grade,chapter:app.chapter,lesson:app.lesson},grading:{status:'idle'}};persist();}
function takeAnswer(id){const s=app.form2025Session;if(!s||s.submitted)return;const q=qById(id);if(!q)return;let value='';if(q.kind==='mcq')value=document.querySelector(`input[name="f25-${CSS.escape(id)}"]:checked`)?.value||'';
 else if(q.kind==='tf4')value=[...document.querySelectorAll(`.f25-tf-option[data-q="${CSS.escape(id)}"]`)].map(e=>e.value).join(',');
 else value=document.querySelector(`.f25-text[data-q="${CSS.escape(id)}"]`)?.value||'';
 s.answers[id]=value;save();document.getElementById('f25-count-done').textContent=String(Object.values(s.answers).filter(v=>String(v).trim()&&String(v).replaceAll(',','')).length);}
function examUI(){const s=app.form2025Session;if(!s)return setup();if(s.submitted)return hero('KẾT QUẢ FORM 2025','Bài làm đã nộp','Em xem lại từng câu và lời giải đã được kiểm chứng trước khi luyện thêm.')+resultsView(s);
 let remaining=Math.max(0,Math.ceil((s.started+s.minutes*60000-Date.now())/1000));if(remaining===0){setTimeout(()=>{if(app.form2025Session&&!app.form2025Session.submitted)submit(true)},10);}
 let n=0,sections=PARTS.filter(p=>s.mode==='school'||p[0]!=='essay');const progress=Object.values(s.answers).filter(v=>String(v).replaceAll(',','').trim()).length;
 return hero('BÀI LÀM THEO FORM 2025','Làm trực tiếp theo từng phần','Bài làm được lưu tự động tại thiết bị. Đáp án không xuất hiện trước khi em nộp.')+
 `<section class="card f25-exam"><div class="stat-row"><strong>Hóa ${e(s.scope.grade)} · ${e(s.scope.lesson||s.scope.chapter||'Tổng hợp')}</strong><span>${s.minutes} phút</span></div><div class="stat-row"><span>Đã trả lời</span><b><span id="f25-count-done">${progress}</span> / ${s.ids.length} câu</b></div><p class="help">Mã lượt: ${e(s.id)} · ${new Date(s.started).toLocaleString('vi-VN')}</p><div class="actions"><button class="btn primary" onclick="EduPlanForm.submit()">Nộp bài và xem lời giải</button><button class="btn" onclick="EduPlanForm.word(false)">Tải đề Word .docx</button></div>${sections.map(([kind,title])=>{const list=s.ids.map(qById).filter(q=>q?.kind===kind);return list.length?`<section class="f25-part"><h2>${title}</h2>${list.map(q=>questionBody(q,s.ids.indexOf(q.id),answerOf(s,q.id),true)).join('')}</section>`:'';}).join('')}<div class="actions"><button class="btn primary" onclick="EduPlanForm.submit()">Hoàn thành & nộp bài</button></div></section>`;
}
async function gradeSession(s){try{const res=await fetch('/api/grade',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({questions:s.ids.map(id=>({id,answer:answerOf(s,id)}))}),signal:AbortSignal.timeout(12000)});
 if(!res.ok)throw Error('Dịch vụ chấm chưa khả dụng (HTTP '+res.status+')');const obj=await res.json();if(!Array.isArray(obj.results)||obj.results.length!==s.ids.length)throw Error('Phản hồi máy chủ không đầy đủ');s.grading={status:'ready',results:obj.results,checked:obj.checked,correct:obj.correct,checkedAt:Date.now()};}
 catch(err){s.grading={status:'unavailable',error:String(err.message||err)};}save();persist();}
async function submit(expired=false){const s=app.form2025Session;if(!s||s.submitted)return;
 const missing=s.ids.length-Object.values(s.answers).filter(v=>String(v).replaceAll(',','').trim()).length;
 if(!expired&&missing>0&&!confirm(`Em còn ${missing} câu chưa trả lời. Vẫn nộp bài chứ?`))return;
 s.submitted=true;s.finishedAt=Date.now();s.expired=!!expired;s.grading={status:'pending'};
 app.history=[{id:s.id,mode:'form2025',scope:s.scope,ids:s.ids,index:0,answers:s.ids.map(id=>({id,answer:answerOf(s,id)})),started:s.started,finishedAt:s.finishedAt,finished:true,flagged:[],selfReview:{},grading:s.grading},...(app.history||[]).filter(x=>x.id!==s.id)].slice(0,200);save();persist();await gradeSession(s);
 const h=app.history.find(x=>x.id===s.id);if(h){h.grading=s.grading;save();}
}
async function retry(){const s=app.form2025Session;if(s?.submitted)await gradeSession(s);}
function reset(){app.form2025Session=null;save();persist();}
function formDocQuestions(s){return (s?.ids||[]).map(qById).filter(Boolean).map(q=>{const tf=q.kind==='tf4'?parseTF(q):null;return tf?{...q,stem:tf.stem,statements:Object.fromEntries(tf.items.map(x=>[x.k,x.text]))}:q;});}
async function word(withWork=false){const s=app.form2025Session;if(!s){notify('Hãy tạo bài trước khi xuất đề Word đúng Form 2025.');return;}
 const qs=formDocQuestions(s),gradeMap=new Map((s.grading?.results||[]).map(x=>[x.id,x]));try{
 await EduPlanDocx.download({title:s.mode==='official'?'ĐỀ HÓA HỌC – CẤU TRÚC FORM 2025':'ĐỀ HÓA HỌC – CẤU TRÚC MỞ RỘNG',grade:s.scope.grade,chapter:s.scope.chapter,lesson:s.scope.lesson,student:app.name,className:app.className,questions:qs,form2025:true,minutes:s.minutes,includeWork:withWork&&!!s.submitted,answers:s.ids.map(id=>({id,answer:answerOf(s,id)})),feedback:withWork&&s.submitted?Object.fromEntries([...gradeMap]):null,filename:`EduPlan_AI_7_9_${withWork?'Bai_Lam_Va_Loi_Giai':'De_Form_2025'}.docx`,footer:'Câu chưa có khóa đã kiểm chứng sẽ không được tự động chấm hoặc tự tạo lời giải.'});
 }catch(err){notify('Lỗi tạo DOCX: '+err.message);}}
const oldDraw=draw;
draw=function(){if(app.tab==='form2025')return examUI();const content=oldDraw();if(['home','catalog','exam','selftest','worksheet','practice','interactive','resources'].includes(app.tab))return content+`<section class="card f25-cta"><h2>Làm đề theo đúng Form 2025</h2><p>18 câu A–D · 4 câu Đúng/Sai (4 ý) · 6 câu trả lời ngắn; làm trên trang, xem lại nguyên đề sau nộp.</p><button class="btn primary" onclick="navigate('form2025')">Vào Form 2025</button></section>`;return content;};
NAV.splice(Math.max(0,NAV.findIndex(x=>x[0]==='selftest'))+1,0,['form2025','▣','Đề Form 2025']);
if(typeof PRIMARY_NAV!=='undefined')PRIMARY_NAV.splice(Math.max(0,PRIMARY_NAV.findIndex(x=>x[0]==='selftest'))+1,0,['form2025','▣','Form 2025']);

// Make post-submit review of pre-existing modules show *all* question content, options and verified feedback.
postSubmitReview=function(s){if(!s?.finished)return '';const byId=new Map((s.grading?.results||[]).map(r=>[r.id,r]));return resultsView({ids:s.ids,answers:Object.fromEntries((s.answers||[]).map(a=>[a.id,a.answer])),grading:s.grading});};
// Unified renderer is also used by the inline workbook and past history.
const oldReviewSession=reviewSession;
reviewSession=function(i){const item=(app.history||[])[i];if(item?.mode==='form2025'){app.tab='form2025';app.form2025Session={id:item.id,ids:item.ids,answers:Object.fromEntries((item.answers||[]).map(a=>[a.id,a.answer])),submitted:true,started:item.started,finishedAt:item.finishedAt,scope:item.scope,grading:item.grading,mode:item.ids.length>28?'school':'official',minutes:50};persist();return;}return oldReviewSession(i);};
window.EduPlanForm={parseTF,valid,reviewOne,resultsView,mode:setMode,start,setAnswer:takeAnswer,submit,reset,retry,word,reviewSaved:function(id){const h=(app.history||[]).find(s=>s.id===id);if(!h)return;app.form2025Session={id:h.id,ids:h.ids,answers:Object.fromEntries((h.answers||[]).map(x=>[x.id,x.answer])),submitted:true,started:h.started,finishedAt:h.finishedAt,scope:h.scope,grading:h.grading,mode:'official',minutes:50};app.tab='form2025';persist();}};
})();
