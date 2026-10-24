from pathlib import Path
root=Path(__file__).parent
b=root/'build_bank.py';s=b.read_text();s=s.replace("mc(12,6,'Thông hiểu','Kim loại kiềm thổ','Trong các hydroxide", "mc(12,5,'Thông hiểu','Đại cương về kim loại','Trong các hydroxide");b.write_text(s)
a=root/'assets/app.js';s=a.read_text()
patches=[
("const allQuestions=()=>base.concat(state.customQuestions||[]).filter(x=>!state.archived?.includes(x.id));", "const allQuestions=()=>base.concat((state.customQuestions||[]).filter(q=>q.approved)).filter(x=>!state.archived?.includes(x.id));"),
("const routes={overview:renderOverview,practice:renderPractice,exams:renderExams,mistakes:renderMistakes,learning:renderLearning,library:renderLibrary,teacher:renderTeacher,reports:renderReports,admin:renderAdmin,about:renderAbout};", "const routes={overview:renderOverview,practice:renderPractice,exams:renderExams,mistakes:renderMistakes,learning:renderLearning,library:renderLibrary,teacher:renderTeacher,reports:renderReports,admin:renderAdmin,about:renderAbout,result:renderResult};"),
('''<button class="btn primary" type="submit">Thêm vào ngân hàng</button></form></section>`}''', '''<button class="btn primary" type="submit">Lưu bản nháp câu hỏi</button></form></section><div class="heading"><h2>Ngân hàng câu hỏi do giáo viên soạn</h2></div><section class="card">${state.customQuestions.length?state.customQuestions.map(q=>`<div class="list-row"><div><b>${esc(q.id)}</b> · ${esc(q.stem)}<div class="tiny subtle">${esc(q.chapter)} · ${esc(typeName(q.type))}</div></div>${q.approved?pill('Đã duyệt','pass'):`<button class="btn sm teal" data-action="approve-question" data-id="${q.id}">Xác nhận kiểm duyệt</button>`}</div>`).join(''):empty('Chưa có câu hỏi do giáo viên biên soạn.')}</section>`}'''),
("case 'random-student':toast", "case 'approve-question':{const q=state.customQuestions.find(x=>x.id===id);if(q&&confirm('Xác nhận đã kiểm tra dữ kiện, công thức, đáp án, lời giải và điều kiện của câu này?')){q.approved=true;q.approvedAt=new Date().toISOString();persist();render();toast('Đã xác nhận kiểm duyệt và đưa câu hỏi vào kho luyện tập.');}break;}\n case 'random-student':toast"),
("toast('Đã lưu câu hỏi mới trong bộ nhớ trình duyệt.');", "toast('Đã lưu bản nháp. Giáo viên cần kiểm tra và duyệt trước khi đưa vào đề.');"),
("const file=ev.target.files?.[0];if(!file)return;try", "const file=ev.target.files?.[0];if(!file)return;if(file.size>5_000_000){toast('Tệp sao lưu vượt 5 MB.');return;}try"),
("el('nav-main').addEventListener('click',ev=>", "document.querySelector('.mobile-menu').addEventListener('click',()=>el('sidebar').classList.toggle('open'));\nel('nav-main').addEventListener('click',ev=>")]
for old,new in patches:
 count=s.count(old)
 print('PATCH',count,old[:65])
 if count!=1: raise ValueError('needle match count:'+str(count))
 s=s.replace(old,new)
a.write_text(s)
e=root/'assets/engine.js';s=e.read_text().replace('attempt.graded=pending===0;return attempt;', 'attempt.graded=pending===0;attempt.incorrect=result.filter(r=>r.correct===false).length;return attempt;');e.write_text(s)
css=root/'assets/style.css';s=css.read_text().replace("@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');\n",'');css.write_text(s)
