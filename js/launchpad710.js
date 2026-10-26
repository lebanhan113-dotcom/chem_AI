/* EduPlan AI 7.10: expose every module outside hidden navigation; preserve all features and data. */
(function(){
'use strict';
const ENTRIES = [
 ['home','⌂','Trang chủ','Bắt đầu học và xem tổng quan'],
 ['catalog','▤','Chọn chương & bài KNTT','Hóa 10, 11, 12 · 78 bài'],
 ['mindmap','🧠','Sơ đồ tư duy','Học kiến thức theo chương và bài'],
 ['mistakes','☑','Sổ ôn lỗi sai','57 chuyên đề thường nhầm'],
 ['bank','☷','Kho câu hỏi','Tìm và giải từng câu'],
 ['practice','✍','Luyện từng câu 5/10/15','Xác nhận và tự chuyển câu'],
 ['interactive','✦','Bài tập tương tác','Làm bài trực tiếp trong học liệu'],
 ['selftest','▣','Làm bài kiểm tra','Nộp bài và xem kết quả'],
 ['form2025','📋','Đề Form 2025','18 A–D · 4 Đ/S · 6 ngắn'],
 ['exam','⤨','Tạo & trộn đề','Chọn bài, tạo nhiều mã đề'],
 ['worksheet','▧','Phiếu học tập','Làm trên web hoặc tải DOCX'],
 ['results','▥','Kết quả học tập','Xem bài đã nộp, ôn câu khó'],
 ['chem','⚗','Công cụ Hóa học','Tính toán và kiểm tra công thức'],
 ['assistant','✧','Trợ lý ChatGPT','Hỏi đáp và giải bài tập'],
 ['docs','📚','Tài liệu tham khảo','Nguồn học liệu đáng tin cậy'],
 ['random','♧','Gọi tên ngẫu nhiên','Tương tác trong giờ học'],
 ['quality','◈','Kiểm định câu hỏi','Xem cảnh báo và kiểm tra nguồn']
];
const GROUPS=[
 {title:'01 · Học kiến thức',sub:'Chọn bài và xem học liệu ngay',ids:['home','catalog','mindmap','mistakes','bank']},
 {title:'02 · Luyện tập và kiểm tra',sub:'Trả lời, nộp bài, luyện lại phần chưa vững',ids:['practice','interactive','selftest','form2025','exam','worksheet']},
 {title:'03 · Kết quả và công cụ hỗ trợ',sub:'Theo dõi, tra cứu, tương tác và tải Word',ids:['results','chem','assistant','docs','random','quality']}
];
const LOOKUP=Object.fromEntries(ENTRIES.map(x=>[x[0],x]));
const el=id=>document.getElementById(id);
function makeCard(item,active){
 const [id,icon,label,description]=item;
 return `<button type="button" class="feature710 ${active===id?'active':''}" data-feature="${id}" aria-current="${active===id?'page':'false'}" onclick="navigate('${id}')"><span class="feature-icon710" aria-hidden="true">${icon}</span><span class="feature-text710"><strong>${label}</strong><small>${description}</small></span></button>`;
}
paintMenu=function(){
 const menu=el('menu');if(!menu)return;
 menu.innerHTML=GROUPS.map(group=>`<section class="feature-group710" aria-label="${group.title}"><div class="feature-heading710"><h3>${group.title}</h3><p>${group.sub}</p></div><div class="feature-grid710">${group.ids.map(id=>makeCard(LOOKUP[id],app.tab)).join('')}</div></section>`).join('');
 const status=el('source-status');if(status)status.textContent=bank.length?`✓ Đã sẵn sàng ${bank.length.toLocaleString('vi-VN')} câu hỏi Hóa học 10–12`:'Đang tải ngân hàng câu hỏi…';
 const current=el('workspace-name');if(current)current.textContent=LOOKUP[app.tab]?.[2]||'Học liệu và công cụ';
};
const oldNavigate=navigate;
navigate=function(tab){
 oldNavigate(tab);
 window.requestAnimationFrame(()=>el('workspace')?.scrollIntoView({behavior:'smooth',block:'start'}));
};
const oldLink=setLessonLink;
setLessonLink=function(grade,chapter,lesson,tab='practice'){
 oldLink(grade,chapter,lesson,tab);
 window.requestAnimationFrame(()=>el('workspace')?.scrollIntoView({behavior:'smooth',block:'start'}));
};
})();
