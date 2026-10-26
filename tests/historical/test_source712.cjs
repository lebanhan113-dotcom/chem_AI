'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const j=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8'));
const pub=[10,11,12].flatMap(g=>j(`data/hoa${g}.json`));
const src=j('data/source712_catalog.json'),catalog=j('data/gradable_catalog.json'),qa=j('data/quality_audit.json'),manifest=j('data/public_manifest.json'),gap=j('data/question_gap_report.json');
const newq=pub.filter(q=>q.id.startsWith('NEW26-10-'));
assert.equal(src.chapters.length,7);
assert.equal(src.chapters.reduce((v,x)=>v+x.imported,0),145);
assert.equal(newq.length,42);
assert.equal(pub.length,217);
assert.equal(new Set(pub.map(q=>q.id)).size,217);
assert.equal(catalog.count,217);
assert.equal(new Set(catalog.ids).size,217);
assert.equal(qa.total,217);
assert.equal(Object.keys(qa.questions).length,217);
assert.equal(manifest.bankTotal,217);
assert.equal(gap.published,217);
assert.equal(gap.lessons.length,78);
const lessons=j('data/curriculum.json');
for(const q of newq){
 assert.equal(q.grade,10);
 assert.equal(q.part,1);
 assert.equal(q.kind,'mcq');
 assert.deepEqual(Object.keys(q.options).sort(),['A','B','C','D']);
 assert(q.stem.length>20&&!q.needs_review);
 assert(!Object.hasOwn(q,'answer'));
 assert(!Object.hasOwn(q,'correctAnswer'));
 assert(lessons['10'].some(c=>c.name===q.chapter&&c.lessons.some(l=>l.name===q.lesson)));
 assert(catalog.ids.includes(q.id));
}
for(const c of src.chapters){assert.equal(c.imported,c.pending+c.public);assert.equal(Object.values(c.parts).reduce((a,b)=>a+b,0),c.imported)}
const api=fs.readFileSync(path.join(root,'api/grade.js'),'utf8');
const keys=JSON.parse(api.match(/const KEYS=(\{.*?\});\nfunction norm/s)[1]);
assert.deepEqual(new Set(Object.keys(keys)),new Set(pub.map(q=>q.id)));
assert.equal(keys['NEW26-10-C4-P1-Q08'].key,'D');
assert(!fs.existsSync(path.join(root,'data/sources_pending_full.json')));
console.log('PASS EduPlan 7.12: 217 published, 42 new, 145 staged in separate archive, 7 sources, verified key whitelist');
