/* EduPlan AI 7.13 - 14 new teacher files, 21 visible chapters, no answer leakage. */
(function(){
'use strict';
const safe=x=>EduPlanChem.esc(String(x??''));
const el=id=>document.getElementById(id);let newCatalog=null;
const newFile='data/source713_catalog.json';
const chapterCount=(g,c)=>bank.filter(q=>q.grade===Number(g)&&q.chapter_no===Number(c)).length;
function chapterFor(g,c){return (curriculum[String(g)]||[]).find(x=>x.no===Number(c));}
function go713(g,c,lesson,tab){
 const ch=chapterFor(g,c);if(!ch)return;
 app.grade=g;app.chapter=ch.name;app.lesson=lesson||'';app.kind='';app.difficulty='';app.part='';app.session=null;
 if(tab==='sources713')app.tab='sources713';else app.tab=tab||'practice';
 persist();el('workspace')?.scrollIntoView({behavior:'smooth',block:'start'});
}
window.go713=go713;
window.chapterLesson713=function(g,c){
 go713(g,c,'','sources713');
 requestAnimationFrame(()=>{const sec=el('src713-'+g+'-'+c);if(sec){sec.scrollIntoView({behavior:'smooth',block:'start'});}});
};
function visibleChapterCards(){
 let grades=[10,11,12].map(g=>{
  const list=curriculum[String(g)]||[];
  return `<section class="course-section713" aria-label="Hóa học ${g}"><h3>Hóa học ${g} · ${list.length} chương</h3><div class="course-grid713">${list.map(ch=>{
   let n=chapterCount(g,ch.no);
   return `<article class="course-card713"><div class="course-title713">Chương ${ch.no}. ${safe(ch.name)}</div><div class="course-meta713">${ch.lessons.length} bài · ${n} câu có khóa kiểm tra</div><div class="course-buttons713"><button type="button" class="primary713" onclick="go713(${g},${ch.no},'','practice')" ${n?'':'disabled'}>▶ Luyện ngay</button><button type="button" onclick="chapterLesson713(${g},${ch.no})">▤ Chọn bài</button><button type="button" onclick="go713(${g},${ch.no},'','bank')" ${n?'':'disabled'}>Kho câu</button></div></article>`;
  }).join('')}</div></section>`;
 });
 const target=el('all-chapters713');if(target)target.innerHTML=grades.join('');
}
const oldDraw=draw;
function sources713(){
 if(!newCatalog)return `<div class="card"><h2>Đang tải 14 bộ đề Hóa học 11–12…</h2></div>`;
 const gids=[11,12];let sections=gids.map(g=>{
  let cs=newCatalog.chapters.filter(ch=>ch.grade===g);
  return `<h2 class="source713-section-title">Hóa học ${g} · ${cs.length} chương</h2><div class="source713-grid">${cs.map(ch=>{
   let count=chapterCount(g,ch.no);
   return `<article class="card source713-chapter" id="src713-${g}-${ch.no}"><h3>Chương ${ch.no}. ${safe(ch.name)}</h3><p class="help"><b>${count} câu có khóa</b> dùng được trong kho công khai của chương; nguồn mới trích <b>${ch.imported} câu</b> gồm ${ch.parts['1']} A–D, ${ch.parts['2']} Đúng/Sai, ${ch.parts['3']} trả lời ngắn, ${ch.parts['4']} tự luận.</p><p class="help">${ch.public} câu mới đã đối chiếu đáp án bước đầu; ${ch.pending} câu mới chờ rà soát riêng.</p><div class="actions"><button class="btn primary" onclick="go713(${g},${ch.no},'','practice')" ${count?'':'disabled'}>▶ Luyện theo chương</button><button class="btn" onclick="go713(${g},${ch.no},'','bank')" ${count?'':'disabled'}>Xem câu hỏi</button></div><div class="source713-lessons">${ch.lessons.map(l=>{let n=bank.filter(q=>q.grade===g&&q.chapter_no===ch.no&&q.lesson===l.name).length;return `<div class="source713-lesson"><span><b>Bài ${l.no}. ${safe(l.name)}</b><small>${n} câu công khai · ${l.public} câu mới</small></span><button class="btn" onclick='go713(${g},${ch.no},${JSON.stringify(l.name)},"bank")' ${n?'':'disabled'}>Xem</button><button class="btn primary" onclick='go713(${g},${ch.no},${JSON.stringify(l.name)},"practice")' ${n?'':'disabled'}>Luyện</button></div>`}).join('')}</div></article>`;
  }).join('')}</div>`;
 }).join('');
 return `<div class="hero"><small>NGÂN HÀNG HÓA HỌC 11–12 · BỔ SUNG 14 ĐỀ</small><h1>Chọn chương → chọn bài → luyện tập</h1><p>Chọn bài trực tiếp, không cần mở menu ẩn. Các câu chưa đủ điều kiện chỉ lưu trong gói thẩm định riêng.</p></div><div class="metrics"><div class="metric"><strong>${newCatalog.chapters.reduce((s,x)=>s+x.imported,0)}</strong><span>Câu đã nhập vào kho nguồn</span></div><div class="metric"><strong>${newCatalog.chapters.reduce((s,x)=>s+x.public,0)}</strong><span>Câu mới công bố bước đầu</span></div><div class="metric"><strong>${newCatalog.chapters.reduce((s,x)=>s+x.pending,0)}</strong><span>Chờ kiểm duyệt</span></div><div class="metric"><strong>14</strong><span>Đề nguồn · 4 phần</span></div></div><p class="notice alert"><b>Lưu ý:</b> Chưa có khóa kiểm tra đáng tin cậy cho phần Đúng/Sai, trả lời ngắn và tự luận từ 14 đề mới. Hệ thống KHÔNG tự chấm hay công bố chúng. Các câu A–D đã đối chiếu lần đầu vẫn cần giáo viên xác nhận trước kiểm tra chính thức.</p>${sections}`;
}
draw=function(){return app.tab==='sources713'?sources713():oldDraw();};
const prevMenu=paintMenu;
paintMenu=function(){
 prevMenu();const menu=el('menu');if(!menu)return;
 const t=`<section class="feature-group710"><div class="feature-heading710"><h3>Ngân hàng 14 đề Hóa học 11–12</h3><p>Chọn chương, chọn bài, xem câu hỏi và làm ngay. 4 phần từ tài liệu gốc được phân loại trong kho nguồn.</p></div><div class="feature-grid710"><button class="feature710 ${app.tab==='sources713'?'active':''}" onclick="navigate('sources713')"><span class="feature-icon710" aria-hidden="true">▧</span><span class="feature-text710"><strong>Chương – bài – 4 phần Hóa học 11–12</strong><small>14 bộ đề mới · luyện ngay câu đã đối chiếu khóa</small></span></button></div></section>`;
 menu.insertAdjacentHTML('afterbegin',t);
 visibleChapterCards();
 if(app.tab==='sources713'){const name=el('workspace-name');if(name)name.textContent='Ngân hàng 14 đề Hóa học 11–12';}
};
fetch('./'+newFile,{cache:'no-cache'}).then(r=>r.ok?r.json():Promise.reject(Error('Không tải được nguồn 14 đề'))).then(x=>{newCatalog=x;visibleChapterCards();if(app.tab==='sources713'){const main=el('main');if(main)main.innerHTML=draw();}}).catch(console.error);
})();
