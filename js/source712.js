/* EduPlan AI 7.12: published questions from seven 2026-2027 Grade 10 source documents.
   Unreviewed source questions are NOT shipped to student clients. */
(function(){
'use strict';
let catalog=null;
const $=id=>document.getElementById(id);
const safe=x=>EduPlanChem.esc(String(x??''));
fetch('./data/source712_catalog.json',{cache:'no-cache'}).then(r=>r.ok?r.json():Promise.reject(Error('Nguồn chưa sẵn sàng'))).then(x=>{catalog=x;if(app.tab==='sources712')persist();}).catch(err=>console.warn('source catalog',err));
function gotoGrade10(ch,lesson,tab='bank',mode=''){
 const chapter=(curriculum['10']||[]).find(x=>x.no===Number(ch));if(!chapter)return;
 app.grade=10;app.chapter=chapter.name;app.lesson=lesson||'';
 app.kind='';app.difficulty='';app.part='';app.session=null;app.search='';app.searchPage=0;
 app.tab=tab;app.amount=mode==='five'?5:app.amount;
 persist();$('workspace')?.scrollIntoView({behavior:'smooth',block:'start'});
 if(mode==='five'){startQuiz('practice');$('workspace')?.scrollIntoView({behavior:'smooth',block:'start'});}
}
window.gotoGrade10=gotoGrade10;
const beforeDraw=draw;
function sources(){
 if(!catalog)return `<div class="card"><h2>Đang nạp danh mục 7 đề Hóa 10…</h2></div>`;
 const total=bank.filter(x=>x.grade===10&&String(x.id).startsWith('NEW26-10-')).length;
 const cards=catalog.chapters.map(ch=>{
  const n=ch.public;
  const lessons=ch.lessons.map(l=>`<div class="src-lesson712"><div><b>Bài ${l.no}. ${safe(l.name)}</b><small>${l.public} câu mới có khóa kiểm tra</small></div><button type="button" class="btn" onclick='gotoGrade10(${ch.no}, ${JSON.stringify(l.name)}, "bank")' ${l.public?'':'disabled'}>Xem câu</button><button type="button" class="btn primary" onclick='gotoGrade10(${ch.no}, ${JSON.stringify(l.name)}, "practice", "five")' ${l.public?'':'disabled'}>Luyện ngay</button></div>`).join('');
  return `<article class="card source-chapter712"><div class="src-top712"><h2>Chương ${ch.no}. ${safe(ch.name)}</h2><span class="tag">${n} câu mới</span></div>
   <p class="help">Đã trích từ đề nguồn: <b>${ch.imported} câu</b> · Phần I: ${ch.parts['1']} · II: ${ch.parts['2']} · III: ${ch.parts['3']} · IV: ${ch.parts['4']}.</p>
   <p class="help">${ch.pending} câu của chương đang chờ đối chiếu đáp án/hình và chưa công bố.</p>
   <div class="src-actions712"><button type="button" class="btn primary" onclick="gotoGrade10(${ch.no},'', 'practice','five')" ${n?'':'disabled'}>▶ Luyện theo chương</button><button type="button" class="btn" onclick="gotoGrade10(${ch.no},'', 'bank')" ${n?'':'disabled'}>☷ Xem kho câu hỏi</button></div>
   <details class="src-lessons712"><summary>Chọn đúng bài học trong chương (${ch.lessons.length} bài)</summary>${lessons}</details></article>`;
 }).join('');
 return `<section class="hero"><small>NGUỒN CÂU HỎI HÓA HỌC 10 · 2026–2027</small><h1>7 chương – Chọn bài và làm ngay</h1>
 <p>Truy cập nhanh các câu hỏi mới có khóa đã được đối chiếu. Câu chưa đủ điều kiện được lưu riêng để rà soát, không dùng để chấm học sinh.</p></section>
 <div class="metrics"><div class="metric"><strong>${catalog.chapters.reduce((s,ch)=>s+ch.imported,0)}</strong><span>Câu trích từ 7 đề</span></div><div class="metric"><strong>${total}</strong><span>Câu mới được công bố</span></div><div class="metric"><strong>${catalog.chapters.reduce((s,ch)=>s+ch.pending,0)}</strong><span>Chờ kiểm duyệt riêng</span></div><div class="metric"><strong>4</strong><span>Phần câu hỏi nguồn</span></div></div>
 <div class="notice alert"><b>Phần II, III và IV:</b> Đã nhập theo từng phần vào kho thẩm định; chưa công bố vì còn câu cần kiểm tra hình, MathType hoặc đáp án. Học sinh chỉ thấy câu đủ điều kiện.</div>
 <div class="source-grid712">${cards}</div>`;
}
draw=function(){return app.tab==='sources712'?sources():beforeDraw();};
const beforeMenu=paintMenu;
paintMenu=function(){
 beforeMenu();const menu=$('menu');if(!menu)return;
 const html=`<section class="feature-group710 featured-source712"><div class="feature-heading710"><h3>Mới bổ sung · Bộ đề Hóa học 10 năm học 2026–2027</h3><p>7 chương, chọn bài và ôn tập trực tiếp. Ngân hàng chưa duyệt không xuất hiện ở trang học sinh.</p></div><div class="feature-grid710"><button class="feature710 ${app.tab==='sources712'?'active':''}" onclick="navigate('sources712')"><span class="feature-icon710" aria-hidden="true">▣</span><span class="feature-text710"><strong>Ngân hàng theo chương – bài – phần</strong><small>Xem nguồn mới, luyện ngay từng nội dung</small></span></button></div></section>`;
 menu.insertAdjacentHTML('afterbegin',html);
 const w=$('workspace-name');if(w&&app.tab==='sources712')w.textContent='Ngân hàng 7 đề Hóa học 10';
};
const oldLesson=setLessonLink;
setLessonLink=function(grade,chapter,lesson,tab='practice'){app.part='';oldLesson(grade,chapter,lesson,tab);};
if(bank.length)paintMenu();
})();
