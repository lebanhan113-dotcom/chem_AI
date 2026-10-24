"""Extract faithfully from 13 teacher DOCX into review-only bank (never auto-publish)."""
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table
import re, json, collections, unicodedata, sys

BASE=Path(__file__).resolve().parents[1]; APP=BASE; SRC=sorted((BASE/'source_docs').glob('*.docx'))
CHAPTERS={
 'Hoa_10_Chuong_1':(10,1),'Hoa_10_Chuong_2':(10,2),'Hoa_10_Chuong_3':(10,3),'Hoa_10_Chuong_4':(10,4),'Hoa_10_Chuong_5':(10,5),'Hoa10_Chuong_6':(10,6),'Hoa_10_Chuong_7':(10,7),
 'Hoa11_Chuong_1':(11,1),'Hoa11_Chuong_2':(11,2),'Hoa11_Chuong_3':(11,3),'Hoa11_Chuong_4':(11,4),'Hoa11_Chuong_5':(11,5),'Hoa11_Chuong_6':(11,6),
}
C=json.loads((APP/'data/curriculum.json').read_text())['grades']; chapters={(grade,i):x['title'] for grade,ch in C.items() for i,x in enumerate(ch,1)}
P_RE=re.compile(r'^PHẦN\s*(IV|III|II|I)\b',re.I)
Q_RE=re.compile(r'^\s*C[Ââ]U\s*(\d{1,2})\b\s*[:.·|–\-]?\s*',re.I)
ALVL=[('Vận dụng cao','Vận dụng cao'),('VẬN DỤNG CAO','Vận dụng cao'),('Vận dụng tính toán','Vận dụng'),('VẬN DỤNG TÍNH TOÁN','Vận dụng'),('Thông hiểu','Thông hiểu'),('THÔNG HIỂU','Thông hiểu'),('Nhận biết','Nhận biết'),('NHẬN BIẾT','Nhận biết')]
SOLUTION_RE=re.compile(r'(?i)(HƯỚNG DẪN GIẢI|LỜI GIẢI|PHÂN TÍCH LỖI SAI|→\s*(ĐÁP ÁN|KẾT QUẢ)|^ĐÁP ÁN\b|^\s*[①②③④⑤⑥]\s*)')
META_RE=re.compile(r'(?i)^(?:DẠNG\b|MỨC ĐỘ\b|LƯU Ý\b|PHÂN LOẠI\b|^\[(NHẬN BIẾT|THÔNG HIỂU|VẬN DỤNG))')
OPT_RE=re.compile(r'^\s*([A-D])\s*[.\):]\s*(.+)\s*$',re.I)
OPT_INLINE=re.compile(r'(?<!\S)([A-D])\s*[.\):]\s*(?=\S)')
STMT_RE=re.compile(r'^\s*([a-d])\s*[).:]\s*(.+)\s*$',re.I)

# Option text can live in one line, in table cells, or across multiple paragraphs.
def elements(doc):
 result=[]
 for node in doc.element.body.iterchildren():
  if node.tag==qn('w:p'):
   p=Paragraph(node,doc);s=p.text.strip()
   if s:result.append(dict(text=s, table=False, has_visual=bool(node.xpath('.//w:drawing|.//w:pict|.//m:oMath'))))
  elif node.tag==qn('w:tbl'):
   tb=Table(node,doc)
   for r in tb.rows:
    seen=[]
    for cell in r.cells:
     val=cell.text.strip().replace('\n','\n')
     if val and (not seen or val!=seen[-1]):seen.append(val)
    if seen:result.append(dict(text='  ||  '.join(seen),table=True,has_visual=False))
 return result

def parse_mcq(items):
 # detect A/B/C/D from one paragraph or table cell (including inline row)
 candidates=[]
 for item in items:
  s=item['text']
  if item['table']:
   for seg in re.split(r'\s*\|\|\s*',s):
    m=OPT_RE.match(seg)
    if m:candidates.append((m.group(1).upper(),m.group(2).strip()))
   continue
  matches=list(OPT_INLINE.finditer(s))
  if len(matches)>=2:
   for i,n in enumerate(matches):
    val=s[n.end():matches[i+1].start() if i+1<len(matches) else len(s)].strip()
    if val:candidates.append((n.group(1).upper(),val))
  else:
   m=OPT_RE.match(s)
   if m:candidates.append((m.group(1).upper(),m.group(2).strip()))
 opts={}
 for code,val in candidates:
  if code not in opts:opts[code]=val
 return [opts.get(x,'') for x in 'ABCD'],candidates

def label_answer(s):
 m=re.search(r'(?i)(?:→\s*)?(?:ĐÁP ÁN|CHỌN|KẾT QUẢ)(?:\s*/\s*KẾT QUẢ)?\s*[:：]?\s*([ABCD])\b',s)
 if m:return 'ABCD'.index(m.group(1).upper())
 m=re.search(r'(?i)→\s*([ABCD])\s*[.。]?\s*$',s)
 return 'ABCD'.index(m.group(1).upper()) if m else None

def parse_tf(items):
 opts={}; flags={}; just={}
 for item in items:
  s=item['text']
  matches=list(re.finditer(r'(?<!\S)([a-d])\s*[).:]\s*(?=\S)',s,re.I))
  if matches:
   for i,mi in enumerate(matches):
    val=s[mi.end():matches[i+1].start() if i+1<len(matches) else len(s)].strip()
    if val and mi.group(1).lower() not in opts:opts[mi.group(1).lower()]=val
  else:
   m=STMT_RE.match(s)
   if m and m.group(1).lower() not in opts:opts[m.group(1).lower()]=m.group(2)
  mo=re.match(r'(?i)^\s*([a-d])\)\s*(ĐÚNG|SAI|Đ|S)\b\s*[:.\-]?\s*(.*)',s)
  if mo:flags[mo.group(1).lower()]=mo.group(2).upper().startswith('Đ');just[mo.group(1).lower()]=mo.group(3).strip()
 # parse compact answers with a)Đ b)S etc
 alltext=' '.join(x['text'] for x in items)
 for letter,ans in re.findall(r'(?i)([a-d])\)\s*(ĐÚNG|SAI|Đ|S)\b',alltext):
  flags[letter.lower()]=ans.upper().startswith('Đ')
 return [opts.get(x,'') for x in 'abcd'],[flags.get(x) for x in 'abcd'],[just.get(x,'') for x in 'abcd']

def answer_short(items):
 ss=[x['text'] for x in items]
 for s in ss:
  for m in [re.search(r'(?i)^\s*(?:→\s*)?(?:ĐÁP ÁN|KẾT QUẢ|ĐÁP SỐ)\s*(?:/\s*KẾT QUẢ)?\s*[:：]\s*(.+)',s),re.search(r'(?i)→\s*(?:x\s*=\s*)?([\-−+]?\d[\d ,.\u00a0]*)\s*(?:\S{0,12})?$',s)]:
   if m:return m.group(1).strip()
 return None

def clean_stem(raw,typ):
 # Remove color/difficulty markers; preserve actual content and all line/table rows.
 out=[]
 for x in raw:
  s=x['text'].strip()
  if s.lower().startswith(('dạng:','mức độ:','phân loại:')):continue
  s=re.sub(r'^\[(Nhận biết|Thông hiểu|Vận dụng(?: cao)?(?: tính toán)?)\]\s*','',s,flags=re.I)
  if typ=='mcq':
   if len(list(OPT_INLINE.finditer(s)))>=2:continue
   if OPT_RE.match(s):continue
   if x['table'] and re.search(r'(?:^|\|\|)\s*[A-D][.)]\s*',s):
    # preserve data tables where cells aren't options
    if len(re.findall(r'\b[A-D][.)]\s*',s))>=1:continue
   if len(list(OPT_INLINE.finditer(s)))>=2:continue
  if typ=='tf' and (STMT_RE.match(s) or len(list(re.finditer(r'(?<!\S)[a-d]\s*[).:]\s*(?=\S)',s,re.I)))>=2):continue
  out.append(s)
 return '\n'.join(out).strip()

def question_split(allblocks,grade,chapter_no):
 part=0;parts={1:[],2:[],3:[],4:[]};cur=None;tail_start=False
 for block in allblocks:
  s=block['text']
  m=P_RE.match(s)
  if m:
   part={'I':1,'II':2,'III':3,'IV':4}[m.group(1).upper()]
   cur=None
   continue
  if not part:continue
  m=Q_RE.match(s) if not block['table'] else None
  if m:
   num=int(m.group(1))
   # Some files repeat "Câu" in answer appendix; only first set of expected questions.
   if num in range(1,[None,19,5,7,5][part]) and not any(x['number']==num for x in parts[part]):
    cur={'number':num,'section':part,'blocks':[dict(block, text=s[m.end():].strip())]};parts[part].append(cur)
   else:cur=None
  elif cur is not None:
   cur['blocks'].append(block)
 return parts

def build():
 allq=[];stats=[]
 for filepath in SRC:
  grade,chapter_no=next((v for p,v in CHAPTERS.items() if filepath.name.startswith(p)),(0,0))
  if not grade:raise RuntimeError('unmapped '+filepath.name)
  doc=Document(filepath)
  parts=question_split(elements(doc),grade,chapter_no)
  if [len(parts[t]) for t in (1,2,3,4)]!=[18,4,6,4]:raise RuntimeError((filepath.name,{k:len(v) for k,v in parts.items()}))
  issues=collections.Counter()
  for section,questions in parts.items():
   typ={1:'mcq',2:'tf',3:'short',4:'essay'}[section]
   for entry in questions:
    bs=entry['blocks']
    # locate first solution; a few docs only include answer without solution
    si=next((i for i,x in enumerate(bs) if SOLUTION_RE.search(x['text'])),len(bs))
    prompt=bs[:si];rest=bs[si:]
    raw_solution='\n'.join(x['text'] for x in rest).strip()
    original=clean_stem(prompt,typ)
    lvl='Thông hiểu'
    t='\n'.join(x['text'] for x in bs[:min(len(bs),8)])
    for a,b in ALVL:
     if a.lower() in t.lower():lvl=b;break
    original=re.sub(r'^\s*\[(?:Nhận biết|Thông hiểu|Vận dụng(?: cao)?(?: tính toán)?)\]\s*','',original,flags=re.I)
    original=re.sub(r'^\s*[·|:]\s*','',original)
    id=f'SRC-{grade}-{chapter_no:02d}-{section}-{entry["number"]:02d}'
    q={'id':id,'grade':grade,'chapter':chapters[(str(grade),chapter_no)],'lesson_id':None,'type':typ,'level':lvl,'stem':original,'explanation':raw_solution[:22000], 'source':f'Tài liệu giáo viên do người dùng cung cấp: {filepath.name} — Phần {"I"*section if section<4 else "IV"}, Câu {entry["number"]}', 'source_file':filepath.name,'source_section':section,'source_number':entry['number'],'status':'import-pending','review_notes':[],'skill':chapters[(str(grade),chapter_no)]}
    if any(x['has_visual'] for x in bs):q['review_notes'].append('Có công thức OMML/hình ảnh: đối chiếu DOCX gốc, vì phần văn bản có thể thiếu dữ kiện.')
    if not original or len(original)<7:q['review_notes'].append('Nội dung câu hỏi ngắn/bị thiếu; kiểm tra bản gốc.')
    if typ=='mcq':
     q['options'],raw_opts=parse_mcq(prompt)
     ans=next((label_answer(x['text']) for x in rest if label_answer(x['text']) is not None),None)
     q['correct']=ans
     if any(not s.strip() for s in q['options']):q['review_notes'].append('Không tách đủ bốn phương án A–D; phải hiệu đính trước khi duyệt.')
     if ans is None:q['review_notes'].append('Chưa nhận dạng chắc chắn được đáp án A–D từ lời giải.')
     q['distractors']={}
     for i,letter in enumerate('ABCD'):
      if i==ans:continue
      rx=re.compile(r'(?i)(?:\(?'+letter+r'\)?\s*[:.)]|chọn\s+(?:nhầm\s+)?'+letter+r'\b)')
      lines=[x['text'] for x in rest if rx.search(x['text']) and 'ĐÁP ÁN' not in x['text'].upper()]
      if lines:q['distractors'][str(i)]={'code':'K01','hypothesis':lines[0][:1100]}
    elif typ=='tf':
     q['statements'],q['correct'],q['statementExplanations']=parse_tf(bs)
     if any(not x for x in q['statements']):q['review_notes'].append('Thiếu ít nhất một trong 4 mệnh đề a–d.')
     if any(v is None for v in q['correct']):q['review_notes'].append('Thiếu đáp án Đúng/Sai xác định cho một hoặc nhiều ý.')
    elif typ=='short':
     raw=answer_short(rest)
     q['correct_text']=raw
     # numeric only when exactly a single machine-readable result, else require manual review
     number=re.fullmatch(r'\s*(?:[A-Za-z]\s*=\s*)?([+-]?\d+(?:[.,]\d+)?)\s*[.,]?\s*',raw or '')
     if number:q['correct']=float(number.group(1).replace(',','.'));q['tolerance']=0.001
     else:q['correct']=None;q['review_notes'].append('Trả lời ngắn chứa đơn vị/nhiều ý/mã số hoặc biểu thức: giáo viên duyệt chế độ chấm trước khi dùng online.')
    else:q['correct']=None;q['rubric']=raw_solution[:1500] or 'Giáo viên chấm tự luận.'
    if len(q['explanation'])<16:q['review_notes'].append('Không trích được lời giải đủ dài; kiểm tra nguồn.')
    if not q['review_notes']:q['review_notes'].append('Đã trích xuất đủ cấu trúc văn bản; cần giáo viên thẩm định nội dung Hóa học trước khi phê duyệt.')
    for p in q['review_notes']:issues[p.split(':')[0]]+=1
    allq.append(q)
  stats.append({'file':filepath.name,'grade':grade,'chapter':chapter_no,'counts':{k:len(v) for k,v in parts.items()},'issues':dict(issues)})
 outfile=APP/'data/teacher_docx_import.json'
 outfile.write_text(json.dumps(allq,ensure_ascii=False,indent=2),encoding='utf-8')
 (APP/'data/teacher_import_audit.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
 print('Total records:',len(allq),collections.Counter(q['type'] for q in allq))
 for grade in (10,11):
  for c in range(1,8 if grade==10 else 7):
   these=[q for q in allq if q['grade']==grade and q['chapter']==chapters[(str(grade),c)]]
   issues=sum(1 for q in these if any('Thiếu' in s or 'Không' in s or 'Chưa' in s or 'Có công thức' in s or 'Trả lời ngắn chứa' in s for s in q['review_notes']))
   print(grade,c,len(these),'review flags',issues,'MCQ valid',sum(q['type']=='mcq' and q['correct'] is not None and len([o for o in q['options'] if o])==4 for q in these),'TF valid',sum(q['type']=='tf' and all(x is not None for x in q['correct']) and all(q['statements']) for q in these))
 return allq
if __name__=='__main__':build()
