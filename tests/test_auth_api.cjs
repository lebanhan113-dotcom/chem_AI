const fs=require('fs');const vm=require('vm');const assert=require('assert');
const calls=[];const store={};
const localStorage={getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=v,removeItem:k=>delete store[k]};
store.a4_config=JSON.stringify({url:'https://testproj.supabase.co',key:'sb_publishable_test'});
const win={};
const ctx={window:win,localStorage,Date,JSON,String,Boolean,Number,Error,URLSearchParams,
 location:{protocol:'https:',hostname:'school.vercel.app',origin:'https://school.vercel.app',pathname:'/'},
 history:{replaceState:()=>{}},
 fetch:async (url,opts)=>{
  calls.push({url,opts});
  if(url.includes('/signup'))return {ok:true,status:200,text:async()=>JSON.stringify({user:{id:'123'}})};
  if(url.includes('/recover'))return {ok:true,status:200,text:async()=>JSON.stringify({})};
  if(url.includes('/token'))return {ok:true,status:200,text:async()=>JSON.stringify({access_token:'testtoken',refresh_token:'refresh',expires_in:3600})};
  if(url.includes('/functions'))return {ok:true,status:200,text:async()=>JSON.stringify({role:'pending'})};
  return {ok:false,status:404,text:async()=>JSON.stringify({error:'unknown'})};
 }
};
vm.runInNewContext(fs.readFileSync(__dirname+'/../web/api.js','utf8'),ctx);
(async()=>{
 await win.API.signUp('teacher@school.vn','SuperSecret11!','Cô Vy');
 const req=calls[0];assert(req.url.includes('/auth/v1/signup?redirect_to='));
 assert(req.url.includes(encodeURIComponent('https://school.vercel.app/')));
 assert.strictEqual(JSON.parse(req.opts.body).data.full_name,'Cô Vy');
 await win.API.requestPasswordReset('teacher@school.vn');assert(calls.some(x=>x.url.includes('/auth/v1/recover')));
 await win.API.signIn('teacher@school.vn','SuperSecret11!');assert(win.API.hasSession());
 const status=await win.API.call('auth.status',{},true);assert.strictEqual(status.role,'pending');
 win.API.signOut();assert(!win.API.hasSession());
 console.log('PASS Auth REST signup redirect, recovery, login, pending role, logout');
})().catch(e=>{console.error(e);process.exitCode=1});
