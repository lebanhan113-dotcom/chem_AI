'use strict';
const {isReady,isAdmin,fingerprint,db}=require('./_db714');
const LETTERS=['A','B','C','D'];
const curriculum=require('../data/curriculum.json');
function validate(x){
 if(!x||!['mcq','tf4','short','essay'].includes(x.kind)||![10,11,12].includes(Number(x.grade))||!Number.isInteger(Number(x.chapter_no))||!Number.isInteger(Number(x.lesson_id)))return 'Lớp / bài / dạng câu không hợp lệ';
 if(!(curriculum[String(x.grade)]||[]).some(ch=>ch.no===Number(x.chapter_no)&&ch.name===x.chapter&&ch.lessons.some(l=>l.no===Number(x.lesson_id)&&l.name===x.lesson)))return 'Chương hoặc bài không có trong danh mục KNTT';
 if(!/^[\w-]{6,100}$/.test(String(x.id||''))||!String(x.stem||'').trim()||String(x.stem).length>12000)return 'Mã câu hoặc nội dung không hợp lệ';
 if(!['NB','TH','VD','VDC'].includes(x.difficulty)||!String(x.explanation||'').trim()||String(x.explanation).length>15000||!String(x.source_title||'').trim())return 'Thiếu mức độ, nguồn hoặc lời giải';
 if(x.confirmed!==true||x.complex_media===true||x.needs_review===true&&x.confirmed!==true)return 'Câu chưa thẩm định hoặc chứa dữ kiện chưa khôi phục';
 if(x.kind==='mcq'&&(!LETTERS.every(a=>typeof x.options?.[a]==='string'&&x.options[a].trim())||!LETTERS.includes(String(x.answer||'').trim().toUpperCase())))return 'Thiếu A–D hoặc khóa';
 if(x.kind==='tf4'&&(!['a','b','c','d'].every(a=>String(x.statements?.[a]||'').trim())||!['a','b','c','d'].every(a=>['D','S'].includes(String(x.answer?.[a]||'').toUpperCase()))))return 'Sai cấu trúc Đúng/Sai bốn ý';
 if(['short','essay'].includes(x.kind)&&!String(x.answer||'').trim())return 'Thiếu đáp án';
 if(JSON.stringify(x).length>45000)return 'Câu quá lớn';return '';
}
module.exports=async function handler(req,res){res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');
 if(req.method!=='POST')return res.status(405).json({error:'POST only'});
 if(!isAdmin(req.headers['x-eduplan-admin']))return res.status(401).json({error:'Không đủ quyền giáo viên quản trị'});
 if(!isReady())return res.status(503).json({error:'Cần cấu hình Supabase ở Vercel'});
 const arr=req.body?.questions;if(!Array.isArray(arr)||arr.length<1||arr.length>100)return res.status(400).json({error:'Chỉ chấp nhận 1–100 câu mỗi lượt'});
 let seen=new Set(),hashes=new Set(),rows=[];
 for(const x of arr){const err=validate(x);if(err)return res.status(400).json({error:x?.id+': '+err});const fp=fingerprint(x);if(seen.has(x.id)||hashes.has(fp))return res.status(400).json({error:'Có câu trùng ngay trong lượt cập nhật'});seen.add(x.id);hashes.add(fp);
 const publicQ={id:x.id,grade:Number(x.grade),chapter_no:Number(x.chapter_no),chapter:x.chapter,lesson_id:Number(x.lesson_id),lesson:x.lesson,part:Number(x.part),kind:x.kind,difficulty:x.difficulty,stem:x.stem,options:x.kind==='mcq'?x.options:{},statements:x.kind==='tf4'?x.statements:{},source_title:x.source_title,source_question_number:x.source_question_number||0,needs_review:false,media:[],reviewed:true};
 rows.push({id:x.id,fingerprint:fp,grade:publicQ.grade,chapter_no:publicQ.chapter_no,lesson_id:publicQ.lesson_id,part:publicQ.part,content:publicQ,answer:x.answer,explanation:x.explanation,source_title:x.source_title,status:'approved'});
 }
 try{const created=await db('eduplan_question_additions?on_conflict=fingerprint',{method:'POST',headers:{'Content-Type':'application/json',Prefer:'resolution=ignore-duplicates,return=representation'},body:JSON.stringify(rows)});return res.status(200).json({inserted:created.length,skipped:rows.length-created.length});}
 catch(err){console.error('bank admin database:',err.message);return res.status(503).json({error:'Không thể lưu câu hỏi. Kiểm tra migration SQL và cấu hình Supabase.'});}
};
module.exports.validate=validate;
