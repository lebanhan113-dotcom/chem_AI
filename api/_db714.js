'use strict';
const {createHash,timingSafeEqual}=require('crypto');
const uri=process.env.SUPABASE_URL||process.env.NEXT_PUBLIC_SUPABASE_URL;
const key=process.env.SUPABASE_SERVICE_ROLE_KEY;
function isReady(){return Boolean(uri&&key);}
function isAdmin(got){const secret=process.env.EDUPLAN_ADMIN_TOKEN||'';if(secret.length<20||typeof got!=='string')return false;const a=Buffer.from(secret),b=Buffer.from(got);return a.length===b.length&&timingSafeEqual(a,b);}
function fingerprint(q){return createHash('sha256').update(String(q.grade)+'|'+String(q.stem||'').toLowerCase().normalize('NFKC').replace(/[\s\p{P}\p{S}]+/gu,'')).digest('hex');}
async function db(path,options={}){if(!isReady())throw Error('Chưa cấu hình cơ sở dữ liệu Supabase trên máy chủ');const url=String(uri).replace(/\/$/,'')+'/rest/v1/'+path;const h={apikey:key,Authorization:'Bearer '+key,Accept:'application/json',...(options.headers||{})};const r=await fetch(url,{...options,headers:h});const body=await r.text();let parsed;try{parsed=JSON.parse(body);}catch{parsed=body;}if(!r.ok)throw Error('Supabase: '+r.status+' '+String(parsed?.message||'Truy vấn thất bại'));return parsed;}
module.exports={isReady,isAdmin,fingerprint,db};
