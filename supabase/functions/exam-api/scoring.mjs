// Logic thuần, được dùng trên MÁY CHỦ. Không nhập module này trong giao diện học sinh.
export function normalized(s) { return String(s ?? '').trim().normalize('NFC').replace(/\s+/g, ' ').toLowerCase(); }
export function numeric(s) { const t = String(s ?? '').trim().replace(',', '.'); return /^[-+]?(?:\d+\.?\d*|\.\d+)$/.test(t) ? Number(t) : NaN; }
export function gradeOne(q, answer) {
  const p = Number(q.points);
  if (!(p >= 0 && Number.isFinite(p))) throw Error('Biểu điểm không hợp lệ');
  if (q.type === 'essay') return {score:null, status:'pending', max:p};
  let correct = false; let score = 0;
  if (q.type === 'mcq') {
    correct = Boolean(answer) && String(answer) === String(q.answer);
    score = correct ? p : 0;
  } else if (q.type === 'short') {
    const accepted = Array.isArray(q.answer) ? q.answer : [q.answer];
    const tol = q.grading?.tolerance;
    correct = accepted.some(a => tol !== null && tol !== undefined && Number.isFinite(numeric(a)) && Number.isFinite(numeric(answer))
      ? Math.abs(numeric(a)-numeric(answer)) <= Number(tol)
      : normalized(a) !== '' && normalized(a) === normalized(answer));
    score = correct ? p : 0;
  } else if (q.type === 'tf') {
    const keys = (q.statements || []).map(s=>String(s.id));
    const expected = q.answer || {};
    const input = answer && typeof answer === 'object' ? answer : {};
    const matches = keys.filter(k => Object.prototype.hasOwnProperty.call(input,k) && typeof input[k] === 'boolean' && input[k] === expected[k]).length;
    const mode = q.grading?.mode;
    if (mode === 'all_or_nothing') score = matches === keys.length ? p : 0;
    else if (mode === 'per_statement') score = keys.length ? p * matches / keys.length : 0;
    else if (mode === 'score_by_correct_count') {
      const val = q.grading?.scores?.[String(matches)];
      if (typeof val !== 'number' || !Number.isFinite(val) || val < 0 || val > p) throw Error('Thiếu bảng điểm Đúng/Sai');
      score = val;
    } else throw Error('Chưa cấu hình quy tắc chấm Đúng/Sai');
    correct = matches === keys.length;
  } else throw Error('Dạng câu hỏi không hợp lệ');
  return {score: Math.round(score * 10000)/10000, status:correct?'correct':'incorrect', max:p};
}
export function gradeAttempt(questions, answers={}) {
  let autoScore=0, maxScore=0, pending=0, correct=0, incorrect=0, unanswered=0;
  const details=[];
  for(const q of questions) {
    const a = answers[q.id];
    const missing=a===undefined||a===null||a===''||(q.type==='tf'&&Object.keys(a||{}).length===0);
    const graded=gradeOne(q,a);
    maxScore += Number(q.points);
    if(graded.status==='pending') pending++;
    else if(missing) unanswered++;
    else if(graded.status==='correct') correct++;
    else incorrect++;
    if(graded.score!==null) autoScore += graded.score;
    details.push({question_id:q.id,type:q.type,received:a??null,...graded});
  }
  return {auto_score:Math.round(autoScore*10000)/10000,max_score:maxScore, pending, correct,incorrect,unanswered,details,final_score:pending?null:Math.round(autoScore*10000)/10000};
}
export function validateQuestion(q) {
  const problems=[];
  if(!q || !['mcq','tf','short','essay'].includes(q.type)) problems.push('Sai dạng câu hỏi');
  if(!q?.body || !String(q.body).trim()) problems.push('Thiếu nội dung');
  if(!Number.isFinite(Number(q?.points)) || Number(q.points)<=0) problems.push('Chưa xác nhận điểm > 0');
  if(!q?.approved) problems.push('Chưa được giáo viên duyệt');
  if((q?.issues||[]).length) problems.push('Còn cảnh báo nội dung hoặc tài nguyên');
  if(q?.type==='mcq') {
    if(!Array.isArray(q.options)||q.options.length<2||q.options.some(o=>!o.text?.trim() && !o.image)) problems.push('Thiếu phương án');
    if(!q.options?.some(o=>String(o.id)===String(q.answer))) problems.push('Thiếu đáp án hợp lệ');
  }
  if(q?.type==='tf') {
    if(!Array.isArray(q.statements)||q.statements.length===0 || q.statements.some(s=>!s.text?.trim())) problems.push('Thiếu các ý đúng/sai');
    if(q.statements?.some(s=>typeof q.answer?.[s.id]!=='boolean')) problems.push('Chưa khai báo Đúng/Sai của từng ý');
    if(!['all_or_nothing','per_statement','score_by_correct_count'].includes(q.grading?.mode)) problems.push('Thiếu quy tắc chấm');
    if(q.grading?.mode==='score_by_correct_count') {
      for(let n=0;n<=(q.statements||[]).length;n++) {
        const v=q.grading?.scores?.[String(n)];
        if(typeof v!=='number'||v<0||v>Number(q.points)) problems.push('Thiếu/không hợp lệ mức điểm '+n+' ý');
      }
    }
  }
  if(q?.type==='short' && (q.answer===undefined || q.answer===null || String(q.answer).trim()==='')) problems.push('Thiếu đáp án trả lời ngắn');
  if(q?.type==='essay' && !String(q.rubric||'').trim()) problems.push('Thiếu hướng dẫn chấm tự luận');
  return problems;
}
export function publicQuestion(q) {
  return {id:q.id, position:q.position,section:q.section,type:q.type,body:q.body,options:q.options || [],statements:q.statements || [],media:q.media||[],points:q.points};
}
