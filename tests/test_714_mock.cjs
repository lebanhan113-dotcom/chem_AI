'use strict';
const assert=require('node:assert/strict');
process.env.SUPABASE_URL='https://mock.supabase.local';process.env.SUPABASE_SERVICE_ROLE_KEY='service-role-for-testing';process.env.EDUPLAN_ADMIN_TOKEN='this-is-a-test-admin-token-very-long';
const admin=require('../api/admin-bank'),pub=require('../api/public-bank'),grade=require('../api/grade');
const c=require('../data/curriculum.json')['10'][0];const q={id:'IMP-10-1-1-sample',grade:10,chapter_no:1,chapter:c.name,lesson_id:c.lessons[0].no,lesson:c.lessons[0].name,kind:'mcq',part:1,difficulty:'NB',stem:'Số electron trong nguyên tử hydrogen trung hòa (Z = 1) là bao nhiêu?',options:{A:'1',B:'2',C:'3',D:'0'},answer:'A',explanation:'Nguyên tử trung hòa: số e = Z = 1.',source_title:'teacher_test.docx',confirmed:true,complex_media:false};
let db=[];global.fetch=async (url,opt={})=>{
 let value=[];if(opt.method==='POST'){const rows=JSON.parse(opt.body);const inserted=rows.filter(x=>!db.some(y=>y.id===x.id||y.fingerprint===x.fingerprint));db.push(...inserted);value=inserted;}else if(String(url).includes('select=content'))value=db.map(x=>({content:x.content}));else if(String(url).includes('select=id,answer'))value=db.map(x=>({id:x.id,answer:x.answer,explanation:x.explanation,content:x.content}));
 return {ok:true,status:200,text:async()=>JSON.stringify(value)};
};
function res(){return {statusCode:200,headers:{},setHeader(k,v){this.headers[k]=v;return this;},status(n){this.statusCode=n;return this;},json(x){this.data=x;return this;}};}
(async()=>{
 let r=res();await admin({method:'POST',headers:{'x-eduplan-admin':process.env.EDUPLAN_ADMIN_TOKEN},body:{questions:[q]}},r);assert.equal(r.statusCode,200);assert.equal(r.data.inserted,1);
 r=res();await admin({method:'POST',headers:{'x-eduplan-admin':process.env.EDUPLAN_ADMIN_TOKEN},body:{questions:[q]}},r);assert.equal(r.data.skipped,1);
 r=res();await pub({method:'GET',query:{offset:0}},r);assert.equal(r.data.questions.length,1);assert.equal(r.data.questions[0].id,q.id);assert(!Object.hasOwn(r.data.questions[0],'answer'));
 r=res();await grade({method:'POST',body:{questions:[{id:q.id,answer:'B'}]}},r);assert.equal(r.data.results[0].correct,false);assert.equal(r.data.results[0].correctAnswer,'A');
 r=res();await grade({method:'POST',body:{questions:[{id:q.id,answer:'A'}]}},r);assert.equal(r.data.results[0].correct,true);
 console.log('PASS 5/5 mocked online cases: publish, duplicate, public secrecy, grading incorrect/correct');
})().catch(e=>{console.error(e);process.exitCode=1;});
