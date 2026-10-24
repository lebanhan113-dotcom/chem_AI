"""Source import and review authorization / four-part exam tests."""
import sys, os, json, tempfile, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
with tempfile.TemporaryDirectory() as td:
 os.environ['DATABASE_URL']='sqlite:///'+td+'/test.sqlite'
 os.environ['ADMIN_PASSWORD']='testTeacherPassword_2026'
 os.environ['SESSION_SECRET']='c'*64
 import server
 c=TestClient(server.APP)
 login=c.post('/api/auth/teacher',json={'password':os.environ['ADMIN_PASSWORD']}).json()
 h={'Authorization':'Bearer '+login['token']}
 s=c.get('/api/sources/summary',headers=h);assert s.status_code==200,s.text
 filename='Hoa_10_Chuong_1_Cau_tao_nguyen_tu_GIAO_VIEN_loi_giai_bay.docx'
 assert c.get('/api/sources/documents/'+filename).status_code==401
 assert c.get('/api/sources/documents/'+filename,headers=h).status_code==200
 summary=s.json();assert summary['total']==672 and summary['approved']==0 and summary['pending']==672,summary
 assert c.get('/api/sources/summary').status_code==401
 m=c.get('/api/sources/questions',params={'grade':10,'limit':100},headers=h).json();assert m['total']==224
 n=c.get('/api/sources/questions',params={'grade':11,'limit':100},headers=h).json();assert n['total']==192
 z=c.get('/api/sources/questions',params={'grade':12,'limit':100},headers=h).json();assert z['total']==256
 grade7=c.get('/api/sources/questions/SRC-12-07-1-01',headers=h).json()['question']
 assert grade7['correct'] is None and grade7['source_kind']=='student-only'
 assert not grade7['explanation']
 assert c.post('/api/sources/questions/SRC-12-07-1-01/review',headers=h,json={'approve':True,'confirmed':True}).status_code==422
 # Both grade 12 student and teacher DOCXs are private and accessible to authenticated teachers only.
 grade1=c.get('/api/sources/questions/SRC-12-01-1-01',headers=h).json()['question']
 assert grade1['correct']==1 and len(grade1['options'])==4
 assert c.get('/api/sources/documents/'+grade1['student_source_file'],headers=h).status_code==200
 assert c.get('/api/sources/documents/'+grade1['student_source_file']).status_code==401
 # Import stays hidden from students and not counted as available for exams.
 sc=c.get('/api/questions/counts',params={'grade':10,'chapter':'Cấu tạo nguyên tử'}).json()
 assert sc['total']<32,sc
 r=c.post('/api/exams/build',json={'grade':10,'chapter':'Cấu tạo nguyên tử'},headers=h);assert r.status_code==409,r.text
 example=c.get('/api/sources/questions/SRC-10-01-1-01',headers=h).json();q=example['question'];assert q['correct'] is not None and len(q['options'])==4
 # Generic review may not circumvent attestation.
 assert c.post('/api/questions/'+q['id']+'/approve',headers=h).status_code==403
 assert c.post('/api/sources/questions/'+q['id']+'/review',headers=h,json={'approve':True,'confirmed':False}).status_code==422
 ok=c.post('/api/sources/questions/'+q['id']+'/review',headers=h,json={'approve':True,'confirmed':True});assert ok.status_code==200,ok.text
 assert c.get('/api/questions/counts',params={'grade':10,'chapter':'Cấu tạo nguyên tử'}).json()['total']==sc['total']+1
 # Existing source records are not overwritten on re-run; /tests migrate DB is idempotent.
 from sqlalchemy import text
 with server.engine.begin() as con:
  con.execute(text("UPDATE questions SET status='approved' WHERE id=:i"),{'i':q['id']})
 # Approve remaining source questions for one chapter, simulating teacher verification only for the test.
 for sec, nmax in ((1,18),(2,4),(3,6),(4,4)):
  for i in range(1,nmax+1):
   id=f'SRC-10-01-{sec}-{i:02d}'
   detail=c.get('/api/sources/questions/'+id,headers=h).json()
   changes={}
   if sec==3 and detail['question'].get('correct') is None:
    # Valid numeric answer must be independently set by a teacher. In this test, cannot auto-approve.
    assert c.post('/api/sources/questions/'+id+'/review',headers=h,json={'approve':True,'confirmed':True}).status_code==422
    continue
   if detail['question']['status']=='approved':continue
   approve=c.post('/api/sources/questions/'+id+'/review',headers=h,json={'approve':True,'confirmed':True,'updates':changes})
   assert approve.status_code==200,(id,approve.text)
 r=c.post('/api/exams/build',json={'grade':10,'chapter':'Cấu tạo nguyên tử','title':'TEST Form 2025 source'},headers=h)
 assert r.status_code==200,r.text
 assert r.json()['count']==32
 print('Source tests passed: 672 imports, 32-question form after verified publication, access control.')
