import re,os,json,hashlib,base64,io,csv,shutil,unicodedata,collections
from pathlib import Path
from bs4 import BeautifulSoup,Tag,NavigableString
from PIL import Image
ROOT=Path(__file__).resolve().parent;HTML=ROOT/'tmp_html'; APP=ROOT; MEDIA=ROOT/'media';MEDIA.mkdir(parents=True,exist_ok=True)
SOURCES={
'Hoa_12_Pin_dien_va_dien_phan_Dung_Sai_GV':(12,5,'Pin điện và điện phân'),
'2025-2026_12.6_Dai_cuong_ve_kim_loai_Cau_hoi_Dung_Sai_DA_SUA':(12,6,'Đại cương về kim loại'),
'Hoa_12_Chuong_7_Nhom_IA_IIA_Cau_hoi_Dung_Sai':(12,7,'Nguyên tố nhóm IA và IIA'),
'Chuong_8_Kim_loai_chuyen_tiep_va_phuc_chat_Cau_hoi_Dung_Sai_HS':(12,8,'Sơ lược về dãy kim loại chuyển tiếp thứ nhất và phức chất')}
LESSONS={
5:{15:'Thế điện cực và nguồn điện hóa học',16:'Điện phân',17:'Ôn tập chương 5'},
6:{18:'Cấu tạo và liên kết trong tinh thể kim loại',19:'Tính chất vật lí và tính chất hóa học của kim loại',20:'Kim loại trong tự nhiên và phương pháp tách kim loại',21:'Hợp kim',22:'Sự ăn mòn kim loại',23:'Ôn tập chương 6'},
7:{24:'Nguyên tố nhóm IA',25:'Nguyên tố nhóm IIA',26:'Ôn tập chương 7'},
8:{27:'Đại cương về kim loại chuyển tiếp dãy thứ nhất',28:'Sơ lược về phức chất',29:'Một số tính chất và ứng dụng của phức chất',30:'Ôn tập chương 8'}}
# Các số bài và tên bài chương 5-8 đã đối chiếu mục lục SGK KNTT 12.
CHAPT={k:v[2] for k,v in SOURCES.items()}
SRCQ=re.compile(r'^Câu\s*(\d{1,3})\s*[.:(]?\s*(.*)',re.I|re.S)
OPT=re.compile(r'^\s*([abcd])\s*\)\s*(.*)',re.I|re.S)
SECT=re.compile(r'^(CHUYÊN ĐỀ\b|PHẦN\s+[IVX0-9ABCD]+\b|ÔN TẬP CHƯƠNG|ĐỀ KIỂM TRA TỔNG HỢP|CÂU HỎI TRONG ĐỀ KIỂM TRA)',re.I)
space=re.compile(r'\s+')
def plain(h):return space.sub(' ',BeautifulSoup(h or '','html.parser').get_text(' ',strip=True)).strip()
def norm(h):return space.sub(' ',unicodedata.normalize('NFKC',plain(h)).lower()).strip()
def sig(q):return hashlib.sha256('|'.join(norm(s) for s in q.get('statements',[])).encode()).hexdigest()
def image_data(src):
 if src.startswith('data:'):
  try:
   raw=base64.b64decode(src.split(',',1)[1]);im=Image.open(io.BytesIO(raw));im.load()
   if im.width<3 or im.height<3:return None
   data=io.BytesIO();im.convert('RGB').save(data,format='PNG');return data.getvalue()
  except Exception:return None
 p=HTML/src
 if p.exists():
  try:
   im=Image.open(p);im.verify();return p.read_bytes()
  except:pass
 return None
def clean_element(el,stem):
 s=BeautifulSoup(str(el),'html.parser');missing=False;figures=0
 for e in list(s.find_all(True)):
  if e.name in ['script','style','iframe','object','embed']:
   e.decompose();continue
  if e.name=='img':
   raw=image_data(e.get('src',''))
   if raw:
    nm='e718_'+hashlib.sha256(raw).hexdigest()[:16]+'.png';out=MEDIA/nm
    if not out.exists():out.write_bytes(raw)
    e.attrs={'src':'/media/'+nm,'loading':'lazy','alt':'Hình hoặc công thức trong nguồn Word'}
    figures+=1
   else:
    e.replace_with('[Hình hoặc công thức nhúng Word cần kiểm tra nguồn]');missing=True
  elif e.name in ('span','font'):
   typ=str(e.get('style','')).lower();e.name='sup' if 'super' in typ else 'sub' if 'sub' in typ else 'span';e.attrs={}
  elif e.name not in ['b','strong','em','i','u','sup','sub','br','p','div','table','tbody','thead','tr','th','td','h1','h2']:
   e.unwrap()
  else:e.attrs={}
 return str(s),missing,figures
def prefix_remove(html,pat):
 s=BeautifulSoup(html,'html.parser');rx=re.compile(pat,re.I|re.S)
 for d in s.descendants:
  if isinstance(d,NavigableString) and d.strip():
   m=rx.match(str(d))
   if m:d.replace_with(str(d)[m.end():]);break
 return str(s)
def lesson_by_chapter(ch,sec,stem=''):
 sec=sec.upper();ctx=(sec+' '+stem).upper()
 if ch==5:
  if 'ÔN TẬP' in sec or 'ĐỀ KIỂM TRA' in sec:return 17
  return 16 if 'ĐIỆN PHÂN' in sec else 15
 if ch==6:
  if 'ÔN TẬP' in sec:return 23
  if 'TÁCH KIM LOẠI' in sec or 'TÁI CHẾ' in ctx:return 20
  if 'HỢP KIM' in stem.upper() and 'ĂN MÒN' not in stem.upper():return 21
  if 'ĂN MÒN' in stem.upper() or 'ĂN MÒN' in sec and 'HỢP KIM' not in stem.upper():return 22
  if any(k in stem.upper() for k in ('CẤU TẠO','TINH THỂ','LIÊN KẾT KIM LOẠI','NGUYÊN TỬ KIM LOẠI')):return 18
  if 'TÍNH CHẤT HÓA' in sec or 'TÍNH CHẤT VẬT' in sec:return 19
  return 18
 if ch==7:
  if 'ÔN TẬP' in sec:return 26
  return 25 if 'IIA' in sec else 24
 if ch==8:
  if 'ÔN TẬP' in sec:return 30
  if 'PHỨC CHẤT' in sec:
   return 29 if any(k in stem.upper() for k in ('ỨNG DỤNG','THÍ NGHIỆM','TẠO THÀNH PHỨC','PHẢN ỨNG TẠO PHỨC','NOBEL')) else 28
  return 27
 return 0
def scan(stem,meta):
 grade,ch,chn=meta
 soup=BeautifulSoup((HTML/(stem+'.html')).read_text(encoding='utf-8'),'html.parser')
 out=[];cur=None;section='';phase='q';counter=0
 def finish():
  nonlocal cur
  if not cur:return
  cur['hasMedia']=bool(cur.pop('embedded',False))
  cur['mediaMissing']=cur.pop('mediaMissing',False)
  cur['hasKey']=len(cur['correct'])==4 and all(type(x)==bool for x in cur['correct'])
  cur['qualityFlags']=[]
  if len(cur['statements'])!=4:cur['qualityFlags'].append('Không đủ 4 nhận định a–d')
  if not cur['hasKey']:cur['qualityFlags'].append('Thiếu khóa đáp án 4 ý')
  if len(cur['explanations'])!=4:cur['qualityFlags'].append('Thiếu lời giải riêng từng ý')
  if cur['hasMedia']:cur['qualityFlags'].append('Có hình/đồ thị/công thức nhúng')
  if cur['mediaMissing']:cur['qualityFlags'].append('Hình/công thức MathType không chuyển được thành ảnh hiển thị')
  if 'chưa kiểm tra' in norm(cur['stemHtml']):cur['qualityFlags'].append('Câu gốc có dữ kiện chưa rõ')
  if len(norm(cur['stemHtml']))<12:cur['qualityFlags'].append('Mở đầu câu hỏi ngắn hoặc thiếu')
  if re.search(r'\b(hình bên|hình sau|bảng sau|đồ thị|sơ đồ sau|biểu đồ|hình vẽ)\b',norm(cur['stemHtml'])) and not cur['hasMedia']:cur['qualityFlags'].append('Có tham chiếu hình/bảng nhưng hình không tìm thấy')
  # Câu có lời giải dạng 'Đúng.' nhưng không giải thích nội dung, không được tự đưa vào chấm.
  detailed=len(cur['explanations'])==4 and all(len(norm(t))>=19 for t in cur['explanations'])
  auto=(cur['hasKey'] and detailed and len(cur['statements'])==4 and not cur['hasMedia'] and not cur['mediaMissing'] and not cur['qualityFlags'])
  cur['status']='auto_accepted_source_key' if auto else 'quarantined_unverified'
  cur['fingerprint']=sig(cur) if len(cur['statements'])==4 else ''
  cur['confidenceLabel']='Đủ khóa & giải thích nguồn; chưa xác minh khoa học độc lập' if auto else 'Cần bổ sung minh chứng trước khi chấm'
  out.append(cur);cur=None
 for el in soup.body.find_all(recursive=False):
  if not isinstance(el,Tag) or el.name not in ['p','div','table','h2','h3']:continue
  raw=space.sub(' ',el.get_text(' ',strip=True)).strip()
  if not raw and not el.find('img'):continue
  if SECT.match(raw) and len(raw)<160:
   section=raw;continue
  mat=SRCQ.match(raw)
  if mat:
   finish();counter+=1;no=int(mat.group(1));html,missing,fig=clean_element(el,stem)
   html=prefix_remove(html,r'^\s*Câu\s*'+str(no)+r'\s*[.:(]?\s*')
   lesson=lesson_by_chapter(ch,section,mat.group(2))
   cur={'id':f'e718-{ch}-{counter:03d}-{no}','grade':grade,'chapter':ch,'chapterName':chn,'lesson':lesson,'lessonName':f'Bài {lesson}. {LESSONS[ch].get(lesson,chn)}' if lesson else f'Chưa định vị được bài · {section[:70]}', 'part':'II','type':'true_false','sectionOrigin':section or chn,'sourceNumber':no,'sourceFile':stem+'.docx','stemHtml':html,'statements':[],'correct':[],'explanations':[],'mediaHtml':'','solutionIntroHtml':'','embedded':fig>0,'mediaMissing':missing,'levelSuggested':'Thông hiểu','competencySuggested':'HH1'}
   phase='q';continue
  if cur is None:continue
  if re.match(r'^Hướng\s*dẫn\s*giải',raw,re.I):phase='solution';continue
  frag,miss,fig=clean_element(el,stem);cur['embedded']|=fig>0;cur['mediaMissing']|=miss
  mo=OPT.match(raw)
  if mo:
   frag=prefix_remove(frag,r'^\s*'+mo.group(1)+r'\s*\)\s*')
   if phase=='q':
    if len(cur['statements'])<4:cur['statements'].append(frag)
    else:cur['mediaHtml']+=frag
   else:
    ans=re.match(r'^(Đúng|Sai)\b',mo.group(2),re.I)
    cur['correct'].append(ans.group(1).casefold()=='đúng' if ans else None)
    cur['explanations'].append(frag)
  else:
   if phase=='q':
    if len(cur['statements'])<4:cur['stemHtml']+=frag
    else:cur['mediaHtml']+=frag
   else:
    if cur['explanations']:cur['explanations'][-1]+=frag
    else:cur['solutionIntroHtml']+=frag
 finish();return out

