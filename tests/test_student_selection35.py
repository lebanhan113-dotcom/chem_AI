"""Regression checks for student grade/chapter/lesson scope and available question counts."""
import os,tempfile,sys
from pathlib import Path
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mkdtemp()+'/student35.sqlite'
os.environ['SESSION_SECRET']='s'*64
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from fastapi.testclient import TestClient
from server import APP
c=TestClient(APP)
assert c.get('/api/health').json()['version']=='3.5'
meta=c.get('/api/curriculum').json()['grades']
assert [len(meta[str(g)]) for g in (10,11,12)]==[7,6,8]
assert [sum(len(ch['lessons']) for ch in meta[str(g)]) for g in (10,11,12)]==[23,25,30]
valid=c.get('/api/study/availability',params={'grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':'11-4','kind':'mcq'})
assert valid.status_code==200,valid.text
assert valid.json()['available']>0
assert c.get('/api/study/pool',params={'grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':'11-4','kind':'mcq'}).status_code==200
assert c.get('/api/study/availability',params={'grade':10,'chapter':'Nitrogen - Sulfur'}).status_code==422
assert c.get('/api/study/availability',params={'grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':'12-1'}).status_code==422
assert c.get('/api/study/pool',params={'grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':'12-1'}).status_code==422
assert c.get('/api/study/availability',params={'grade':11,'chapter':'all'}).json()['available']==0
assert c.get('/index.html').status_code==200
print('PASS 3.5: 78 lesson curriculum; chapter-to-lesson validation; available counts; index.html.')
