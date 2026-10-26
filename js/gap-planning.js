/* EduPlan 7.11: learning coverage and publication gap view. */
(function(){
'use strict';
const kindList=[['mcq','Trắc nghiệm A–D',10],['tf4','Đúng/Sai bốn ý',4],['short','Trả lời ngắn',4],['essay','Tự luận',2]];
const esc=s=>EduPlanChem.esc(String(s??''));
function reportTable(){const g=Number(app.grade),cs=curriculum[String(g)]||[];
 return cs.map(ch=>{const chRows=bank.filter(q=>q.grade===g&&q.chapter===ch.name),n=chRows.length;
 return `<section class="card"><h2>Chương ${ch.no}. ${esc(ch.name)} <span class="tag">${n} câu</span></h2><div class="lesson-plan-grid">${ch.lessons.map(l=>{const qs=chRows.filter(q=>q.lesson===l.name),n=qs.length;
 const type=kindList.map(([k,name,t])=>`${name}: ${qs.filter(q=>q.kind===k).length}/${l.name.startsWith('Ôn tập')?Math.max(1,Math.round(t/2)):t}`).join(' · ');
 return `<div class="lesson-plan-row"><div><b>Bài ${l.no}. ${esc(l.name)}</b><small>${esc(type)}</small></div><div class="coverage-count ${n===0?'empty':n<10?'low':'good'}">${n} câu</div><button type="button" class="btn" onclick="setLessonLink(${g},${jsAttr(ch.name)},${jsAttr(l.name)},'practice')" ${n?'':'disabled'}>Luyện ngay</button></div>`;}).join('')}</div></section>`;}).join('');
}
function planningPage(){const q=bank.filter(x=>x.grade===Number(app.grade)),n=q.length;
return `<div class="hero"><small>EDUPLAN AI · KẾ HOẠCH NÂNG CAO CHẤT LƯỢNG</small><h1>Những câu hỏi cần bổ sung</h1><p>Thống kê trực tiếp từ ngân hàng đang công bố. Không tự tạo, không chèn câu chưa kiểm duyệt vào bài của học sinh.</p></div>
<div class="card"><h2>Chọn khối lớp</h2>${field('Khối lớp','grade',[[10,'Hóa học 10'],[11,'Hóa học 11'],[12,'Hóa học 12']],app.grade)}<div class="metrics"><div class="metric"><strong>${n}</strong><span>Câu hiện có</span></div><div class="metric"><strong>${q.filter(x=>x.kind==='mcq').length}</strong><span>Trắc nghiệm A–D</span></div><div class="metric"><strong>${q.filter(x=>x.kind==='tf4').length}</strong><span>Đúng/Sai bốn ý</span></div><div class="metric"><strong>${q.filter(x=>x.kind==='short').length}</strong><span>Trả lời ngắn</span></div></div>
<p class="notice alert">Mức tối thiểu GỢI Ý cho mỗi bài thường: 10 A–D, 4 câu Đúng/Sai bốn ý, 4 trả lời ngắn và 2 tự luận. Đề Form 2025 chính thức cần 18 A–D, 4 Đúng/Sai bốn ý và 6 trả lời ngắn; phạm vi quá hẹp có thể chưa đủ câu.</p>
<div class="actions"><a class="btn primary" href="./reports/Bao_Cao_Tich_Hop_14_De_Hoa_11_12_EduPlan_7_13.docx" download>Tải kế hoạch Word .docx</a><a class="btn" href="./reports/Thieu_Cau_Hoi_78_Bai_KNTT.csv" download>Tải bảng 78 bài CSV</a></div></div>${reportTable()}`;
}
const before=draw;
draw=function(){return app.tab==='planning'?planningPage():before();};
})();
