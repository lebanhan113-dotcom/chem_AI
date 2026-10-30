/* Browser Word parser. Uses JSZip local vendor, never auto-fills missing answers. */
(function(){'use strict';
const NS={w:'http://schemas.openxmlformats.org/wordprocessingml/2006/main',r:'http://schemas.openxmlformats.org/officeDocument/2006/relationships',v:'urn:schemas-microsoft-com:vml',a:'http://schemas.openxmlformats.org/drawingml/2006/main',m:'http://schemas.openxmlformats.org/officeDocument/2006/math'};
const get=(node,ns,local)=>node?.getAttributeNS(ns,local)||node?.getAttribute(local)||'';
const descendants=(n,ns,name)=>Array.from(n?.getElementsByTagNameNS(ns,name)||[]);
const direct=(n,ns,name)=>Array.from(n?.childNodes||[]).filter(x=>x.nodeType===1&&x.namespaceURI===ns&&x.localName===name);
const parse=(s)=>new DOMParser().parseFromString(s,'application/xml');
const uuid=()=>crypto.randomUUID?crypto.randomUUID():'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>(c==='x'?Math.random()*16:((Math.random()*4)|8)).toString(16).charAt(0));
const matches=(s,p)=>p.test((s||'').normalize('NFC'));
const isRed=(color)=>{if(!color)return false;const m=color.replace('#','').toUpperCase();if(!/^[0-9A-F]{6}$/.test(m))return false;const n=parseInt(m,16);return ((n>>16)&255)>155 && ((n>>8)&255)<145 && (n&255)<145;};
const pathNormalize=s=>(s||'').replace(/^\//,'').replace(/\\/g,'/');
const shortName=ext=>({'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','gif':'image/gif','webp':'image/webp','svg':'image/svg+xml'})[ext];
async function readWord(file){
 const zip=await JSZip.loadAsync(await file.arrayBuffer());
 const word=zip.file('word/document.xml');if(!word)throw Error('Tệp DOCX không có word/document.xml');
 const xml=parse(await word.async('string'));
 const relxml=zip.file('word/_rels/document.xml.rels'); const rels={};
 if(relxml){const r=parse(await relxml.async('string')); for(const x of Array.from(r.getElementsByTagName('Relationship'))) rels[x.getAttribute('Id')]=x.getAttribute('Target');}
 const body=xml.getElementsByTagNameNS(NS.w,'body')[0];if(!body)throw Error('Không tìm thấy nội dung Word');
 const lines=[];
 const elements=Array.from(body.childNodes).filter(n=>n.nodeType===1);
 function takeParagraph(p){
   let text='';let images=[];let math=false;
   function walk(node){
     if(node.nodeType!==1)return;
     if(node.namespaceURI===NS.w && node.localName==='t'){text+=node.textContent||'';return;}
     if(node.namespaceURI===NS.w && node.localName==='tab'){text+='\t';return;}
     if(node.namespaceURI===NS.w && node.localName==='br'){text+='\n';return;}
     if(node.namespaceURI===NS.m && node.localName==='oMath'){math=true;return;}
     if(node.namespaceURI===NS.w && node.localName==='pict')return;
     for(const ch of Array.from(node.childNodes))walk(ch);
   }
   walk(p);
   const runs=descendants(p,NS.w,'r');
   const firstLabel=runs.find(r=>descendants(r,NS.w,'t').some(t=>t.textContent?.trim()));
   const col=descendants(firstLabel,NS.w,'rPr').flatMap(x=>descendants(x,NS.w,'color'))[0];
   const leadColor=get(col,NS.w,'val')||col?.getAttribute('w:val')||col?.getAttribute('val');
   // images from drawing and VML; record missing when WMF/EMF cannot be shown in HTML
   for(const elm of [...descendants(p,NS.a,'blip'),...descendants(p,NS.v,'imagedata')]){
     const rid=get(elm,NS.r,'embed')||get(elm,NS.r,'id');if(!rid)continue;
     const target=rels[rid];if(!target){images.push({error:'Không có tệp đính kèm cho '+rid});continue;}
     const pathname=pathNormalize(target.startsWith('../')?target.slice(3):target.startsWith('word/')?target:'word/'+target);
     images.push({path:pathname});
   }
   lines.push({text:text.trim(),red:isRed(leadColor),math,images,xml:p});
 }
 for(const x of elements){
   if(x.namespaceURI===NS.w&&x.localName==='p')takeParagraph(x);
   if(x.namespaceURI===NS.w&&x.localName==='tbl')for(const p of descendants(x,NS.w,'p'))takeParagraph(p);
 }
 let section='I',q=null,questions=[],warnings=[];
 async function attach(line,target){
   if(line.math){target.issues.push('Công thức Word (OMML) chưa thể chuyển đổi chính xác; cần chèn ảnh/công thức đã xác thực.');}
   for(const img of line.images){
     if(img.error){target.issues.push(img.error);continue;}
     const ext=(img.path.split('.').pop()||'').toLowerCase(),mime=shortName(ext);
     if(!mime){target.issues.push('Ảnh hoặc công thức '+img.path+' ở định dạng '+ext.toUpperCase()+' chưa hỗ trợ. Cần thay bằng ảnh PNG/JPEG đúng hình gốc.');continue;}
     const f=zip.file(img.path);if(!f){target.issues.push('Không tìm thấy tài nguyên '+img.path);continue;}
     const arr=await f.async('base64');
     (target.media||(target.media=[])).push('data:'+mime+';base64,'+arr);
   }
 }
 let dest=null; // The paragraph owner may be a choice, but warnings always belong to question.
 for(const line of lines){
   const t=line.text.replace(/\s+/g,' ').trim();
   const sec=t.match(/^PHẦN\s+(I{1,3}|IV|V)\s*[:.]/i);
   if(sec){section=sec[1].toUpperCase();q=null;dest=null;continue;}
   const question=t.match(/^Câu\s+(\d+)\s*[:.]\s*(.*)$/i);
   if(question){
     q={id:uuid(),position:questions.length+1,section,type:({I:'mcq',II:'tf',III:'short',IV:'essay'})[section]||'essay',
       number:parseInt(question[1],10),body:question[2],options:[],statements:[],media:[],points:0,answer:null,grading:{},rubric:'',approved:false,issues:[]};
     questions.push(q);dest={kind:'body'};await attach(line,q);continue;
   }
   if(!q)continue;
   const explicit=t.match(/^Đáp\s*án\s*[:：]\s*(.*)$/i);
   if(explicit){
     if(q.type==='short')q.answer=explicit[1];
     else if(q.type==='mcq'&&/^[A-D]$/i.test(explicit[1]))q.answer=explicit[1].toUpperCase();
     else if(q.type==='tf'){
       const chunks=[...explicit[1].matchAll(/([a-z])\s*=\s*(Đúng|Sai|true|false)/gi)];
       if(chunks.length){q.answer=q.answer||{};for(const m of chunks)q.answer[m[1]]= /^(Đúng|true)$/i.test(m[2]);}
     }
     continue;
   }
   if(/^Lời\s*giải\s*$/i.test(t)){dest={kind:'rubric'};continue;}
   if(/^Quy\s*tắc\s*chấm\s*[:：]/i.test(t)){q.issues.push('Quy tắc chấm trong Word cần xác nhận thủ công: '+t);continue;}
   const opt=t.match(/^([A-D])\s*[.)]\s*(.*)$/);
   if(q.type==='mcq'&&opt){
     const o={id:opt[1],text:opt[2],media:[]};q.options.push(o);
     if(line.red){if(q.answer&&q.answer!==o.id)q.issues.push('Nhiều phương án chữ đỏ, cần đối chiếu lại đáp án.');q.answer=o.id;}
     dest={kind:'option',item:o};
     for(const img of line.images){const ext=(img.path.split('.').pop()||'').toLowerCase();const f=zip.file(img.path);
       if(!shortName(ext)||!f){q.issues.push('Phương án '+o.id+' chứa ảnh '+img.path+' chưa chuyển được; cần bổ sung ảnh gốc.');continue;}
       o.media.push('data:'+shortName(ext)+';base64,'+await f.async('base64'));
     }
     if(line.math)q.issues.push('Công thức Word trong phương án '+o.id+' cần nhập lại chính xác.');
     continue;
   }
   const tf=t.match(/^([a-d])\s*[.)]\s*(.*)$/);
   if(q.type==='tf'&&tf){const st={id:tf[1],text:tf[2],media:[]};q.statements.push(st);
     q.answer=q.answer||{};q.answer[st.id]=Boolean(line.red);dest={kind:'statement',item:st};await attach(line,q);continue;}
   if(!t && !line.images.length && !line.math)continue;
   if(dest?.kind==='option' || dest?.kind==='statement')dest.item.text+='\n'+t;
   else if(dest?.kind==='rubric'&&q.type==='essay')q.rubric+=(q.rubric?'\n':'')+t;
   else q.body+=(q.body?'\n':'')+t;
   await attach(line,q);
 }
 for(const q of questions){
   if(q.type==='mcq' && !q.answer)q.issues.push('Chưa nhận diện được đáp án chữ đỏ.');
   if(q.type==='tf'){
     if(!q.statements.length)q.issues.push('Không nhận diện được các ý Đúng/Sai.');
     q.issues.push('Đáp án Đúng/Sai suy từ chữ đỏ; cần giáo viên kiểm tra từng ý và thiết lập quy tắc chấm.');
   }
   if(q.type==='short' && !q.answer)q.issues.push('Thiếu dòng Đáp án:');
   if(q.type==='essay' && !q.rubric)q.issues.push('Thiếu hướng dẫn chấm tự luận.');
 }
 return {meta:{title:file.name.replace(/\.docx$/i,''),subject:'Hóa học',grade:'',topic:'',source_file:file.name},questions,
     report:{total:questions.length,sections:{I:questions.filter(q=>q.section==='I').length,II:questions.filter(q=>q.section==='II').length,III:questions.filter(q=>q.section==='III').length,IV:questions.filter(q=>q.section==='IV').length},warningCount:questions.reduce((n,q)=>n+q.issues.length,0)}};
}
window.WordReader={readWord};
})();
