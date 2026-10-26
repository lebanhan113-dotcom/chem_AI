'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f)));const q=[10,11,12].flatMap(g=>read('data/hoa'+g+'.json'));const ids=read('data/gradable_catalog.json').ids;
assert.equal(q.length,322);assert.equal(new Set(q.map(x=>x.id)).size,322);assert.deepEqual(new Set(ids),new Set(q.map(x=>x.id)));console.log('PASS 322 câu nguồn cũ giữ nguyên');
for(const f of ['teacher-tools/docx-reader.js','teacher-tools/import.js','teacher-tools/index.html','api/admin-bank.js','api/public-bank.js','api/_db714.js','sql/supabase_question_additions.sql','js/bank-update714.js'])assert(fs.existsSync(path.join(root,f)));
const doc=fs.readFileSync(path.join(root,'index.html'),'utf8');assert(doc.includes('bank-update714.js'));assert(doc.includes('teacher-tools')===false);console.log('PASS Bộ cập nhật được tách khỏi dữ liệu công khai');
const validate=require('../api/admin-bank').validate;const ch=read('data/curriculum.json')['10'][0];const sample={id:'IMP-10-1-1-q4567',grade:10,chapter_no:1,chapter:ch.name,lesson_id:ch.lessons[0].no,lesson:ch.lessons[0].name,kind:'mcq',part:1,difficulty:'TH',stem:'Một câu hỏi ví dụ để kiểm thử chức năng cập nhật',options:{A:'A1',B:'B1',C:'C1',D:'D1'},answer:'B',explanation:'Đã đối chiếu nguồn trong môi trường thử.',source_title:'test.docx',confirmed:true};
assert.equal(validate(sample),'');assert(validate({...sample,confirmed:false}));assert(validate({...sample,options:{A:'1'}}));assert(validate({...sample,chapter:'Sai chương'}));assert(validate({...sample,complex_media:true}));console.log('PASS 5/5 tình huống kiểm soát kiểm duyệt');
const publicApi=require('../api/public-bank');const adminApi=require('../api/admin-bank');
function response(){return {statusCode:200,headers:{},setHeader(k,v){this.headers[k]=v;return this;},status(n){this.statusCode=n;return this;},json(x){this.payload=x;return this;}};}
(async()=>{
 let res=response();await adminApi({method:'POST',headers:{},body:{questions:[sample]}},res);assert.equal(res.statusCode,401);
 res=response();await publicApi({method:'GET',query:{}},res);assert.equal(res.statusCode,200);assert.deepEqual(res.payload.questions,[]);
 res=response();await adminApi({method:'GET',headers:{}},res);assert.equal(res.statusCode,405);
 console.log('PASS 3/3 tình huống API không cấu hình, bảo vệ quyền');
 const apiFile=fs.readFileSync(path.join(root,'api/grade.js'),'utf8');assert(!fs.readFileSync(path.join(root,'js/bank-update714.js'),'utf8').includes('SUPABASE_SERVICE_ROLE_KEY'));
 assert(apiFile.includes('dynamicKeys'));assert(apiFile.includes('teacher_review'));console.log('PASS Dịch vụ chấm và tải câu bổ sung chỉ ở máy chủ');
 console.log('RESULT EduPlan 7.14: checks passed');
})().catch(e=>{console.error(e);process.exitCode=1;});
