const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const handler=require('../api/grade.js');
const catalog=require('../data/gradable_catalog.json');
function resp(){return {statusCode:200,headers:{},setHeader(k,v){this.headers[k]=v;},status(c){this.statusCode=c;return this;},json(d){this.data=d;return this;}}}
async function call(method,qs){const r=resp();await handler({method,body:{questions:qs}},r);return r;}
(async()=>{
 assert.equal(catalog.count,377);
 const known=catalog.ids[0];
 const unlisted='UNVERIFIED_00001';
 const info=await call('POST',[{id:known,answer:'D'},{id:unlisted,answer:'A'}]);
 assert.equal(info.statusCode,200);assert.equal(info.data.results.length,2);
 assert.equal(info.data.checked,1);assert.equal(info.data.results[1].status,'unverified');
 const good=await call('POST',[{id:known,answer:info.data.results[0].correctAnswer}]);
 assert.equal(good.data.correct,1);assert.equal(good.data.checked,1);
 const dup=await call('POST',[{id:known,answer:'A'},{id:known,answer:'B'}]);assert.equal(dup.statusCode,400);
 const large=await call('POST',Array.from({length:51},(_,i)=>({id:'x'+i,answer:'B'})));assert.equal(large.statusCode,400);
 const get=await call('GET',[{id:known,answer:'B'}]);assert.equal(get.statusCode,405);
 const empty=await call('POST',[]);assert.equal(empty.statusCode,400);
 console.log('API: 7/7 checks passed; vetted catalog:',catalog.count);
})().catch(err=>{console.error(err);process.exit(1)});
