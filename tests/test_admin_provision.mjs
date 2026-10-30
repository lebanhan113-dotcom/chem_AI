import assert from 'node:assert/strict';
import {provisionAdmin,ADMIN_EMAIL} from '../setup/admin-provision.mjs';
const uid='123e4567-e89b-12d3-a456-426614174000';
const key='sb_secret_TEST_ONLY';
const password='TestPassOnly#12345';
const mkRes=(body,status=200)=>({ok:status>=200&&status<300,status,json:async()=>body});
function makeFake(existing,confirmed=true){
 let calls=[];
 const fetcher=async(url,opts={})=>{
  calls.push({url,opts});
  if(url.includes('/admin/users?'))return mkRes({users:existing?[{id:uid,email:ADMIN_EMAIL,email_confirmed_at:confirmed?'2026-01-01':null}]:[]});
  if(url.endsWith('/admin/users')&&opts.method==='POST')return mkRes({id:uid,email:ADMIN_EMAIL});
  if(url.includes('/admin/users/')&&opts.method==='PUT')return mkRes({id:uid,email:ADMIN_EMAIL});
  if(url.includes('/app_profiles'))return mkRes([{id:uid,role:'admin'}],201);
  throw Error('Unexpected request: '+url);
 };
 return {fetcher,calls};
}
{
 const x=makeFake(false);const result=await provisionAdmin({url:'https://a123.supabase.co',secretKey:key,password,fetcher:x.fetcher});
 assert.equal(result.created,true);assert.equal(result.email,ADMIN_EMAIL);
 assert.equal(x.calls.length,3);
 assert.equal(JSON.parse(x.calls[1].opts.body).email_confirm,true);
 assert.equal(JSON.parse(x.calls[1].opts.body).password,password);
 assert(!Object.values(x.calls[2].opts.headers).some(s=>String(s).startsWith('Bearer sb_secret_')));
 assert.equal(JSON.parse(x.calls[2].opts.body).role,'admin');
}
{
 const x=makeFake(true);const result=await provisionAdmin({url:'https://a123.supabase.co',secretKey:key,password,fetcher:x.fetcher});
 assert.equal(result.created,false);assert.equal(x.calls.length,2);
 assert(!x.calls.some(c=>c.opts.method==='PUT'));
}
{
 const x=makeFake(true);const result=await provisionAdmin({url:'https://a123.supabase.co',secretKey:key,password,resetExisting:true,fetcher:x.fetcher});
 assert.equal(result.reset,true);assert.equal(x.calls.length,3);
 assert(x.calls.some(c=>c.opts.method==='PUT'));
}
{
 const x=makeFake(true,false);
 await assert.rejects(()=>provisionAdmin({url:'https://a123.supabase.co',secretKey:key,password,fetcher:x.fetcher}),/chua duoc xac minh/);
 assert.equal(x.calls.length,1);
}
{
 const x=makeFake(false);
 await assert.rejects(()=>provisionAdmin({url:'http://a123.supabase.co',secretKey:key,password,fetcher:x.fetcher}),/URL https/);
 await assert.rejects(()=>provisionAdmin({url:'https://a123.supabase.co',secretKey:'sb_publishable_TEST',password,fetcher:x.fetcher}),/secret key/);
}
console.log('PASS: create, existing, reset, unverified, configuration validation');
