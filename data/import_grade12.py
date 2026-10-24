"""Add grade 12 source questions from uploaded grade 12 student and teacher docs.
Student copies are authoritative for question stems; teacher docs supply draft answers/explanations.
Everything remains pending verification by teachers. Never fabricate absent answers.
"""
from pathlib import Path
from docx import Document
import sys,re,json,csv,collections,hashlib,unicodedata,difflib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'data'))
from import_teacher_docs import elements, parse_mcq, parse_tf, label_answer, answer_short, clean_stem, OPT_RE,OPT_INLINE,SOLUTION_RE,ALVL
SOURCE=ROOT/'source_docs'; DATA=ROOT/'data'
CUR=json.loads((DATA/'curriculum.json').read_text())['grades']['12']
CHAPTERS={i:CUR[i-1]['title'] for i in range(1,9)}
TFILES={i:next(SOURCE.glob('Hoa_12_Chuong_'+str(i)+'_*.docx'),None) for i in range(1,7)}
SFILES={i:next(SOURCE.glob('2025 - 2026. 12.'+str(i)+' *.docx'),None) for i in range(1,9)}
# Consecutively numbered 1..32 regardless of part; no assumption of reset.
P_RE=re.compile(r'^PHẦN\s+(IV|III|II|I)\b',re.I)
Q_RE=re.compile(r'^\s*C[Ââ]U\s*(\d{1,2})\b\s*[:.·|–\-]?\s*',re.I)
EXPECTED={1:(1,18),2:(19,22),3:(23,28),4:(29,32)}
TYPES={1:'mcq',2:'tf',3:'short',4:'essay'}

def parse_doc(path,teacher=False):
 blocks=elements(Document(path)); part=None; parts={1:{},2:{},3:{},4:{}};cur=None
 for b in blocks:
  s=b['text'].strip()
  m=P_RE.match(s)
  if m:
   part={'I':1,'II':2,'III':3,'IV':4}[m.group(1).upper()];cur=None;continue
  if part is None:continue
  m=Q_RE.match(s) if not b['table'] else None
  if m:
   number=int(m.group(1));low,high=EXPECTED[part]
   if not low<=number<=high:
    # Adjacent repeated "CÂU N" captions in teacher docs are supported.
    cur=None;continue
   if number in parts[part]:
    if teacher and cur is parts[part][number]:
     cur.append(dict(b,text=s[m.end():].strip()))
    else:cur=None
   else:
    cur=[dict(b,text=s[m.end():].strip())];parts[part][number]=cur
  elif cur is not None:cur.append(b)
 for p in range(1,5):
  low,high=EXPECTED[p]
  missing=[i for i in range(low,high+1) if i not in parts[p]]
  if missing:raise ValueError(f'{path.name} part {p} missing {missing}; found {list(parts[p])}')
 return parts

def split_teacher_prompt(blocks):
 i=next((i for i,b in enumerate(blocks) if SOLUTION_RE.search(b['text'])),len(blocks))
 return blocks[:i],blocks[i:]

def short_numeric(raw):
 if not raw:return None
 m=re.fullmatch(r'\s*(?:[A-Za-z]\s*=\s*)?([+-]?\d+(?:[.,]\d+)?)\s*[.,]?\s*',raw)
 return float(m.group(1).replace(',','.')) if m else None

def get_level(blocks):
 txt='\n'.join(b['text'] for b in blocks[:min(len(blocks),5)])
 for a,b in ALVL:
  if a.lower() in txt.lower():return b
 return 'Thông hiểu'

def strip_quiz_meta(text):
 lines=[]
 for t in text.splitlines():
  st=t.strip()
  if not st:continue
  if re.match(r'^(?:CHỦ ĐỀ\b|BÀI\s+\d+\b|DẠNG\s*[:：]|MỨC ĐỘ\s*[:：]|\[(?:NHẬN BIẾT|THÔNG HIỂU|VẬN DỤNG)|(?:NHẬN BIẾT|THÔNG HIỂU|VẬN DỤNG(?: CAO)?(?: TÍNH TOÁN)?)\s*$)',st,re.I):continue
  lines.append(st)
 return '\n'.join(lines)

def parse_student(blocks,typ):
 # A-C may be inline with options on same line. import_teacher_docs.clean_stem handles most.
 stem=strip_quiz_meta(clean_stem(blocks,typ))
 if typ=='tf':
  # Some student DOCX put the question and a)-d) in a single multiline paragraph.
  first_text=blocks[0]['text'] if blocks else ''
  before=re.split(r'(?m)^\s*a\)\s*',first_text,maxsplit=1)[0].strip()
  if before and (not stem or len(stem)<len(before)/2):stem=strip_quiz_meta(before)
 if typ=='mcq':
  opts,_=parse_mcq(blocks)
  return stem,opts,None
 if typ=='tf':
  stmts,_,_=parse_tf(blocks)
  return stem,stmts,None
 return stem,None,None

def read_teacher(blocks,typ):
 if not blocks:return {'explanation':'','correct':None,'correct_text':None,'rubric':None,'source_stem':''}
 prom,rest=split_teacher_prompt(blocks)
 sol='\n'.join(x['text'] for x in rest).strip()
 teacher_stem=clean_stem(prom,typ)
 if typ=='mcq':
  ans=next((label_answer(x['text']) for x in rest if label_answer(x['text']) is not None),None)
  return {'explanation':sol[:22000],'correct':ans,'source_stem':teacher_stem}
 if typ=='tf':
  _o,flags,just=parse_tf(rest)
  # Some teacher solutions show answers together in a table at top or under an intro.
  return {'explanation':sol[:22000],'correct':flags if len(flags)==4 else [None]*4,'statement_explanations':just,'source_stem':teacher_stem}
 if typ=='short':
  raw=answer_short(rest)
  return {'explanation':sol[:22000],'correct':short_numeric(raw),'correct_text':raw,'source_stem':teacher_stem}
 return {'explanation':sol[:22000],'correct':None,'rubric':sol[:1500] if sol else '', 'source_stem':teacher_stem}

def run():
 old=[q for q in json.loads((DATA/'teacher_docx_import.json').read_text()) if q['grade']!=12]
 assert len(old)==416,len(old)
 new=[];stats=[];manifest=[]
 for ch in range(1,9):
  sf=SFILES[ch];tf=TFILES.get(ch)
  sp=parse_doc(sf);tp=parse_doc(tf,teacher=True) if tf else {k:{} for k in range(1,5)}
  mcnt=collections.Counter();issues=collections.Counter();similarities=[]
  for sec,(low,high) in EXPECTED.items():
   typ=TYPES[sec]
   for num in range(low,high+1):
    raw=sp[sec][num]
    stem,choices,_=parse_student(raw,typ)
    tinfo=read_teacher(tp[sec].get(num),typ)
    notes=['Bắt buộc giáo viên đối chiếu nguồn, số liệu, phương trình và đáp án trước khi công bố.']
    if not tf:notes.append('CHƯA CÓ TÀI LIỆU GIÁO VIÊN/ĐÁP ÁN: chưa được phép tự chấm hoặc công bố đề; giáo viên phải bổ sung lời giải và đáp án.')
    if any(x['has_visual'] for x in raw):notes.append('Câu có thành phần hình/công thức nhúng: kiểm tra lại trực tiếp bản DOCX học sinh.')
    if len(stem)<8:notes.append('Nội dung câu hỏi quá ngắn hoặc chưa trích xuất đủ.')
    # The student file determines the stem; teacher source must be audited if materially different.
    teacher_stem=tinfo.get('source_stem') or ''
    if teacher_stem:
     a=re.sub(r'\s+',' ',stem).lower();b=re.sub(r'\s+',' ',teacher_stem).lower()
     ratio=difflib.SequenceMatcher(None,a[:1300],b[:1300]).ratio()
     similarities.append(round(ratio,3))
     if ratio<0.50:notes.append(f'Bản giáo viên và học sinh có khác biệt đáng kể (độ tương đồng văn bản {ratio:.2f}); cần đối chiếu trước khi sử dụng đáp án.')
    q={
     'id':f'SRC-12-{ch:02d}-{sec}-{num-low+1:02d}',
     'grade':12,'chapter':CHAPTERS[ch],'lesson_id':None,'type':typ,'level':get_level(raw),
     'stem':stem,'explanation':tinfo.get('explanation') or '',
     'source':f'Tệp học sinh: {sf.name}; '+(f'Tệp giáo viên: {tf.name}.' if tf else 'Chưa có đáp án giáo viên.' )+f' Phần {"I"*sec if sec<4 else "IV"} câu {num}.',
     'source_file':tf.name if tf else sf.name,'student_source_file':sf.name,
     'source_section':sec,'source_number':num,'status':'import-pending','review_notes':notes,
     'skill':CHAPTERS[ch], 'has_teacher_solution':bool(tf), 'source_kind':'teacher-and-student' if tf else 'student-only'
    }
    if typ=='mcq':
     q['options']=choices
     q['correct']=tinfo['correct']
     if any(not p.strip() for p in choices):notes.append('Thiếu ít nhất một phương án A–D ở bản trích xuất.')
     if q['correct'] is None:notes.append('Chưa xác định đáp án A–D; giáo viên phải nhập và xác thực.')
     q['distractors']={}
    elif typ=='tf':
     q['statements']=choices;q['correct']=tinfo['correct'] if tf else [None]*4
     q['statementExplanations']=tinfo.get('statement_explanations') or ['']*4
     if any(not s for s in choices):notes.append('Thiếu ít nhất một mệnh đề đúng/sai a–d trong trích xuất.')
     if any(v is None for v in q['correct']):notes.append('Chưa đầy đủ đáp án đúng/sai 4 ý; giáo viên phải nhập.')
    elif typ=='short':
     q['correct']=tinfo['correct'];q['correct_text']=tinfo.get('correct_text')
     if q['correct'] is not None:q['tolerance']=0.001
     else:notes.append('Chưa có đáp án dạng một số để chấm máy. Giáo viên cần nhập kết quả và dung sai, hoặc chấm thủ công.')
    else:
     q['correct']=None;q['rubric']=tinfo.get('rubric') or ''
     if not q['rubric']:notes.append('Chưa có hướng dẫn chấm tự luận; giáo viên cần biên soạn rubric.')
    for n in notes:issues[n.split(':')[0]]+=1
    mcnt[typ]+=1
    new.append(q)
  assert dict(mcnt)=={'mcq':18,'tf':4,'short':6,'essay':4},(ch,mcnt)
  stats.append({'grade':12,'chapter':ch,'name':CHAPTERS[ch], 'teacher_file':tf.name if tf else None,'student_file':sf.name,'new_unique_questions':32,'types':dict(mcnt),'text_similarity_mean':round(sum(similarities)/len(similarities),3) if similarities else None, 'needs_manual_review':dict(issues)})
  manifest.append({'chapter':ch,'student_sha256':hashlib.sha256(sf.read_bytes()).hexdigest(),'teacher_sha256':hashlib.sha256(tf.read_bytes()).hexdigest() if tf else None})
 merged=old+new
 if len(set(q['id'] for q in merged))!=len(merged):raise ValueError('duplicate IDs')
 (DATA/'teacher_docx_import.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2))
 (DATA/'grade12_import_audit.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
 (DATA/'grade12_source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 with open(DATA/'grade12_import_index.csv','w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['id','lớp','chương','phần','câu nguồn','loại','mức độ','có lời giải GV','đáp án chấm tự động','số ghi chú','tệp GV','tệp HS','nội dung câu hỏi'])
  for q in new:w.writerow([q['id'],12,q['chapter'],q['source_section'],q['source_number'],q['type'],q['level'],q['has_teacher_solution'],q.get('correct'),len(q['review_notes']),q['source_file'] if q['has_teacher_solution'] else '',q['student_source_file'],q['stem'].replace('\n',' ')])
 print('MERGED',len(merged),'NEW',len(new),'COUNTS',collections.Counter(q['type'] for q in new))
 for row in stats:print('Chapter',row['chapter'],'teacher',bool(row['teacher_file']),'mean text sim',row['text_similarity_mean'])
 for ch in range(1,9):
  b=[q for q in new if q['grade']==12 and q['id'].startswith('SRC-12-'+str(ch).zfill(2))]
  print(ch,'MCQ4',sum(q['type']=='mcq' and len(q['options'])==4 and all(q['options']) for q in b),'mcq answers',sum(q['type']=='mcq' and q['correct'] is not None for q in b),'TF full',sum(q['type']=='tf' and all(q['statements']) for q in b),'TF ans',sum(q['type']=='tf' and all(x is not None for x in q['correct']) for q in b),'short numeric',sum(q['type']=='short' and q['correct'] is not None for q in b))
 return new
if __name__=='__main__':run()
