(function(){'use strict';
const K='a4_config';
// Public project settings can be published with Vercel to let every student device connect.
// Local settings override the published values on a teacher's browser.
const published=(window.EDU_PUBLIC_CONFIG&&typeof window.EDU_PUBLIC_CONFIG==='object')?window.EDU_PUBLIC_CONFIG:{};
const saved=JSON.parse(localStorage.getItem(K)||'{}');
let cfg={url:String(saved.url||published.url||'').trim().replace(/\/$/,''),key:String(saved.key||published.key||'').trim()},tokens=JSON.parse(localStorage.getItem('a4_teacher_tokens')||'null');
const setConfig=x=>{cfg={url:String(x.url||'').trim().replace(/\/$/,''),key:String(x.key||'').trim()};localStorage.setItem(K,JSON.stringify(cfg));};
const configured=()=>Boolean(cfg.url&&cfg.key);
const getConfig=()=>({...cfg});
async function json(url,init){const res=await fetch(url,init);const raw=await res.text();let out={};try{out=JSON.parse(raw)}catch{throw Error('Máy chủ không trả về JSON hợp lệ')};if(!res.ok||out.error)throw Error(out.error||out.msg||('HTTP '+res.status));return out;}
async function signIn(email,password){if(!configured())throw Error('Cần thiết lập URL và publishable/anon key của Supabase');
 const out=await json(cfg.url+'/auth/v1/token?grant_type=password',{method:'POST',headers:{'Content-Type':'application/json',apikey:cfg.key},body:JSON.stringify({email,password})});
 saveAuthTokens(out);return out;
}

function publicSiteUrl(){
 if(location.protocol!=='https:' && !['localhost','127.0.0.1'].includes(location.hostname))throw Error('Đăng ký và đặt lại mật khẩu cần website HTTPS đã triển khai trên Vercel');
 return location.origin + location.pathname;
}
async function signUp(email,password,name){
 if(!configured())throw Error('Cần kết nối Supabase trước khi đăng ký');
 if(!/^\S+@\S+\.\S+$/.test(email))throw Error('Email không hợp lệ');
 if(String(password).length<10)throw Error('Mật khẩu phải có ít nhất 10 ký tự');
 const url=cfg.url+'/auth/v1/signup?redirect_to='+encodeURIComponent(publicSiteUrl());
 const out=await json(url,{method:'POST',headers:{'Content-Type':'application/json',apikey:cfg.key},body:JSON.stringify({email:email.trim().toLowerCase(),password,data:{full_name:String(name||'').trim().slice(0,120)}})});
 // In case Confirm Email is disabled, a session might be returned. Roles remain
 // pending unless this exact email was previously invited by an administrator.
 if(out.access_token&&out.refresh_token)saveAuthTokens(out);
 return out;
}
function saveAuthTokens(out){
 tokens={access:out.access_token,refresh:out.refresh_token,expires:Date.now()+Number(out.expires_in||3600)*1000};
 localStorage.setItem('a4_teacher_tokens',JSON.stringify(tokens));
}
async function requestPasswordReset(email){
 if(!configured())throw Error('Cần kết nối Supabase');
 await json(cfg.url+'/auth/v1/recover?redirect_to='+encodeURIComponent(publicSiteUrl()),{method:'POST',headers:{'Content-Type':'application/json',apikey:cfg.key},body:JSON.stringify({email:String(email||'').trim()})});
 return {ok:true};
}
function consumeAuthRedirect(){
 const fragment=location.hash.replace(/^#/,'');
 if(!fragment.includes('access_token='))return null;
 const h=new URLSearchParams(fragment);
 const access=h.get('access_token'),refreshToken=h.get('refresh_token');
 if(!access||!refreshToken)return null;
 saveAuthTokens({access_token:access,refresh_token:refreshToken,expires_in:Number(h.get('expires_in')||3600)});
 const type=h.get('type')||'signup';
 history.replaceState({},'',location.pathname+location.search);
 return type;
}
async function changePassword(password){
 if(!tokens?.access)throw Error('Cần mở liên kết đặt lại mật khẩu trong email');
 if(String(password||'').length<10)throw Error('Mật khẩu mới phải có ít nhất 10 ký tự');
 return json(cfg.url+'/auth/v1/user',{method:'PUT',headers:{'Content-Type':'application/json',apikey:cfg.key,Authorization:'Bearer '+tokens.access},body:JSON.stringify({password})});
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
window.API={setConfig,getConfig,configured,signIn,signUp,requestPasswordReset,consumeAuthRedirect,changePassword,signOut,call,hasSession:()=>Boolean(tokens?.access)};
})();
