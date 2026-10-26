
/* EduPlan AI 7.8 -- context learning workbench across the existing shared bank.
   Public assets contain no answer key. Grades are shown only from /api/grade.
   This module does not mutate or copy the 1,958 source questions. */
(function(){
'use strict';
const EMBED_TABS = new Set(['home','catalog','mindmap','mistakes','bank','quality','results','chem','assistant','random','docs','resources']);
const MAX_INLINE = 15;
const getCurrentScope = () => ({grade:Number(app.grade),chapter:app.chapter||'',lesson:app.lesson||'',kind:app.kind||'',difficulty:app.difficulty||''});
const activeItems = () => filterQuestions().filter(q=>String(q.stem||'').trim());
const reviewSets=()=> new Set((app.history||[]).flatMap(s=>(s.flagged||[]).concat(Object.entries(s.selfReview||{}).filter(([_,v])=>v==='review').map(([k])=>k))));
function ensureInline(){app.inline78=app.inline78||null;return app.inline78;}
function labelScope(){return `Hóa ${app.grade} · ${app.lesson||app.chapter||'Tổng hợp các chương'}`;}
function chooseSample(n){
  const pool=activeItems();if(!pool.length){notify('Không có câu hỏi trong phạm vi đã chọn. Hãy chọn toàn chương hoặc bài khác.');return;}
  const seen=new Set((app.history||[]).flatMap(s=>(s.answers||[]).map(a=>a.id)));
  const wrong=reviewSets();
  const selected=seededShuffle(pool).sort((a,b)=>(Number(wrong.has(b.id))-Number(wrong.has(a.id)))||Number(seen.has(a.id))-Number(seen.has(b.id))).slice(0,Math.min(MAX_INLINE,Number(n)||5));
  app.inline78={id:'inline-'+Date.now(),ids:selected.map(q=>q.id),index:0,answers:[],draft:{},flagged:[],scope:getCurrentScope(),started:Date.now(),finished:false};
  save();renderInline();
  if(selected.length<n)notify(`Chỉ có ${selected.length} câu phù hợp trong phạm vi này. Không tự lấy câu sai bài hoặc tự tạo đáp án.`);
}
function questionOfInline(){const state=ensureInline();if(!state)return null;return bank.find(q=>q.id===state.ids[state.index]);}
function inlineInput(q,v){
 const v0=String(v??'');
 if(q.kind==='mcq'&&Object.keys(q.options||{}).length){return `<div class="answers">${Object.entries(q.options).filter(([k])=>/^[A-D]$/.test(k)).map(([k,val])=>`<label class="answer"><input type="radio" name="inline-response" value="${k}" ${v0===k?'checked':''}><span><b>${k}.</b> ${chem(val)}</span></label>`).join('')}</div>`;}
 if(q.kind==='tf4'&&Object.keys(q.statements||q.options||{}).length){const o=Object.entries(Object.keys(q.statements||{}).length?q.statements:q.options);return `<div class="list">${o.map(([k,txt],i)=>`<div class="answer"><b>${e(k)}.</b><span style="flex:1">${chem(txt)}</span><select class="inline-tf" data-i="${i}" aria-label="Ý ${e(k)}">${[['','Chọn'],['D','Đúng'],['S','Sai']].map(([a,b])=>option(a,b,v0.split(',')[i]||'')).join('')}</select></div>`).join('')}</div>`;}
 return `<label class="field">Câu trả lời của em<textarea id="inline-text" rows="4" placeholder="Viết các bước giải hoặc câu trả lời...">${e(v0)}</textarea></label>`;
}
function answerInline(){const q=questionOfInline();if(!q)return '';if(q.kind==='mcq'&&Object.keys(q.options||{}).length)return document.querySelector('input[name="inline-response"]:checked')?.value||'';
 if(q.kind==='tf4'&&document.querySelector('.inline-tf'))return [...document.querySelectorAll('.inline-tf')].map(a=>a.value).join(',');
 return document.getElementById('inline-text')?.value||'';}
function inlineDraft(){const state=ensureInline(),q=questionOfInline();if(!state||state.finished||!q)return;state.draft[q.id]=answerInline();save();}
function inlineSaveAndNext(){
 const state=ensureInline(),q=questionOfInline();if(!state||state.finished||!q)return;
 const v=answerInline().trim();if(!v||v.replaceAll(',','').length===0){notify('Vui lòng chọn hoặc nhập câu trả lời.');return;}
 if(q.kind==='tf4'&&document.querySelector('.inline-tf')&&v.split(',').some(x=>!x)){notify('Hãy chọn Đúng/Sai cho tất cả các ý trước khi xác nhận.');return;}
 const old=state.answers.find(x=>x.id===q.id),a={id:q.id,answer:v,at:new Date().toISOString()};if(old)Object.assign(old,a);else state.answers.push(a);
 state.draft[q.id]=v;if(state.index<state.ids.length-1)state.index++;else state.finished=true;
 if(state.finished){state.finishedAt=Date.now();const hist={id:state.id,mode:'interactive',scope:state.scope,ids:state.ids,index:state.index,started:state.started,finished:true,finishedAt:state.finishedAt,flagged:state.flagged,answers:state.answers,draft:state.draft,selfReview:{},grading:{status:'pending'}};app.history=[hist,...(app.history||[]).filter(x=>x.id!==hist.id)].slice(0,200);gradeInlineResult(hist);}
 save();renderInline();
}
async function gradeInlineResult(hist){
 try{
 const response=await fetch('./api/grade',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({questions:hist.ids.map(id=>({id,answer:(hist.answers||[]).find(a=>a.id===id)?.answer||''}))})});
 if(!response.ok)throw Error('Dịch vụ chấm chưa có hoặc không khả dụng');
 const data=await response.json();if(!Array.isArray(data.results))throw Error('Dịch vụ chấm trả dữ liệu chưa đúng');
 hist.grading={status:'ready',results:data.results,checked:data.checked,correct:data.correct,checkedAt:Date.now()};
 }catch(err){hist.grading={status:'unavailable',error:String(err.message||err)};}
 save();if(app.inline78?.id===hist.id)renderInline();
}
function inlineBack(){const s=ensureInline();if(!s||s.finished)return;inlineDraft();s.index=Math.max(0,s.index-1);save();renderInline();}
function inlineNext(){const s=ensureInline();if(!s||s.finished)return;inlineDraft();s.index=Math.min(s.ids.length-1,s.index+1);save();renderInline();}
function inlineMark(){const s=ensureInline(),q=questionOfInline();if(!s||s.finished||!q)return;const i=s.flagged.indexOf(q.id);if(i>=0)s.flagged.splice(i,1);else s.flagged.push(q.id);save();renderInline();}
function resumeInline(){const s=ensureInline();if(!s)return;renderInline();}
function clearInline(){if(app.inline78&&!app.inline78.finished&&app.inline78.answers.length&&!confirm('Bắt đầu lượt mới? Tiến độ đang làm trong khung này sẽ bị thay thế.'))return;app.inline78=null;save();renderInline();}
async function inlineWord(withWork){
 const s=ensureInline();const qs=s?.ids.map(id=>bank.find(q=>q.id===id)).filter(Boolean)||activeItems().slice(0,5);
 if(!qs.length){notify('Chưa có câu trong phạm vi đang chọn để tải Word.');return;}
 const answers=withWork&&s?[...s.answers,...Object.entries(s.draft||{}).filter(([id])=>!s.answers.some(a=>a.id===id)).map(([id,answer])=>({id,answer}))]:[];
 try{await EduPlanDocx.download({title:'PHIẾU TỰ LUYỆN HÓA HỌC THEO BÀI',grade:s?.scope.grade||app.grade,chapter:s?.scope.chapter||app.chapter,lesson:s?.scope.lesson||app.lesson,student:app.name,className:app.className,questions:qs,answers,includeWork:withWork,feedback:withWork?Object.fromEntries(((app.history||[]).find(h=>h.id===s?.id)?.grading?.results||[]).map(x=>[x.id,x])):null,filename:`EduPlan_AI_7_8_${withWork?'Bai_Lam':'Phieu_Hoc_Tap'}_Hoa_${app.grade}.docx`,footer:'Câu hỏi lấy từ ngân hàng dùng chung. Đáp án chưa kiểm duyệt không được tự động công bố.'});}
 catch(err){notify('Không tải được Word: '+err.message);}
}
function gradeDetail(s){
 const hist=(app.history||[]).find(h=>h.id===s.id),g=hist?.grading||s.grading||{};
 if(g.status==='pending')return `<p class="help">Đang yêu cầu chấm bài qua máy chủ...</p>`;
 const current={ids:s.ids,answers:Object.fromEntries((s.answers||[]).map(x=>[x.id,x.answer])),grading:g};
 return window.EduPlanForm?.resultsView(current)||`<p>Đã lưu bài làm; chờ dịch vụ chấm điểm.</p>`;
}
function inlineDisplay(){
 const s=ensureInline();if(!s)return `<div class="inline-help">Nhấn <b>Bắt đầu 5 câu</b> để luyện ngay trong mục đang xem. Tất cả câu đều lấy từ ngân hàng gốc theo bộ lọc.</div>`;
 if(s.finished)return `<div class="notice success"><b>Đã hoàn thành ${s.answers.length}/${s.ids.length} câu.</b> Kết quả đã lưu vào mục Kết quả.</div>${gradeDetail(s)}<div class="actions"><button class="btn" onclick="EduPlan78.clear()">Luyện nhóm mới</button></div>`;
 const q=questionOfInline();if(!q)return '<p>Không tìm thấy câu đã chọn trong ngân hàng.</p>';
 const val=s.draft[q.id]??s.answers.find(a=>a.id===q.id)?.answer??'';
 const html=`<div class="inline-question"><div class="stat-row"><b>Câu ${s.index+1}/${s.ids.length}</b><span>Đã trả lời ${s.answers.length}</span></div><div class="progress"><div style="width:${Math.round(s.answers.length*100/s.ids.length)}%"></div></div><div class="qid">${e(q.id)} · ${e(KIND[q.kind]||'Câu hỏi')} · ${e(q.lesson||q.chapter)}</div><h3>${chem(q.stem)}</h3>${safeMedia(q)}${inlineInput(q,val)}<p class="help">Câu nguồn có thể chưa được thẩm định. Không tự suy đoán đáp án.</p><label class="check-row"><input type="checkbox" ${s.flagged.includes(q.id)?'checked':''} onchange="EduPlan78.mark()"> Đánh dấu cần ôn</label><div class="actions"><button class="btn primary" onclick="EduPlan78.confirm()">${s.index===s.ids.length-1?'Xác nhận & hoàn thành':'Xác nhận & tiếp tục →'}</button><button class="btn" onclick="EduPlan78.back()" ${s.index===0?'disabled':''}>← Câu trước</button><button class="btn" onclick="EduPlan78.next()" ${s.index===s.ids.length-1?'disabled':''}>Câu sau →</button></div></div>`;
 return html;
}
function workbench(){
 const n=activeItems().length,s=ensureInline();const same=!!s&&JSON.stringify(s.scope)===JSON.stringify(getCurrentScope());
 return `<section class="card inline-workbench" id="inline-workbench"><div class="inline-head"><div><span class="micro-label">LUYỆN TẬP TẠI CHỖ · DÙNG CHUNG NGÂN HÀNG</span><h2>Em thử làm bài ngay</h2><p class="help">${e(labelScope())} · Có <b>${n}</b> câu theo phạm vi đang chọn</p></div><span class="mini-badge">Không cần API key</span></div>
 <div class="actions"><button class="btn primary" onclick="EduPlan78.start(5)">Bắt đầu 5 câu</button><button class="btn" onclick="EduPlan78.start(10)">10 câu</button><button class="btn" onclick="EduPlan78.start(15)">15 câu</button><button class="btn" onclick="EduPlan78.word(false)">Tải phiếu Word</button><button class="btn" onclick="navigate('selftest')">Kiểm tra có chấm</button></div>
 <div id="inline-body">${same?inlineDisplay():s&&!s.finished?`<div class="notice alert">Em có một lượt đang làm thuộc bài/chương khác. Chọn đúng phạm vi cũ để tiếp tục hoặc bắt đầu lượt mới.</div>`:inlineDisplay()}</div>
 <p class="help">Luyện tự giải được lưu trên thiết bị. Đáp án chỉ hiện sau nộp nếu máy chủ Vercel có khóa đáp án đã kiểm duyệt.</p></section>`;
}
function renderInline(){const x=document.getElementById('inline-workbench');if(!x)return;
 x.outerHTML=workbench();}
document.addEventListener('input',ev=>{if(ev.target?.id==='inline-text')inlineDraft()});
document.addEventListener('change',ev=>{if(ev.target?.name==='inline-response'||ev.target?.classList.contains('inline-tf'))inlineDraft()});
const priorDraw=draw;
draw=function(){let html=priorDraw();if(EMBED_TABS.has(app.tab))html+=workbench();return html;};
// Keep the one active study session and immediate DOCX buttons visible when changing modules.
const previousNavigate=navigate;
navigate=function(tab){if(app.inline78&&!app.inline78.finished)inlineDraft();return previousNavigate(tab);};
// Improve Word for exported worksheets, exam papers and history; no hidden answer keys are embedded.
const oldResults78=results;
results=function(){return oldResults78()+`<section class="card"><h2>Tự ôn từ kết quả</h2><p>Chọn đúng bài đang học và luyện lại câu cần ôn hoặc tải phiếu Word để học ngoài mạng.</p><div class="actions"><button class="btn primary" onclick="navigate('practice')">Luyện tiếp 5 câu</button><button class="btn" onclick="EduPlan78.word(true)">Tải Word có bài làm</button><button class="btn" onclick="navigate('mistakes')">Xem sổ lỗi sai</button></div></section>`;};
window.EduPlan78={start:chooseSample,confirm:inlineSaveAndNext,back:inlineBack,next:inlineNext,mark:inlineMark,clear:clearInline,word:inlineWord,resume:resumeInline};
if(bank.length)persist();
})();
