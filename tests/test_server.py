import os, sys, tempfile, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
TMP=tempfile.TemporaryDirectory()
os.environ['DATABASE_URL']='sqlite:///'+TMP.name+'/test.sqlite'
os.environ['ADMIN_PASSWORD']='testTeacherPassword_2026'
os.environ['SESSION_SECRET']='a'*64
from fastapi.testclient import TestClient
from server import APP
client=TestClient(APP)

def as_user(token):return {'Authorization':'Bearer '+token}
def test_core_end_to_end():
 r=client.get('/api/health');assert r.status_code==200
 c=client.get('/api/curriculum').json()['grades'];assert [(g,len(c[g]),sum(len(x['lessons']) for x in c[g])) for g in ['10','11','12']]==[('10',7,23),('11',6,25),('12',8,30)]
 teacher=client.post('/api/auth/teacher',json={'password':'testTeacherPassword_2026'}).json()['token']
 assert teacher
 cl=client.post('/api/classes',json={'name':'11A1 TEST','grade':11},headers=as_user(teacher)).json();assert cl['code']
 stu=client.post('/api/auth/join',json={'code':cl['code'],'name':'HS 01','pin':'987654'}).json()
 st=stu['token']
 assert client.post('/api/auth/join',json={'code':cl['code'],'name':'HS 01','pin':'badpin'}).status_code==401
 q=client.get('/api/questions/counts',params={'grade':11,'chapter':'Nitrogen - Sulfur'}).json();print('counts',q)
 assert all(q['by_type'].get(t,0)>=n for t,n in [('mcq',18),('tf',4),('short',6),('essay',4)])
 no=client.post('/api/exams/build',headers=as_user(teacher),json={'grade':10,'chapter':'Liên kết hóa học','lesson_id':'10-12','mcq':18,'tf':4,'short':6,'essay':4});assert no.status_code==409
 build=client.post('/api/exams/build',headers=as_user(teacher),json={'grade':11,'chapter':'Nitrogen - Sulfur','title':'Kiểm tra test'});assert build.status_code==200,build.text
 exam=client.get('/api/exams/'+build.json()['id'],headers=as_user(st)).json(); assert len(exam['questions'])==32
 assert not any('correct' in question or 'explanation' in question for question in exam['questions'])
 answers={}
 bank=json.loads((ROOT/'data/questions.json').read_text());index={x['id']:x for x in bank}
 for question in exam['questions']:
  row=index[question['id']]
  if row['type']=='mcq':answers[row['id']]=row['correct']
  elif row['type']=='tf':answers[row['id']]=row['correct']
  elif row['type']=='short':answers[row['id']]=row['correct']
  elif row['type']=='essay':answers[row['id']]='Bài làm cần kiểm chứng.'
 res=client.post('/api/exams/'+exam['id']+'/submit',json={'answers':answers},headers=as_user(st));assert res.status_code==200,res.text
 a=res.json();assert a['graded'] is False and a['score']>8
 assert client.post('/api/exams/'+exam['id']+'/submit',json={'answers':answers},headers=as_user(st)).status_code==409
 essay_ids=[x['id'] for x in a['results'] if x['type']=='essay'];grade=client.post('/api/attempts/'+a['id']+'/grade',json={'points':{i:1 for i in essay_ids}},headers=as_user(teacher));assert grade.status_code==200,grade.text
 assert grade.json()['score']==10 and grade.json()['graded']
 stats=client.get('/api/analytics',headers=as_user(teacher)).json();assert stats['attempts']==1 and stats['distinct_participants']==1
 assert client.get('/api/analytics',headers=as_user(st)).status_code==403
 sheets=client.post('/api/worksheets',headers=as_user(teacher),json={'grade':11,'chapter':'Nitrogen - Sulfur','title':'Jigsaw Nitrogen - Sulfur','kind':'Jigsaw 6 nhóm · 45 phút'});assert sheets.status_code==200
 sheet_id=sheets.json()['id']
 teacher_doc=client.get('/api/worksheets/'+sheet_id+'/docx?mode=teacher',headers=as_user(teacher));assert teacher_doc.status_code==200 and len(teacher_doc.content)>1000
 student_doc=client.get('/api/worksheets/'+sheet_id+'/docx?mode=student',headers=as_user(st));assert student_doc.status_code==200
 assert student_doc.content!=teacher_doc.content
 assert client.get('/api/worksheets/'+sheet_id+'/docx?mode=teacher',headers=as_user(st)).status_code==403
 from docx import Document
 import io
 text_student=' '.join(p.text for p in Document(io.BytesIO(student_doc.content)).paragraphs)
 assert 'Đáp án:' not in text_student
 assert 'Hướng dẫn giải' not in text_student
 print('All end-to-end checks passed. Score',grade.json()['score'],'DOCX',len(student_doc.content),len(teacher_doc.content))

def test_online_library_fallback():
 refs=client.get('/api/references').json();assert len(refs)>=10
 d=client.get('/api/references/search',params={'q':''});assert d.status_code==200

if __name__=='__main__':
 test_core_end_to_end();test_online_library_fallback()
