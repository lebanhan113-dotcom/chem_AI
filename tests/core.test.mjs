import test from 'node:test';import assert from 'node:assert/strict';
import {hashPassword,verifyPassword,makeSession,readSession,publicQuestion,checkQuestion,gradeExam} from '../lib/core.js';

test('mật khẩu và phiên giáo viên dùng băm và chữ ký',()=>{const h=hashPassword('a-private-password!');assert(!h.includes('a-private-password!'));assert.equal(verifyPassword('a-private-password!',h),true);assert.equal(verifyPassword('wrong',h),false);const t=makeSession({email:'teacher@example.com',role:'teacher'},'test-secret-value');assert.equal(readSession(t,'test-secret-value').role,'teacher');assert.equal(readSession(t,'wrong'),null)});
test('API học sinh không chứa đáp án hoặc rubric',()=>{const q={id:'q1',type:'mcq',position:1,section:'I',body:'kiểm thử',options:[{id:'A',text:'a'},{id:'B',text:'b'}],answer:'B',rubric:'bí mật',points:1,approved:true};const s=JSON.stringify(publicQuestion(q));assert(!s.includes('"answer"'));assert(!s.includes('rubric'));assert.equal(checkQuestion(q).length,0)});
test('Chấm bốn dạng câu và giữ trạng thái tự luận chờ chấm',()=>{const q=[
 {id:'1',type:'mcq',points:1,answer:'A'},
 {id:'2',type:'tf',points:1,statements:[{id:'a'},{id:'b'}],answer:{a:true,b:false},grading:{mode:'per_statement'}},
 {id:'3',type:'short',points:1,answer:'20',grading:{}},
 {id:'4',type:'essay',points:2,rubric:'chấm tay'}
 ];const a={1:'A',2:{a:true,b:false},3:'20',4:'Cách giải của học sinh'};const g=gradeExam(q,a);assert.equal(g.score,3);assert.equal(g.status,'pending_essay');assert.equal(g.pending,1);const h=gradeExam(q,a,{4:1.5});assert.equal(h.score,4.5);assert.equal(h.status,'official')});
test('Dừng phát hành câu thiếu thông tin',()=>{const issues=checkQuestion({id:'1',type:'mcq',body:'',points:0,options:[],answer:null,issues:['Ảnh WMF chưa xử lý'],approved:false});assert(issues.length>=4)});
