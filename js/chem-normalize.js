/* EduPlan AI 7.6: non-destructive, review-first chemical notation formatter.
   Deliberately NEVER rewrites raw question-bank data or infers scientific correctness. */
(function(global){
'use strict';
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ELEMENTS=new Set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split(' '));
function formulaToken(str,allowPlain=false){
  if(!/^[A-Z(]/.test(str))return null;
  let text=str,charge='';
  const caret=text.match(/\^(?:\{)?([0-9]*[+-])(?:\})?$/);
  if(caret){charge=caret[1];text=text.slice(0,caret.index);}
  else { const sign=text.match(/([+-])$/);if(sign){text=text.slice(0,-1);const mono=text.match(/^([A-Z][a-z]?)(\d{1,2})$/);if(mono&&ELEMENTS.has(mono[1])){charge=mono[2]+sign[1];text=mono[1];}else charge=sign[1];}}
  let i=0,parts=[],foundNumber=false;
  while(i<text.length){
    if(text[i]==='('){const match=text.slice(i).match(/^\((?:[A-Z][a-z]?\d*)+\)(\d*)/);if(!match)return null;const inner=match[0].slice(1,match[0].indexOf(')'));let nested=formulaToken(inner,true);if(!nested)return null;parts.push({text:'('},...nested.parts,{text:')'});if(match[1]){parts.push({text:match[1],position:'sub'});foundNumber=true;}i+=match[0].length;continue;}
    const m=text.slice(i).match(/^([A-Z][a-z]?)(\d*)/);if(!m||!ELEMENTS.has(m[1]))return null;
    parts.push({text:m[1]});if(m[2]){parts.push({text:m[2],position:'sub'});foundNumber=true;}i+=m[0].length;
  }
  if(!parts.length||(!foundNumber&&!charge&&!allowPlain))return null;
  if(charge)parts.push({text:charge,position:'sup'});
  return {parts};
}
// Strong boundary checks: no substitutions inside ordinary words or mixed-case element names.
const candidate=/(?<![\p{L}0-9_])(?:[A-Z][a-z]?\d*(?:\((?:[A-Z][a-z]?\d*)+\)\d*)?){1,12}(?:\^(?:\{)?\d*[+-](?:\})?|[+-])?(?![\p{L}0-9_])/gu;
const config=/\b[1-7][spdf](?:[1-9]|1[0-4])\b/g;
function basicSegments(input){
 const text=String(input??''),matches=[];for(const m of text.matchAll(candidate)){if(m[0].length>80)continue;const parsed=formulaToken(m[0]);if(parsed)matches.push({start:m.index,end:m.index+m[0].length,parts:parsed.parts});}
 // When a molecular formula follows a stoichiometric coefficient, format the formula only.
 // This changes visual subscript runs, never the original number or source text.
 const withCoefficient=/(?<![\p{L}0-9_])(\d{1,3})((?:[A-Z][a-z]?\d*(?:\((?:[A-Z][a-z]?\d*)+\)\d*)?){1,12})(?![\p{L}0-9_])/gu;
 for(const m of text.matchAll(withCoefficient)){
  if(matches.some(x=>m.index<x.end&&m.index+m[0].length>x.start))continue;
  const f=formulaToken(m[2]);if(f)matches.push({start:m.index,end:m.index+m[0].length,parts:[{text:m[1]},...f.parts]});
 }
 // Electron notation: explicit orbital labels, not element symbols.
 for(const m of text.matchAll(config)){if(matches.some(x=>m.index<x.end&&m.index+m[0].length>x.start))continue;let cut=m[0].search(/\d+$/);matches.push({start:m.index,end:m.index+m[0].length,parts:[{text:m[0].slice(0,cut)},{text:m[0].slice(cut),position:'sup'}]});}
 matches.sort((a,b)=>a.start-b.start);let seg=[],last=0;for(const m of matches){if(m.start<last)continue;if(m.start>last)seg.push({text:text.slice(last,m.start)});seg.push(...m.parts);last=m.end;}if(last<text.length)seg.push({text:text.slice(last)});return seg.length?seg:[{text}];
}
function fromCe(raw){const rx=/(<=>|<->|->|<-|⇌|→|\+|\s+)/g;let arr=[],last=0;for(const m of raw.matchAll(rx)){if(m.index>last)arr.push(...ceChunk(raw.slice(last,m.index)));const v=m[0];arr.push({text:v==='->'?'→':v==='<-'?'←':v==='<=>'||v==='<->'?'⇌':v});last=m.index+v.length;}arr.push(...ceChunk(raw.slice(last)));return arr;}
function ceChunk(s){const m=String(s).match(/^(\d+)([A-Z][\s\S]+)$/);return m?[{text:m[1]},...basicSegments(m[2])]:basicSegments(s);}
function latexFallback(src){
 const iso=src.match(/^\s*\{\}\^\{(\d+)\}_\{(\d+)\}\\mathrm\{([A-Z][a-z]?)\}\s*$/);if(iso&&ELEMENTS.has(iso[3]))return [{text:iso[1],position:'sup'},{text:iso[2],position:'sub'},{text:iso[3]}];
 const frac=src.match(/^\\frac\{([^{}]+)\}\{([^{}]+)\}$/);if(frac)return [{text:'(' + frac[1] + ')/(' + frac[2] + ')'}];
 if(/^\\ce\{[\s\S]*\}$/.test(src))return fromCe(src.slice(4,-1));
 return [{text:'Biểu thức cần xem bằng trình hiển thị toán học',warning:true}];
}
function segments(text){const s=String(text??''),token=/\\ce\{[^{}]{1,300}\}|\\\([\s\S]{1,400}?\\\)|\\\[[\s\S]{1,400}?\\\]/g;let a=[],last=0;for(const m of s.matchAll(token)){if(m.index>last)a.push(...basicSegments(s.slice(last,m.index)));const chunk=m[0];a.push(...(chunk.startsWith('\\ce{')?fromCe(chunk.slice(4,-1)):latexFallback(chunk.slice(2,-2))));last=m.index+chunk.length;}a.push(...basicSegments(s.slice(last)));return a;}
function html(text){return segments(text).map(p=>p.warning?`<span class="chem-warning" title="Chưa đủ thông tin để chuyển công thức">${esc(p.text)}</span>`:p.position==='sub'?`<sub class="chem-sub">${esc(p.text)}</sub>`:p.position==='sup'?`<sup class="chem-sup">${esc(p.text)}</sup>`:esc(p.text)).join('');}
// No blind auto-correction. Flag suspicious data for review instead.
function inspect(q,ctx){const problems=[],chapterNames=ctx?.chapters||[],lessonNames=ctx?.lessons||[];
 const stem=String(q.stem||''),combined=[stem,...Object.values(q.options||{}),...Object.values(q.statements||{})].join(' ');
 if(!q.topic&&!q.knowledge_topic)problems.push({code:'TOPIC_UNCONFIRMED',label:'Chưa xác minh chủ đề kiến thức'});
 if(!q.learning_outcome&&!q.expected_outcome)problems.push({code:'OUTCOME_UNCONFIRMED',label:'Chưa liên kết yêu cầu cần đạt GDPT 2018'});
 if(!stem.trim())problems.push({code:'MISSING_STEM',label:'Thiếu nội dung câu hỏi'});
 if(!q.lesson||!lessonNames.includes(q.lesson))problems.push({code:'LESSON_UNCONFIRMED',label:'Bài học chưa được xác nhận theo mục lục KNTT'});
 if(!['NB','TH','VD','VDC'].includes(q.difficulty))problems.push({code:'LEVEL_UNCONFIRMED',label:'Mức độ nhận thức chưa được thẩm định'});
 if(!chapterNames.includes(q.chapter))problems.push({code:'CHAPTER_MISMATCH',label:'Chương không khớp danh mục KNTT'});
 if(q.needs_review!==false)problems.push({code:'SOURCE_REVIEW',label:'Nguồn chưa qua kiểm tra khoa học độc lập'});
 if(/\[pic\]|\\(?:frac|sqrt|ce|left|right|mathrm)|\{\{.*?\}\}|\bMathType\b|\bOLE\b/i.test(combined))problems.push({code:'COMPLEX_FORMULA',label:'Có công thức/đối tượng cần kiểm tra trực quan'});
 if(q.kind==='mcq'&&Object.keys(q.options||{}).filter(k=>/^[A-D]$/.test(k)).length!==4)problems.push({code:'MCQ_OPTIONS',label:'Phương án A–D chưa đủ'});
 if(q.kind==='tf4'&&Object.keys(q.statements||{}).length+Object.keys(q.options||{}).length<4)problems.push({code:'TF_STATEMENTS',label:'Các ý Đúng/Sai chưa đủ hoặc chưa trích xuất'});
 if((q.media||[]).length)problems.push({code:'SOURCE_IMAGE',label:'Có hình minh họa, cần đối chiếu dữ kiện với bản gốc'});
 return problems;
}

// Basic mass-balance checker for neutral molecular equations only. Not a chemistry proof.
function atomCount(formula){
 let i=0;function group(stop=false){const count={};function add(k,v){count[k]=(count[k]||0)+v;}
  while(i<formula.length){if(formula[i]===')'){if(!stop)throw Error('Ngoặc đóng dư');i++;return count;}
   if(formula[i]==='('){i++;const g=group(true);const n=number();for(const [k,v] of Object.entries(g))add(k,v*n);continue;}
   const m=formula.slice(i).match(/^([A-Z][a-z]?)/);if(!m||!ELEMENTS.has(m[1]))throw Error('Ký hiệu nguyên tố không hợp lệ');i+=m[1].length;add(m[1],number());
  }if(stop)throw Error('Thiếu ngoặc đóng');return count;}
 function number(){const m=formula.slice(i).match(/^\d+/);if(!m)return 1;i+=m[0].length;const n=Number(m[0]);if(!n||n>1000)throw Error('Chỉ số ngoài phạm vi');return n;}
 const r=group();if(i!==formula.length)throw Error('Sai cú pháp');return r;
}
function checkEquation(input){
 const raw=String(input||'').trim().replace(/^\\ce\{([\s\S]*)\}$/,'$1').replace(/\s*\((?:s|l|g|aq)\)\s*/gi,'').replaceAll('→','->');
 if(/[⇌⇄↔=]/.test(raw)&&!raw.includes('->'))return {status:'unsupported',detail:'Phản ứng thuận nghịch cần đối chiếu điều kiện cân bằng, không kiểm định bằng công cụ đơn giản này.'};
 if(/[\^\[\]]/.test(raw))return {status:'unsupported',detail:'Ion/điện tích và phức chất cần kiểm tra cả bảo toàn điện tích; công cụ này chỉ kiểm tra phương trình phân tử trung hòa.'};
 const split=raw.split('->');if(split.length!==2)return {status:'invalid',detail:'Nhập phương trình dạng 2H2 + O2 -> 2H2O.'};
 function side(t){const total={};for(const item of t.split(/\s*\+\s*/)){const m=item.trim().match(/^(\d+)?\s*((?:[A-Z][a-z]?|[()\d])+?)$/);if(!m)throw Error('Không nhận diện được chất: '+item);const n=Number(m[1]||1);if(n>1000)throw Error('Hệ số quá lớn');const atoms=atomCount(m[2]);for(const [k,v] of Object.entries(atoms))total[k]=(total[k]||0)+v*n;}return total;}
 try{const lhs=side(split[0]),rhs=side(split[1]),all=[...new Set([...Object.keys(lhs),...Object.keys(rhs)])],diff=all.filter(x=>(lhs[x]||0)!==(rhs[x]||0));return {status:diff.length?'unbalanced':'balanced',detail:diff.length?'Chưa bảo toàn số nguyên tử: '+diff.join(', '):'Đã bảo toàn số nguyên tử. Chưa xác nhận sản phẩm, điều kiện hoặc tính khả thi hóa học.',lhs,rhs};}
 catch(e){return {status:'unsupported',detail:'Không thể kiểm định an toàn: '+e.message};}
}
global.EduPlanChem=Object.freeze({html,segments,inspect,formulaToken,checkEquation,esc});
})(window);
