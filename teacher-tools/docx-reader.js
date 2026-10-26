/* Small, dependency-free DOCX text importer. Extracts Word paragraphs from ZIP;
   MathType, equations, drawings and tables are flagged for human review. */
(function(global){'use strict';
const txt=new TextDecoder('utf-8');
function u16(v,p){return v.getUint16(p,true);}function u32(v,p){return v.getUint32(p,true);}
async function xmlFromDocx(buffer){
 const data=new Uint8Array(buffer),v=new DataView(buffer);let eocd=-1;
 for(let p=data.length-22;p>=Math.max(0,data.length-65558);p--)if(u32(v,p)===0x06054b50){eocd=p;break;}
 if(eocd<0)throw Error('Tệp DOCX không phải ZIP hợp lệ');
 let count=u16(v,eocd+10),p=u32(v,eocd+16);
 for(let i=0;i<count;i++){
  if(u32(v,p)!==0x02014b50)throw Error('Bảng ZIP không hợp lệ');
  const method=u16(v,p+10),size=u32(v,p+20),namelen=u16(v,p+28),extra=u16(v,p+30),comment=u16(v,p+32),offset=u32(v,p+42);
  const name=txt.decode(data.subarray(p+46,p+46+namelen));p+=46+namelen+extra+comment;
  if(name!=='word/document.xml')continue;
  if(u32(v,offset)!==0x04034b50)throw Error('ZIP local header không hợp lệ');
  const start=offset+30+u16(v,offset+26)+u16(v,offset+28),slice=data.subarray(start,start+size);
  if(method===0)return txt.decode(slice);
  if(method!==8||typeof DecompressionStream==='undefined')throw Error('Trình duyệt chưa hỗ trợ giải nén DOCX');
  const bytes=await new Response(new Blob([slice]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer();
  return txt.decode(new Uint8Array(bytes));
 }
 throw Error('Không tìm thấy word/document.xml');
}
async function read(file){if(file.size>18*1024*1024)throw Error('DOCX vượt giới hạn 18 MB');const xml=await xmlFromDocx(await file.arrayBuffer());
 const dom=new DOMParser().parseFromString(xml,'application/xml');if(dom.querySelector('parsererror'))throw Error('XML trong DOCX không hợp lệ');
 const paragraphs=Array.from(dom.getElementsByTagNameNS('*','p')).map(n=>{
  const chunks=Array.from(n.getElementsByTagNameNS('*','t')).map(t=>t.textContent||'').join('');
  const flags=['oMath','object','drawing','pict'].filter(tag=>n.getElementsByTagNameNS('*',tag).length>0);
  return {text:chunks.trim(),flags};
 }).filter(p=>p.text||p.flags.length);
 return {paragraphs,originalName:file.name};
}
global.EduPlanDocxReader={read};
})(window);
