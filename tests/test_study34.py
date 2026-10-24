"""Student-first self-practice, access protection, lesson classification and progress."""
from pathlib import Path
import os,tempfile,sys,json,collections
from fastapi.testclient import TestClient
root=Path(__file__).resolve().parents[1]
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mkdtemp()+'/study34.sqlite'
os.environ['ADMIN_PASSWORD']='strong_teach_password'
os.environ['SESSION_SECRET']='s'*64
sys.path.insert(0,str(root));from server import APP
source=json.loads((root/'data/teacher_docx_import.json').read_text())
assert len(source)==672
mapped=[x for x in source if x['lesson_id']]
assert len(mapped)==422,len(mapped)
curr=json.loads((root/'data/curriculum.json').read_text())['grades']
assert [sum(len(ch['lessons']) for ch in curr[g]) for g in ('10','11','12')]==[23,25,30]
with TestClient(APP) as client:
 assert client.get('/').status_code==200
 assert client.get('/index.html').status_code==200
 assert client.get('/api/health').json()['version']=='3.5'
 for grade,n in ((10,7),(11,6),(12,8)):
  resp=client.get('/api/study/catalog',params={'grade':grade}).json()
  assert len(resp['chapters'])==n
 assert sum(ch['waiting'] for gr in (10,11,12) for ch in client.get('/api/study/catalog',params={'grade':gr}).json()['chapters'])==672
 # Guest access: available demo questions only, don't reveal answers.
 pool=client.get('/api/study/pool',params={'grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':'11-4','kind':'mcq','limit':10}).json()
 assert pool['questions'] and pool['total_available']>0,pool
 q=pool['questions'][0]
 assert 'correct' not in q and 'explanation' not in q and 'distractors' not in q
 # Repeated review request never makes a pending source public.
 assert client.post('/api/study/check',json={'id':'SRC-12-07-1-01','answer':0}).status_code==404
 # A learner sees a detailed explanation once they answer.
 checked=client.post('/api/study/check',json={'id':q['id'],'answer':0}).json()
 assert checked['correct'] in (True,False) and checked['explanation'] and not checked['saved']
 # Cannot access other lesson label as though it belonged to chapter.
 assert client.get('/api/study/pool',params={'grade':10,'chapter':'Cấu tạo nguyên tử','lesson_id':'12-24'}).status_code==422
 # Registered student gets persistent evidence of practice.
 token=client.post('/api/auth/teacher',json={'password':os.environ['ADMIN_PASSWORD']}).json()['token']
 th={'Authorization':'Bearer '+token}
 c=client.post('/api/classes',headers=th,json={'name':'11A1','grade':11}).json()
 st=client.post('/api/auth/join',json={'code':c['code'],'name':'Học sinh A','pin':'supersecret'}).json()
 sh={'Authorization':'Bearer '+st['token']}
 first=client.post('/api/study/check',headers=sh,json={'id':q['id'],'answer':0}).json()
 assert first['saved']
 progress=client.get('/api/study/progress',headers=sh).json()
 assert progress['total_attempts']==1 and progress['by_topic'][0]['lesson_id']=='11-4'
 assert client.get('/api/study/progress').status_code==401
 # Review status remains unchanged by automatic tagging.
 row=client.get('/api/sources/questions/SRC-12-07-1-01',headers=th).json()['question']
 assert row['status']=='import-pending'
 wrong=client.post('/api/sources/questions/SRC-12-07-1-01/review',headers=th,json={'updates':{'lesson_id':'11-2'},'confirmed':False,'approve':False})
 assert wrong.status_code==422
print('Student study 3.4 tests OK; classified',len(mapped),'source questions to suggested lesson categories.')
