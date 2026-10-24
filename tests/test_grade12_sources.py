"""Document import integrity, 8 chapters, privacy, no fabricated answers."""
from pathlib import Path
import json,collections,tempfile,os,sys
root=Path(__file__).resolve().parents[1]
q=json.loads((root/'data/teacher_docx_import.json').read_text())
assert len(q)==672 and len({x['id'] for x in q})==672
assert collections.Counter(x['grade'] for x in q)=={10:224,11:192,12:256}
for c in range(1,9):
 b=[x for x in q if x['id'].startswith(f'SRC-12-{c:02}-')]
 assert collections.Counter(x['type'] for x in b)=={'mcq':18,'tf':4,'short':6,'essay':4},(c,collections.Counter(x['type'] for x in b))
 assert all(x['stem'] and x['status']=='import-pending' for x in b)
 assert all(len(x['options'])==4 and all(x['options']) for x in b if x['type']=='mcq')
 assert all(len(x['statements'])==4 and all(x['statements']) for x in b if x['type']=='tf')
 if c>=7:
  assert all(not x['has_teacher_solution'] and not x['explanation'] for x in b)
  assert all(x['correct'] is None for x in b if x['type']!='tf')
  assert all(x['correct']==[None]*4 for x in b if x['type']=='tf')
 else:
  assert all(x['has_teacher_solution'] for x in b)
  assert sum(x['correct'] is not None for x in b if x['type']=='mcq')==18
  assert sum(all(type(v) is bool for v in x['correct']) for x in b if x['type']=='tf')==4
 assert len(set(x['source_number'] for x in b))==32
files=list((root/'source_docs').glob('*.docx'));assert len(files)==27
# Import records are not accessible in public and are loaded without overwriting older data.
with tempfile.TemporaryDirectory() as td:
 os.environ['DATABASE_URL']='sqlite:///'+td+'/check.sqlite'
 os.environ['ADMIN_PASSWORD']='test_password_very_secure'
 os.environ['SESSION_SECRET']='z'*64
 sys.path.insert(0,str(root));import server
 from fastapi.testclient import TestClient
 with TestClient(server.APP) as client:
  assert client.get('/api/health').json()['version']=='3.5'
  unauth=client.get('/api/sources/questions/SRC-12-08-1-01');assert unauth.status_code==401
  teacher=client.post('/api/auth/teacher',json={'password':os.environ['ADMIN_PASSWORD']}).json()
  h={'Authorization':'Bearer '+teacher['token']}
  sm=client.get('/api/sources/summary',headers=h).json();assert sm['total']==672 and sm['approved']==0
  g12=client.get('/api/sources/questions',params={'grade':12,'limit':100},headers=h).json();assert g12['total']==256
  ch7=client.get('/api/sources/questions/SRC-12-07-1-01',headers=h).json()['question']
  assert ch7['correct'] is None and not ch7['explanation']
  assert client.post('/api/sources/questions/SRC-12-07-1-01/review',headers=h,json={'approve':True,'confirmed':True}).status_code==422
  assert client.get('/api/sources/documents/'+ch7['source_file']).status_code==401
  assert client.get('/api/sources/documents/'+ch7['source_file'],headers=h).status_code==200
  from sqlalchemy import text
  with server.engine.begin() as conn:
   total=conn.execute(text('SELECT COUNT(*) FROM questions')).scalar()
  assert total==755,total
print('All 3.4 grade12 source tests passed. 672 sources, 256 grade12, 755 initialized rows.')
