/* EduPlan AI 7.14 – Teacher-only staging and upload (never public answer keys). */
(function(){'use strict';
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let curriculum={},existing=[],staged=[],active=0;const MAX_FILE=18*1024*1024,MAX_RECORDS=2000;
function message(s,err=false){$('message').textContent=s;$('message').style.color=err?'#b42318':'#0f645d';}
function defaults(x={}){return {id:String(x.id||'').trim(),grade:Number(x.grade)||10,chapter_no:Number(x.chapter_no)||1,lesson_id:Number(x.lesson_id)||0,chapter:String(x.chapter||''),lesson:String(x.lesson||''),part:Number(x.part)||1,kind:String(x.kind||'mcq'),difficulty:String(x.difficulty||'NB'),stem:String(x.stem||''),options:(x.options&&typeof x.options==='object')?x.options:{},statements:(x.statements&&typeof x.statements==='object')?x.statements:{},answer:typeof x.answer==='object'?x.answer:String(x.answer||''),explanation:String(x.explanation||''),source_title:String(x.source_title||''),source_question_number:x.source_question_number||0,needs_review:x.needs_review!==false,complex_media:!!x.complex_media,confirmed:!!x.confirmed,media_fixed:!!x.media_fixed};}
function chapter(x){return (curriculum[String(x.grade)]||[]).find(c=>c.no===Number(x.chapter_no));}
function lesson(x){return chapter(x)?.lessons.find(l=>l.no===Number(x.lesson_id));}
function harmonize(x){const ch=chapter(x);if(ch){x.chapter=ch.name;if(!x.lesson_id||!ch.lessons.some(l=>l.no===x.lesson_id))x.lesson_id=ch.lessons[0]?.no||0;x.lesson=lesson(x)?.name||'';}x.part=({mcq:1,tf4:2,short:3,essay:4}[x.kind]||x.part||1);}
function normalize(s){return String(s||'').toLocaleLowerCase('vi').normalize('NFKC').replace(/[\s\p{P}\p{S}]+/gu,'').trim();}
function hash(s){let h=2166136261;for(const c of String(s)){h^=c.codePointAt(0);h=Math.imul(h,16777619);}return (h>>>0).toString(36);}
function questionID(x){return 'IMP-'+x.grade+'-'+x.chapter_no+'-'+x.part+'-'+hash(x.source_title+'|'+x.source_question_number+'|'+x.stem);}
function findDup(x,skip=-1){const n=normalize(x.stem);return existing.some(y=>y.id===x.id||normalize(y.stem)===n)||(staged.some((y,i)=>i!==skip&&(y.id===x.id||normalize(y.stem)===n)));}
function valid(x,i){const problems=[];const ch=chapter(x),ls=lesson(x);
 if(![10,11,12].includes(x.grade)||!ch||!ls||!x.stem.trim())problems.push('Thiếu khối / chương / bài / câu hỏi');
 if(!['NB','TH','VD','VDC'].includes(x.difficulty))problems.push('Mức độ không hợp lệ');
 if(x.stem.length>12000)problems.push('Nội dung quá dài');
 if(x.kind==='mcq'&&'ABCD'.split('').some(k=>!String(x.options?.[k]||'').trim()))problems.push('Chưa đủ 4 phương án A–D');
 if(x.kind==='tf4'&&'abcd'.split('').some(k=>!String(x.statements?.[k]||'').trim()))problems.push('Chưa đủ 4 nhận định a–d');
 if(x.kind==='mcq'&&!/^[ABCD]$/.test(String(x.answer).trim().toUpperCase()))problems.push('Khóa A–D chưa hợp lệ');
 if(x.kind==='tf4'&&(!x.answer||typeof x.answer!=='object'||'abcd'.split('').some(k=>!['D','S'].includes(String(x.answer[k]||'').toUpperCase()))))problems.push('Thiếu khóa Đúng/Sai từng ý');
 if(['short','essay'].includes(x.kind)&&!String(x.answer||'').trim())problems.push('Chưa nhập đáp án hoặc hướng dẫn chấm');
 if(!x.explanation.trim())problems.push('Thiếu lời giải được kiểm chứng');
 if(x.complex_media)problems.push('Có MathType, hình hoặc đối tượng Word cần đối chiếu');
 if(findDup(x,i))problems.push('Trùng ID hoặc trùng nội dung trong ngân hàng');
 if(!x.confirmed)problems.push('Chưa xác nhận đã đối chiếu dữ liệu và đáp án');
 return problems;
}
function setVals(x){const items=[['grade',x.grade],['chapter_no',x.chapter_no],['lesson_id',x.lesson_id],['kind',x.kind],['difficulty',x.difficulty],['stem',x.stem],['answer',typeof x.answer==='object'?JSON.stringify(x.answer):x.answer],['explanation',x.explanation],['source_title',x.source_title]];for(const [id,v]of items)if($(id))$(id).value=v;
 $('chapter_no').innerHTML=(curriculum[String(x.grade)]||[]).map(c=>`<option value="${c.no}">${esc('Chương '+c.no+'. '+c.name)}</option>`).join('');$('chapter_no').value=String(x.chapter_no);
 $('lesson_id').innerHTML=(chapter(x)?.lessons||[]).map(l=>`<option value="${l.no}">${esc('Bài '+l.no+'. '+l.name)}</option>`).join('');$('lesson_id').value=String(x.lesson_id);
 $('options').value=x.kind==='mcq'?'ABCD'.split('').map(k=>k+'|'+String(x.options?.[k]||'')).join('\n'):x.kind==='tf4'?'abcd'.split('').map(k=>k+'|'+String(x.statements?.[k]||'')).join('\n'):'';
 $('confirmed').checked=!!x.confirmed;$('media-fixed').checked=!!x.media_fixed;
}
function partName(p){return {1:'I · A–D',2:'II · Đúng/Sai',3:'III · Trả lời ngắn',4:'IV · Tự luận'}[p]||'';}
function editor(i=active){if(!staged.length){$('editor').hidden=true;return;}active=Math.max(0,Math.min(staged.length-1,i));const x=staged[active];$('editor').hidden=false;$('editing').textContent='Đang rà soát câu '+(active+1)+'/'+staged.length+' · '+(x.id||'chưa có ID');setVals(x);$('problems').textContent=valid(x,active).join(' • ')||'Đạt điều kiện dữ liệu, có thể đồng bộ sau khi lưu.';}
function collect(){const x=staged[active];if(!x)return;
 const oldSig=[x.grade,x.chapter_no,x.part,x.stem].join('|');
 for(const f of ['grade','chapter_no','lesson_id'])x[f]=Number($(f).value);
 for(const f of ['kind','difficulty','stem','explanation','source_title'])x[f]=$(f).value;
 const val=$('answer').value.trim();if(x.kind==='tf4'){try{x.answer=JSON.parse(val);}catch{x.answer=val;}}else x.answer=val;
 let opts={};$('options').value.split('\n').forEach(line=>{const m=line.match(/^\s*([A-Da-d])\s*\|\s*(.*)$/);if(m)opts[m[1]]=m[2];});if(x.kind==='tf4')x.statements=opts;else if(x.kind==='mcq')x.options=opts;
 harmonize(x);x.confirmed=$('confirmed').checked; x.media_fixed=$('media-fixed').checked; if(x.media_fixed&&x.confirmed)x.complex_media=false;
 if(oldSig!==[x.grade,x.chapter_no,x.part,x.stem].join('|'))x.id=questionID(x);saveLocal();
}
function csvRows(text){let out=[],row=[],s='',quoted=false;for(let i=0;i<text.length;i++){let c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){s+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){row.push(s);s='';}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(s);if(row.some(v=>v.trim()))out.push(row);row=[];s='';}else s+=c;}row.push(s);if(row.some(v=>v.trim()))out.push(row);return out;}
function parseCSV(text){const rows=csvRows(text.replace(/^\uFEFF/,'')),keys=rows.shift().map(x=>x.trim());return rows.map(row=>{let o={};keys.forEach((k,i)=>o[k]=row[i]||'');if(typeof o.options==='string'&&o.options.startsWith('{'))try{o.options=JSON.parse(o.options);}catch{};if(typeof o.statements==='string'&&o.statements.startsWith('{'))try{o.statements=JSON.parse(o.statements);}catch{};return o;});}
function docxToQuestionRows(source){const {paragraphs,originalName}=source;let m=originalName.match(/\b(10|11|12)\.(\d+)/),grade=m?Number(m[1]):10,chapNo=m?Number(m[2]):1;let part=1,rows=[],cur=null,solution=false;
 function flush(){if(!cur)return;cur.stem=cur.stem.trim();cur.explanation=cur.explanation.trim();if(cur.stem){const x=defaults(cur);harmonize(x);x.id=questionID(x);rows.push(x);}cur=null;}
 function addOptions(text){let matches=[...text.matchAll(/(^|\s)([ABCD])\s*[.\)]\s*/g)];if(matches.length>=1){if(matches[0].index>0)cur.stem+=' '+text.slice(0,matches[0].index).trim();matches.forEach((a,i)=>{let start=a.index+a[0].length,end=i+1<matches.length?matches[i+1].index:text.length;cur.options[a[2]]=text.slice(start,end).trim();});return true;}return false;}
 for(const p of paragraphs){let s=p.text.replace(/\s+/g,' ').trim();if(!s)continue;
 let ph=s.match(/^PHẦN\s+(I{1,3}|IV)\s*[.:]/i);if(ph){flush();part={I:1,II:2,III:3,IV:4}[ph[1].toUpperCase()]||part;continue;}
 let c=s.match(/^Câu\s*(\d+)\s*[.:]\s*(.*)$/i);if(c){flush();cur={grade,chapter_no:chapNo,part,kind:({1:'mcq',2:'tf4',3:'short',4:'essay'}[part]),stem:c[2],options:{},statements:{},answer:'',explanation:'',source_title:originalName,source_question_number:Number(c[1]),complex_media:!!p.flags.length};solution=false;continue;}
 if(!cur)continue;if(p.flags.length)cur.complex_media=true;
 if(/^(Hướng dẫn giải|Lời giải|Đáp án)\s*:?(.*)$/i.test(s)){solution=true;let tail=s.replace(/^(Hướng dẫn giải|Lời giải|Đáp án)\s*:?/i,'').trim();if(tail)cur.explanation+=' '+tail;continue;}
 if(solution){cur.explanation+=' '+s;continue;}
 if(part===1){if(!addOptions(s))cur.stem+=' '+s;}
 else if(part===2){let a=s.match(/^([a-d])\s*[).:]\s*(.*)$/i);if(a)cur.statements[a[1].toLowerCase()]=a[2];else cur.stem+=' '+s;}
 else cur.stem+=' '+s;
 }
 flush();return rows;
}
async function importFile(file){if(file.size>MAX_FILE)throw Error('Tệp vượt 18 MB');const name=file.name.toLowerCase();let rows;
 if(name.endsWith('.docx'))rows=docxToQuestionRows(await EduPlanDocxReader.read(file));
 else if(name.endsWith('.json')){const x=JSON.parse(await file.text());rows=Array.isArray(x)?x:x.questions||[];}
 else if(name.endsWith('.csv'))rows=parseCSV(await file.text());
 else throw Error('Chỉ hỗ trợ DOCX, JSON, CSV');
 if(!Array.isArray(rows)||rows.length>MAX_RECORDS)throw Error('Không thấy mảng câu hỏi hoặc quá 2.000 câu/tệp');
 return rows.map(r=>{const x=defaults({...r,source_title:r.source_title||file.name});if(!r.chapter_no){const m=file.name.match(/\b(10|11|12)\.(\d+)/);if(m){x.grade=+m[1];x.chapter_no=+m[2];}} x.confirmed=false;x.media_fixed=false;harmonize(x);x.id=x.id||questionID(x);return x;});
}
async function saveLocal(){try{localStorage.setItem('eduplan_teacher_staging_714',JSON.stringify(staged));}catch{message('Bộ nhớ thiết bị đầy. Hãy xuất bản JSON dự phòng; dữ liệu chưa đồng bộ sẽ không tồn tại trên thiết bị khác.',true);}}
function render(){let stat={ready:0,review:0,duplicate:0};staged.forEach((x,i)=>{const v=valid(x,i);v.length?stat.review++:stat.ready++;if(v.some(s=>s.includes('Trùng')))stat.duplicate++;});$('summary').innerHTML=`<b>${staged.length}</b> câu đã nhập · <b>${stat.ready}</b> đủ điều kiện để gửi duyệt · <b>${stat.review}</b> cần rà soát · <b>${stat.duplicate}</b> nghi trùng`;
 const g=$('filter-grade').value,p=$('filter-part').value,term=$('filter-term').value.trim().toLocaleLowerCase('vi');
 const items=staged.map((x,i)=>({...x,i})).filter(x=>(!g||String(x.grade)===g)&&(!p||String(x.part)===p)&&(!term||[x.stem,x.chapter,x.lesson,x.source_title].join(' ').toLocaleLowerCase('vi').includes(term)));
 $('list').innerHTML=items.slice(0,200).map(x=>`<button class="question-item ${x.i===active?'selected':''}" onclick="EduPlanImporter.open(${x.i})"><strong>${esc(x.grade+' · '+x.chapter+' · '+partName(x.part))}</strong><span>Bài: ${esc(x.lesson)} · ${esc(x.stem.slice(0,130))}</span><small>${valid(x,x.i).length?'Cần rà soát':'Đủ điều kiện gửi duyệt'} · ${esc(x.source_title)}</small></button>`).join('')||'<p>Chưa có câu hỏi phù hợp.</p>';
 editor();}
function downloadJson(data,name){const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2500);}
async function upload(){collect();const ready=staged.filter((x,i)=>!valid(x,i));if(!ready.length){message('Chưa có câu đạt đủ điều kiện. Hãy rà soát và đánh dấu xác nhận.',true);render();return;}
 if(!confirm(`Gửi ${ready.length} câu lên máy chủ để công bố cho học sinh? Cần xác nhận chuyên môn của giáo viên.`))return;
 const token=$('token').value;if(token.length<12){message('Nhập khóa quản trị hợp lệ (chỉ được cấu hình trên máy chủ).',true);return;}
 $('upload').disabled=true;try{let accepted=0,skipped=0;for(let i=0;i<ready.length;i+=75){const res=await fetch('../api/admin-bank',{method:'POST',headers:{'Content-Type':'application/json','X-EduPlan-Admin':token},body:JSON.stringify({questions:ready.slice(i,i+75)})});const x=await res.json();if(!res.ok)throw Error(x.error||'Máy chủ không chấp nhận yêu cầu');accepted+=x.inserted||0;skipped+=x.skipped||0;}
 message(`Đã ghi thêm ${accepted} câu mới vào cơ sở dữ liệu online; ${skipped} câu đã tồn tại hoặc bị trùng. Học sinh sẽ nạp câu đã công bố khi tải lại trang.`);
 }catch(err){message('Đồng bộ thất bại: '+err.message+' — vẫn giữ dữ liệu nguồn tại trình duyệt để xuất dự phòng.',true);}finally{$('upload').disabled=false;}}
window.EduPlanImporter={open:i=>{collect();render();editor(i);},reload:render};
window.addEventListener('DOMContentLoaded',async()=>{
 const [c,banks]=await Promise.all([fetch('../data/curriculum.json').then(x=>x.json()),Promise.all([10,11,12].map(g=>fetch('../data/hoa'+g+'.json').then(x=>x.json())))]);curriculum=c;existing=banks.flat();try{staged=JSON.parse(localStorage.getItem('eduplan_teacher_staging_714')||'[]').map(defaults);}catch{staged=[];}
 $('source-files').addEventListener('change',async ev=>{let imported=0;for(const file of ev.target.files){try{const rows=await importFile(file);staged.push(...rows);imported+=rows.length;}catch(err){message('Không nhập được '+file.name+': '+err.message,true);}}await saveLocal();render();message(`Đã đọc ${imported} câu từ ${ev.target.files.length} tệp. Tất cả đang ở trạng thái chờ giáo viên rà soát. KHÔNG tự duyệt.`);ev.target.value='';});
 $('save').onclick=()=>{collect();render();message('Đã lưu bản nháp trên thiết bị, chưa đồng bộ toàn trường.');};
 $('chapter_no').onchange=()=>{collect();let x=staged[active];x.chapter_no=Number($('chapter_no').value);harmonize(x);render();};
 $('grade').onchange=()=>{collect();staged[active].grade=Number($('grade').value);staged[active].chapter_no=1;harmonize(staged[active]);render();};
 $('kind').onchange=()=>{collect();staged[active].kind=$('kind').value;harmonize(staged[active]);render();};
 for(const id of ['filter-grade','filter-part','filter-term'])$(id).addEventListener('input',render);
 $('export').onclick=()=>{collect();downloadJson({version:'7.14',exportedAt:new Date().toISOString(),questions:staged},'EduPlan_714_Kho_cho_tham_dinh_PRIVATE.json');message('Đã tải kho thẩm định có đáp án. Chỉ lưu riêng tư, KHÔNG đăng công khai.');};
 $('upload').onclick=upload;
 $('clear').onclick=()=>{if(confirm('Xóa bản nháp trên thiết bị này? Hành động không xóa ngân hàng máy chủ.')){staged=[];localStorage.removeItem('eduplan_teacher_staging_714');render();}};
 render();
});
})();
