/* CHEM-MAP TUTOR AI 2.0 — rule-based, locally auditable learning engine. */
(function(root){
  'use strict';
  const E = {};
  const DEGREES=['Nhận biết','Thông hiểu','Vận dụng','Vận dụng cao'];
  const clean=s=>String(s??'').trim();
  const round=(n,d=2)=>Number(Number(n||0).toFixed(d));
  const tagCorrect=(q,answer)=>{
    if(q.type==='mcq')return typeof answer!=='undefined'&&answer!==null&&answer!==''&&Number(answer)===Number(q.correct);
    if(q.type==='short'){
      const v=clean(answer).replace(',','.'); if(v===''||!/^[+-]?(\d+\.?\d*|\.\d+)$/.test(v))return false;
      return Math.abs(Number(v)-Number(q.correct))<=Number(q.tolerance??0.001);
    }
    return false;
  };
  E.levels=DEGREES;
  E.shuffle=(xs)=>{const a=[...xs];for(let i=a.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;};
  E.evaluate=function(q,answer){
    if(q.type==='mcq'){
      const answered=clean(answer)!=='';
      const ok=tagCorrect(q,answer);
      let diagnostics=[];
      if(answered&&!ok){
        const d=q.distractors?.[String(answer)];
        diagnostics=[{code:d?.code??null,text:d?.hypothesis??'Phương án này chưa đúng; cần đối chiếu với lời giải chuẩn.',evidence:`Người học chọn ${'ABCD'[Number(answer)]??'?'}; đáp án chuẩn ${'ABCD'[Number(q.correct)]}.`,confidence:'Giả thuyết từ phương án nhiễu',status:'suspected'}];
      }
      return {earned:ok?1:0,max:1,correct:ok,answered,diagnostics,answerText:answered?('ABCD'[Number(answer)]??'—'):'Chưa trả lời',correctText:'ABCD'[Number(q.correct)]};
    }
    if(q.type==='tf'){
      const a=Array.isArray(answer)?answer:[];
      let right=0,completed=0;const diagnostics=[];
      q.correct.forEach((v,i)=>{
        const response=a[i];
        if(response==='T'||response==='F'){
          completed++;
          if((response==='T')===v)right++;
          else diagnostics.push({code:null,text:`Ý ${'abcd'[i]}) chưa chính xác. ${q.statementExplanations?.[i]||'Hãy đối chiếu căn cứ hóa học.'}`,evidence:`Ý ${'abcd'[i]}: chọn ${response==='T'?'Đúng':'Sai'} thay vì ${v?'Đúng':'Sai'}.`,confidence:'Sai lệch đã quan sát; chưa đủ xác định nguyên nhân',status:'observed'});
        }
      });
      return {earned:right/q.correct.length,max:1,correct:right===q.correct.length,answered:completed>0,diagnostics,answerText:q.correct.map((_,i)=>a[i]==='T'?'Đ':a[i]==='F'?'S':'—').join(' / '),correctText:q.correct.map(x=>x?'Đ':'S').join(' / '),parts:right};
    }
    if(q.type==='short'){
      const answered=clean(answer)!=='';const ok=tagCorrect(q,answer);
      const diagnostics=answered&&!ok?[{code:q.defaultError??null,text:'Kết quả khác đáp án chuẩn. Chưa thể kết luận nguyên nhân khi chỉ có đáp số; hãy ghi các bước để giáo viên xác nhận.',evidence:`Đáp số đã nộp: ${clean(answer)}.`,confidence:'Sai lệch kết quả đã quan sát',status:'observed'}]:[];
      return {earned:ok?1:0,max:1,correct:ok,answered,diagnostics,answerText:answered?clean(answer):'Chưa trả lời',correctText:String(q.correct)};
    }
    if(q.type==='essay'){
      const answered=clean(answer)!=='';
      return {earned:0,max:1,correct:null,answered,diagnostics:[],answerText:answered?clean(answer):'Chưa trả lời',correctText:'Chờ giáo viên chấm theo rubric',pending:true};
    }
    throw Error('Question type not supported: '+q.type);
  };
  E.gradeAttempt=function(questions,answers){
    const results=questions.map(q=>({questionId:q.id,type:q.type,...E.evaluate(q,answers?.[q.id])}));
    const pendingCount=results.filter(r=>r.pending).length;
    const earned=results.reduce((a,r)=>a+r.earned,0);
    const total=results.reduce((a,r)=>a+r.max,0);
    const score=total?round(10*earned/total,2):0;
    const autoTotal=total-pendingCount;
    const autoScore=autoTotal?round(earned/autoTotal*10,2):0;
    return {results,score,autoScore,pendingCount,total,earned,graded:pendingCount===0,incorrect:results.filter(x=>x.correct===false).length};
  };
  E.rescore=function(attempt){
    const result=attempt.results||[];const total=result.length;
    let pending=0,earn=0;
    for(const r of result){if(r.pending)pending++;earn+=Number(r.earned)||0;}
    attempt.pendingCount=pending;attempt.score=total?round(10*earn/total,2):0;
    attempt.graded=pending===0;attempt.incorrect=result.filter(r=>r.correct===false).length;return attempt;
  };
  E.levelIndex=level=>Math.max(0,DEGREES.indexOf(level));
  E.mastery=function(attempts,studentId){
    const by={};for(const a of attempts.filter(x=>x.studentId===studentId)){
      (a.questions||[]).forEach((q,i)=>{
        const r=a.results?.[i];if(!r||r.pending)return;
        const k=q.skill||q.chapter||'Khác';by[k]??={skill:k,earned:0,total:0,items:0,grade:q.grade};
        by[k].earned+=Number(r.earned)||0;by[k].total+=Number(r.max)||1;by[k].items++;
      });
    }
    return Object.values(by).map(x=>({...x,percent:x.total?Math.round(100*x.earned/x.total):0,reliability:x.items>=5?'Có dữ liệu bước đầu':x.items>=3?'Cần thêm minh chứng':'Dữ liệu ít'})).sort((a,b)=>a.percent-b.percent);
  };
  E.plan=function(attempts,bank,studentId,grade){
    const records=attempts.filter(a=>a.studentId===studentId).sort((a,b)=>b.createdAt.localeCompare(a.createdAt)).slice(0,8);
    const errors=[];
    for(const a of records){for(let i=0;i<a.questions.length;i++){
      const q=a.questions[i],r=a.results?.[i];if(!r||r.correct!==false)continue;
      for(const d of r.diagnostics||[])errors.push({code:d.code,skill:q.skill,chapter:q.chapter,grade:q.grade,questionId:q.id,status:d.status,confidence:d.confidence});
    }}
    const counts={};for(const e of errors){const key=e.code||e.skill||e.chapter;counts[key]=(counts[key]||0)+1;}
    const mastery=E.mastery(attempts,studentId).filter(x=>String(x.grade)===String(grade));
    let targets=mastery.filter(x=>x.percent<85).slice(0,3).map(x=>x.skill);
    if(!targets.length)targets=[...new Set(errors.filter(x=>String(x.grade)===String(grade)).map(e=>e.skill))].slice(0,3);
    const available=bank.filter(q=>String(q.grade)===String(grade)&&q.type!=='essay');
    let chosen=[];const used=new Set();
    for(const skill of targets){
      const candidate=available.filter(q=>q.skill===skill&&!used.has(q.id));
      if(candidate.length){const q=candidate.sort((a,b)=>E.levelIndex(a.level)-E.levelIndex(b.level))[0];chosen.push(q);used.add(q.id);}
    }
    const sameLevel=mastery[0]?.percent>=80?'Vận dụng':'Thông hiểu';
    for(const q of E.shuffle(available.filter(q=>!used.has(q.id)&&E.levelIndex(q.level)<=E.levelIndex(sameLevel)+1))){if(chosen.length>=5)break;chosen.push(q);used.add(q.id);}
    return {items:chosen.slice(0,5),targets,topErrors:Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,4),evidenceCount:errors.length,hasHistory:records.length>0,summary:records.length?'Bài luyện đề xuất theo những kỹ năng có kết quả thấp; mức độ tin cậy phụ thuộc số bài đã làm.':'Chưa có dữ liệu lịch sử; hệ thống đề xuất bài khởi động theo khối lớp.'};
  };
  E.validateQuestion=function(q){
    if(!q||!q.id||!q.stem||!q.chapter||!q.grade||!q.type||!q.level)return 'Thiếu trường bắt buộc.';
    if(q.type==='mcq'&&(!Array.isArray(q.options)||q.options.length!==4||!Number.isInteger(Number(q.correct))||Number(q.correct)<0||Number(q.correct)>3))return 'Câu nhiều lựa chọn cần 4 phương án và 1 đáp án hợp lệ.';
    if(q.type==='tf'&&(!Array.isArray(q.statements)||q.statements.length!==4||!Array.isArray(q.correct)||q.correct.length!==4||q.correct.some(x=>typeof x!=='boolean')))return 'Câu Đúng/Sai cần 4 ý và 4 đáp án boolean.';
    if(q.type==='short'&&!Number.isFinite(Number(q.correct)))return 'Câu trả lời ngắn phải có đáp số dạng số.';
    if(q.type==='essay'&&(!Array.isArray(q.rubric)||!q.rubric.length))return 'Câu tự luận cần rubric.';
    return null;
  };
  root.CMEngine=E;
  if(typeof module!=='undefined'&&module.exports)module.exports=E;
})(typeof window!=='undefined'?window:globalThis);
