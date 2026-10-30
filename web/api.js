(function(){'use strict';
const K='a4_config';
let cfg=JSON.parse(localStorage.getItem(K)||'{}'),tokens=JSON.parse(localStorage.getItem('a4_teacher_tokens')||'null');
const setConfig=x=>{cfg={url:String(x.url||'').trim().replace(/\/$/,''),key:String(x.key||'').trim()};localStorage.setItem(K,JSON.stringify(cfg));};
const configured=()=>Boolean(cfg.url&&cfg.key);
const getConfig=()=>({...cfg});
async function json(url,init){const res=await fetch(url,init);const raw=await res.text();let out={};try{out=JSON.parse(raw)}catch{throw Error('Máy chủ không trả về JSON hợp lệ')};if(!res.ok||out.error)throw Error(out.error||out.msg||('HTTP '+res.status));return out;}
async function signIn(email,password){if(!configured())throw Error('Cần thiết lập URL và publishable/anon key của Supabase');
 const out=await json(cfg.url+'/auth/v1/token?grant_type=password',{method:'POST',headers:{'Content-Type':'application/json',apikey:cfg.key},body:JSON.stringify({email,password})});
 tokens={access:out.access_token,refresh:out.refresh_token,expires:Date.now()+Number(out.expires_in||3600)*1000};localStorage.setItem('a4_teacher_tokens',JSON.stringify(tokens));return out;
}
async function refresh(){if(!tokens?.refresh)throw Error('Giáo viên chưa đăng nhập');
 const out=await json(cfg.url+'/auth/v1/token?grant_type=refresh_token',{method:'POST',headers:{'Content-Type':'application/json',apikey:cfg.key},body:JSON.stringify({refresh_token:tokens.refresh})});
 tokens={access:out.access_token,refresh:out.refresh_token,expires:Date.now()+Number(out.expires_in||3600)*1000};localStorage.setItem('a4_teacher_tokens',JSON.stringify(tokens));
}
function signOut(){tokens=null;localStorage.removeItem('a4_teacher_tokens');}
async function call(action,data={},auth=false){if(!configured())throw Error('Chưa cấu hình kết nối Supabase');
 if(auth && (!tokens||!tokens.access))throw Error('Hãy đăng nhập giáo viên');
 if(auth&&Date.now()>tokens.expires-45000)await refresh();
 const headers={'Content-Type':'application/json',apikey:cfg.key};if(auth)headers.Authorization='Bearer '+tokens.access;
 return json(cfg.url+'/functions/v1/exam-api',{method:'POST',headers,body:JSON.stringify({action,data})});
}
window.API={setConfig,getConfig,configured,signIn,signOut,call,hasSession:()=>Boolean(tokens?.access)};
})();
