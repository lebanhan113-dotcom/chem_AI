'use strict';
const {isReady,db}=require('./_db714');
module.exports=async function handler(req,res){res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');if(req.method!=='GET')return res.status(405).json({error:'GET only'});
 if(!isReady())return res.status(200).json({questions:[],enabled:false});
 const offset=Math.max(0,Math.min(200000,parseInt(req.query?.offset||0,10)||0));const limit=200;
 try{const rows=await db('eduplan_question_additions?select=content&status=eq.approved&order=created_at.asc,id.asc&limit='+limit+'&offset='+offset);
 return res.status(200).json({questions:rows.map(x=>x.content),offset,limit,hasMore:rows.length===limit,enabled:true});}
 catch(err){console.error('bank public database:',err.message);return res.status(503).json({error:'Chưa thể tải câu hỏi đồng bộ'});}
};
