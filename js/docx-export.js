/* EduPlan 7.2: standalone DOCX writer. No third party dependency, no API key. */
(function(){
'use strict';
const UTF8 = new TextEncoder();
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const xmlText = s => esc(s).replace(/\r\n|\r|\n/g,'</w:t></w:r><w:r><w:br/></w:r><w:r><w:t xml:space="preserve">');
const P = (s, opts={}) => `<w:p><w:pPr>${opts.keep?'<w:keepNext/>':''}${opts.center?'<w:jc w:val="center"/>':''}<w:spacing w:after="${opts.after||115}"/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>${opts.bold?'<w:b/>':''}<w:sz w:val="${opts.size||22}"/></w:rPr><w:t xml:space="preserve">${xmlText(s)}</w:t></w:r></w:p>`;
const bytes = x => x instanceof Uint8Array ? x : UTF8.encode(x);
const tableCrc = (()=>{const t=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=c&1?(0xedb88320^(c>>>1)):(c>>>1);t[n]=c>>>0;}return t;})();
function crc32(arr){let c=0xffffffff;for(const b of arr)c=tableCrc[(c^b)&255]^(c>>>8);return (c^0xffffffff)>>>0;}
function zip(entries){let total=0;const data=[];const index=[];let offset=0;
 const u16=(view,pos,v)=>view.setUint16(pos,v,true),u32=(view,pos,v)=>view.setUint32(pos,v,true);
 for(const item of entries){const name=bytes(item.name),body=bytes(item.body),crc=crc32(body),loc=new Uint8Array(30+name.length),dv=new DataView(loc.buffer);u32(dv,0,0x04034b50);u16(dv,4,20);u16(dv,6,0x800);u16(dv,8,0);u32(dv,14,crc);u32(dv,18,body.length);u32(dv,22,body.length);u16(dv,26,name.length);loc.set(name,30);data.push(loc,body);
 const ctr=new Uint8Array(46+name.length),cv=new DataView(ctr.buffer);u32(cv,0,0x02014b50);u16(cv,4,20);u16(cv,6,20);u16(cv,8,0x800);u16(cv,10,0);u32(cv,16,crc);u32(cv,20,body.length);u32(cv,24,body.length);u16(cv,28,name.length);u32(cv,42,offset);ctr.set(name,46);index.push(ctr);offset+=loc.length+body.length;total+=ctr.length;
 }
 const tail=new Uint8Array(22),dv=new DataView(tail.buffer);u32(dv,0,0x06054b50);u16(dv,8,entries.length);u16(dv,10,entries.length);u32(dv,12,total);u32(dv,16,offset);
 return new Blob([...data,...index,tail],{type:'application/vnd.openxmlformats-officedocument.wordprocessingml.document'});
}
function imageDrawing(rid,id,wide,high){const EMU=9525;return `<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0"><wp:extent cx="${wide*EMU}" cy="${high*EMU}"/><wp:docPr id="${id}" name="Minh họa ${id}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="${id}" name="Minh họa"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="${rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="${wide*EMU}" cy="${high*EMU}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>`;}
function safeMediaPath(path){return /^assets\/(61|62|64|65|66)\/[a-f0-9]{10,80}\.(png|jpe?g)$/i.test(path||'');}
async function embedMedia(q,assets,rels,ids){let out='';for(const path of (q.media||[]).filter(safeMediaPath).slice(0,6)){
 try{const response=await fetch('./'+path);if(!response.ok)continue;const body=new Uint8Array(await response.arrayBuffer());if(body.length>4e6)continue;const ext=/\.jpe?g$/i.test(path)?'jpeg':'png',name=`word/media/image${++ids.count}.${ext}`,rid=`rId${ids.count+1}`;assets.push({name,body});rels.push(`<Relationship Id="${rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image${ids.count}.${ext}"/>`);out+=imageDrawing(rid,ids.count,440,240);
 }catch(err){console.warn('DOCX image skipped',path,err);}
 }return out;}
function choices(q){return Object.entries(q.options||{}).filter(([k])=>/^[A-D]$/i.test(k)).map(([k,v])=>P(`${k}. ${v}`)).join('');}
async function download(payload){
 const list=(payload.variants||[{code:payload.code||'01',questions:payload.questions||[]}]),rels=[],assets=[],ids={count:0};let content='';
 content+=P('EDUPLAN AI | HÓA HỌC THPT',{bold:true,center:true,size:28,after:160});content+=P(payload.title||'BÀI LUYỆN TẬP',{bold:true,center:true,size:30,after:200});
 content+=P(`Khối: ${payload.grade||'10'} | Chương: ${payload.chapter||'Tong hop'} | Bài: ${payload.lesson||'Theo chuong'}`);
 content+=P(`Họ và tên: ${payload.student||'..........................................'} | Lớp: ${payload.className||'...............'}`);
 content+=P('Nguồn: Ngân hàng EduPlan AI. Tài liệu tự học, không kèm khóa đáp án chưa xác minh.');
 for(const variant of list){if(list.length>1)content+=P(`MÃ ĐỀ: ${variant.code}`,{bold:true,size:26,after:150});
 for(let i=0;i<variant.questions.length;i++){const q=variant.questions[i];content+=P(`Câu ${i+1}. ${q.stem||''}`,{bold:true,keep:true,size:22});content+=choices(q);
 if(q.kind==='tf4'){for(const [k,v] of Object.entries(q.statements||{}))content+=P(`${k}) ${v}  [ ] Đúng  [ ] Sai`);}
 content+=await embedMedia(q,assets,rels,ids);
 if(payload.includeWork){const a=(payload.answers||[]).find(a=>a.id===q.id);content+=P('Bài làm: '+(a?.answer||'Chưa trả lời'));}else content+=P('Bài làm: ............................................................................................');
 content+=P('....................................................................................................................',{after:170});
 }
 }
 if(payload.footer)content+=P(payload.footer);
 const body=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><w:body>${content}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr></w:body></w:document>`;
 const types=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="jpeg" ContentType="image/jpeg"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>`;
 const rootRels=`<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>`;
 const docRels=`<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">${rels.join('')}</Relationships>`;
 const blob=zip([{name:'[Content_Types].xml',body:types},{name:'_rels/.rels',body:rootRels},{name:'word/document.xml',body},{name:'word/_rels/document.xml.rels',body:docRels},...assets]);const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=(payload.filename||'EduPlan_AI_Hoa_Hoc.docx').replace(/[^a-zA-Z0-9_.-]/g,'_');document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);return {size:blob.size,images:assets.length};
}
window.EduPlanDocx={download,zip};
})();
