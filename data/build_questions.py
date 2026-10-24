import json
from pathlib import Path
p=Path(__file__).parent
src=json.loads((p/'legacy_bank.json').read_text())['questions']
new=[]
# choices, right index, explanation, lesson number and error tag
M=[
('Phân tử nitrogen (N₂) chứa liên kết nào?',['Một liên kết đơn','Một liên kết đôi','Một liên kết ba','Một liên kết ion'],2,'N₂ có một liên kết ba rất bền, là nguyên nhân quan trọng khiến nitrogen ít hoạt động ở điều kiện thường.',4,'K01'),
('Số oxi hóa của N trong NH₃ là',['+3','−3','+5','0'],1,'Trong NH₃: x + 3(+1) = 0, suy ra x = −3.',5,'P01'),
('Dung dịch NH₃ trong nước có tính',['acid mạnh','base yếu','trung tính','oxi hóa mạnh'],1,'NH₃ nhận proton của H₂O, tạo NH₄⁺ và OH⁻ với mức độ không hoàn toàn.',5,'K01'),
('Chất khí nào có mùi khai đặc trưng?',['N₂','NH₃','NO','CO₂'],1,'Ammonia NH₃ có mùi khai; không được ngửi trực tiếp hóa chất trong phòng thí nghiệm.',5,'K01'),
('Thuốc thử dùng để nhận biết ion NH₄⁺ trong muối ammonium là',['NaOH, đun nóng nhẹ','NaCl','BaCl₂','AgNO₃'],0,'Ion NH₄⁺ phản ứng với OH⁻ khi đun nhẹ tạo NH₃; xác định bằng giấy quỳ ẩm, không ngửi trực tiếp.',5,'K02'),
('Trong NH₄NO₃, số oxi hóa của N ở cation NH₄⁺ là',['−3','+3','+5','−1'],0,'Ion NH₄⁺: x+4=+1 nên x=−3.',5,'P01'),
('Sản phẩm khử phổ biến khi Cu tác dụng với HNO₃ loãng theo phương trình minh họa là',['H₂','NO','N₂','SO₂'],1,'3Cu + 8HNO₃ (loãng) → 3Cu(NO₃)₂ + 2NO + 4H₂O. Sản phẩm khử thực tế phụ thuộc điều kiện.',6,'K04'),
('Trong HNO₃, nitrogen có số oxi hóa',['+3','−3','+5','+4'],2,'HNO₃: (+1)+x+3(−2)=0 ⇒ x=+5.',6,'P01'),
('Khí NO trong không khí dễ chuyển thành',['NO₂','NH₃','N₂','H₂'],0,'NO bị O₂ oxi hóa thành NO₂: 2NO + O₂ → 2NO₂.',6,'K05'),
('Đặc điểm quan trọng của HNO₃ là',['Chỉ có tính acid','Vừa có tính acid, vừa oxi hóa mạnh','Chỉ có tính base','Không phản ứng với kim loại'],1,'HNO₃ thể hiện tính acid và tính oxi hóa mạnh do N có số oxi hóa +5.',6,'K01'),
('Đơn chất sulfur có kí hiệu hóa học là',['Su','S','So','Sr'],1,'Kí hiệu nguyên tố sulfur là S.',7,'K01'),
('Trong SO₂, số oxi hóa của sulfur là',['+6','+4','−2','0'],1,'SO₂: x + 2(−2) = 0 ⇒ x = +4.',7,'P01'),
('SO₂ có thể thể hiện tính khử khi phản ứng với chất nào?',['O₂ (có xúc tác, nhiệt độ thích hợp)','N₂','Ar','H₂O'],0,'SO₂ bị oxi hóa thành SO₃, S từ +4 lên +6: 2SO₂ + O₂ ⇌ 2SO₃.',7,'K02'),
('Acid sulfuric đặc có khả năng',['Hút nước mạnh','Không tan trong nước','Không có tính oxi hóa','Chỉ phản ứng với base'],0,'H₂SO₄ đặc háo nước mạnh; pha loãng phải rót acid từ từ vào nước, không làm ngược lại.',8,'K02'),
('Ion sulfate SO₄²⁻ có thể được nhận biết bằng dung dịch chứa',['Ba²⁺','Na⁺','K⁺','NH₄⁺'],0,'Ba²⁺ + SO₄²⁻ → BaSO₄↓ (trắng), khó tan trong acid loãng.',8,'K01'),
('Kim loại Cu phản ứng với H₂SO₄ đặc, nóng thường tạo khí nào?',['H₂','O₂','SO₂','NH₃'],2,'Cu + 2H₂SO₄ (đặc, nóng) → CuSO₄ + SO₂ + 2H₂O.',8,'K04'),
('Cách pha loãng H₂SO₄ đặc an toàn là',['Rót nước vào acid','Rót acid từ từ vào nước, khuấy đều','Đổ đồng thời thật nhanh','Đun sôi acid trước'],1,'Pha loãng H₂SO₄ rất tỏa nhiệt; luôn thêm acid vào nước từ từ với bảo hộ phù hợp.',8,'K02'),
('Trong BaSO₄, sulfur có số oxi hóa',['+4','+6','−2','0'],1,'BaSO₄ chứa SO₄²⁻, trong ion sulfate sulfur có số oxi hóa +6.',8,'P01')]
for i,(stem,options,correct,exp,lesson,error) in enumerate(M,1):
 q={'id':f'N11-M{i:02d}','grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':f'11-{lesson}','type':'mcq','level':['Nhận biết','Thông hiểu','Vận dụng'][i%3],'stem':stem,'options':options,'correct':correct,'explanation':exp,'skill':'Nitrogen - Sulfur','distractors':{str(j):{'code':error,'hypothesis':'Cần đối chiếu khái niệm, điều kiện phản ứng và dấu hiệu đặc trưng; đây là giả thuyết lỗi từ đáp án đã chọn.'} for j in range(4) if j!=correct},'source':'Câu hỏi biên soạn độc lập theo chương Nitrogen - Sulfur','status':'sample-reviewed'}
 new.append(q)
T=[
('Về tính chất của ammonia', ['NH₃ là base yếu trong dung dịch nước.','NH₃ có thể tạo NH₄⁺ khi nhận H⁺.','NH₃ có liên kết ion N–H.','Dung dịch ammonia làm quỳ tím ẩm hóa xanh.'],[True,True,False,True],['Đúng: NH₃ phản ứng một phần với nước.','Đúng: NH₃ là base Brønsted.','Sai: N–H là liên kết cộng hóa trị phân cực.','Đúng: dung dịch có OH⁻.'],5),
('Về nitric acid', ['Trong HNO₃, nitrogen có số oxi hóa +5.','HNO₃ loãng phản ứng với Cu, thường cho khí NO trong phương trình minh họa.','HNO₃ là acid có tính oxi hóa yếu.','Dung dịch HNO₃ phản ứng với CaCO₃ tạo CO₂.'],[True,True,False,True],['Đúng: tổng số oxi hóa bằng 0.','Đúng với điều kiện phản ứng minh họa đã nêu.','Sai: HNO₃ oxi hóa mạnh.','Đúng: phản ứng acid với carbonate.'],6),
('Về sulfur dioxide', ['SO₂ là oxide acid.','S trong SO₂ có số oxi hóa +4.','SO₂ luôn chỉ thể hiện tính oxi hóa.','SO₂ có thể bị oxi hóa thành SO₃.'],[True,True,False,True],['Đúng: SO₂ + H₂O ⇌ H₂SO₃.','Đúng: S +4.','Sai: SO₂ còn thể hiện tính khử.','Đúng: với O₂ và điều kiện thích hợp.'],7),
('Về sulfuric acid và sulfate', ['H₂SO₄ đặc có tính háo nước.','Khi pha loãng cần thêm nước vào acid đặc.','Ion sulfate tạo kết tủa trắng với Ba²⁺.','H₂SO₄ loãng tác dụng với Zn có thể giải phóng H₂.'],[True,False,True,True],['Đúng.','Sai: phải cho từ từ acid vào nước.','Đúng: BaSO₄ trắng.','Đúng: Zn + H₂SO₄ → ZnSO₄ + H₂.'],8)]
for i,(stem,statements,cor,why,lesson) in enumerate(T,1):
 new.append({'id':f'N11-T{i:02d}','grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':f'11-{lesson}','type':'tf','level':'Thông hiểu','stem':stem,'statements':statements,'correct':cor,'statementExplanations':why,'explanation':'Xét riêng từng nhận định và căn cứ hóa học.','skill':'Nitrogen - Sulfur','source':'Câu hỏi biên soạn độc lập','status':'sample-reviewed'})
S=[
('Trong phân tử NH₃ có bao nhiêu nguyên tử H?',3,'NH₃ chứa 3 nguyên tử H.',5),
('Tổng số nguyên tử có trong một phân tử HNO₃ là bao nhiêu?',5,'1 H + 1 N + 3 O = 5.',6),
('Số oxi hóa của sulfur trong SO₂ là bao nhiêu?',4,'x+2(−2)=0 ⇒ x=+4.',7),
('Hệ số của HNO₃ sau khi cân bằng phương trình: Cu + HNO₃ (loãng) → Cu(NO₃)₂ + NO + H₂O là bao nhiêu?',8,'3Cu + 8HNO₃ → 3Cu(NO₃)₂ + 2NO + 4H₂O.',6),
('Với 0,10 mol ion SO₄²⁻ và đủ Ba²⁺, số mol kết tủa BaSO₄ bằng bao nhiêu? (Ghi theo mol.)',0.10,'Phản ứng Ba²⁺ + SO₄²⁻ → BaSO₄ theo tỉ lệ 1:1.',8),
('Hòa tan 0,10 mol Zn bằng H₂SO₄ loãng vừa đủ. Số mol H₂ tạo thành là bao nhiêu?',0.10,'Zn + H₂SO₄ → ZnSO₄ + H₂, tỉ lệ mol Zn:H₂=1:1.',8)]
for i,(stem,answer,exp,lesson) in enumerate(S,1):
 new.append({'id':f'N11-S{i:02d}','grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':f'11-{lesson}','type':'short','level':'Vận dụng' if i>3 else 'Nhận biết','stem':stem,'correct':answer,'tolerance':0.001,'explanation':exp,'skill':'Nitrogen - Sulfur','source':'Câu hỏi biên soạn độc lập','status':'sample-reviewed'})
E=[
('Trình bày tính base của ammonia NH₃ trong nước. Viết phương trình minh họa và nêu một cách nhận biết ion NH₄⁺.','NH₃ + H₂O ⇌ NH₄⁺ + OH⁻; NH₄⁺ + OH⁻ (đun nhẹ) → NH₃↑ + H₂O. Dùng giấy quỳ tím ẩm gần miệng ống nghiệm xác định khí NH₃; không ngửi trực tiếp.',5),
('Cân bằng phản ứng Cu với HNO₃ loãng cho NO. Xác định chất oxi hóa, chất khử và giải thích sự thay đổi số oxi hóa.','3Cu + 8HNO₃ → 3Cu(NO₃)₂ + 2NO + 4H₂O. Cu⁰ → Cu²⁺ là chất khử. N(+5) trong nitrate → N(+2) trong NO: HNO₃ (NO₃⁻) là chất oxi hóa.',6),
('Viết phương trình oxi hóa SO₂ thành SO₃ và giải thích vì sao SO₂ có thể thể hiện tính khử.','2SO₂ + O₂ ⇌ 2SO₃ (xúc tác V₂O₅, nhiệt độ thích hợp). S tăng số oxi hóa từ +4 lên +6 nên SO₂ là chất khử.',7),
('Trình bày phương pháp nhận biết ion sulfate trong một mẫu dung dịch và giải thích yêu cầu an toàn khi pha loãng H₂SO₄ đặc.','Cho dung dịch chứa Ba²⁺ thích hợp: Ba²⁺ + SO₄²⁻ → BaSO₄↓ màu trắng. Khi pha loãng H₂SO₄ đặc luôn rót acid từ từ vào nước vì phản ứng tỏa nhiệt mạnh, có nguy cơ bắn acid nếu làm ngược.',8)]
for i,(stem,exp,lesson) in enumerate(E,1):
 new.append({'id':f'N11-E{i:02d}','grade':11,'chapter':'Nitrogen - Sulfur','lesson_id':f'11-{lesson}','type':'essay','level':'Vận dụng cao','stem':stem,'explanation':exp,'correct':None,'rubric':'Giáo viên chấm theo mức độ đầy đủ, tính chính xác và lập luận; tổng 1 điểm/câu trong bản mẫu.','skill':'Nitrogen - Sulfur','source':'Câu hỏi biên soạn độc lập','status':'sample-reviewed'})
for q in src:
 q['chapter']=q['chapter'].replace('Nitrogen – Sulfur','Nitrogen - Sulfur').replace('Ester – Lipid','Ester - Lipid').replace('Hợp chất carbonyl – Carboxylic acid','Hợp chất carbonyl - Carboxylic acid')
 q['chapter']=q['chapter'].replace('Bảng tuần hoàn các nguyên tố hóa học','Bảng tuần hoàn các nguyên tố hóa học và định luật tuần hoàn').replace('Tốc độ phản ứng hóa học','Tốc độ phản ứng').replace('Đại cương hóa học hữu cơ','Đại cương về hóa học hữu cơ').replace('Kim loại chuyển tiếp và phức chất','Sơ lược về dãy kim loại chuyển tiếp thứ nhất và phức chất')
 if q['id']=='C11-008': q['chapter']='Hợp chất carbonyl - Carboxylic acid'
 q['status']='legacy-demo'
 q['lesson_id']=None
 # Assign legacy sample to an exact KNTT lesson only when the stem clearly matches.
 maps={
 'C10-001':3,'C10-002':3,'C10-003':6,'C10-004':11,'C10-005':12,'C10-006':15,'C10-007':15,'C10-008':15,'C10-009':17,'C10-010':19,'C10-011':21,'C10-012':15,'C10-013':15,'C10-014':21,'C10-016':15,'C10-017':15,
 'C11-008':23,'C11-001':1,'C11-002':1,'C11-003':2,'C11-004':5,'C11-005':6,'C11-006':6,'C11-007':8,'C11-009':16,'C11-010':17,'C11-011':20,'C11-012':24,'C11-013':1,'C11-014':6,'C11-015':6,'C11-016':2,'C11-017':6,
 'C12-001':1,'C12-002':1,'C12-003':1,'C12-004':5,'C12-005':4,'C12-006':8,'C12-007':9,'C12-008':12,'C12-009':15,'C12-010':22,'C12-012':28,'C12-013':1,'C12-014':15,'C12-015':1,'C12-016':16,'C12-017':1}
 if q['id'] in maps:q['lesson_id']=str(q['grade'])+'-'+str(maps[q['id']])
 q['source']='Dữ liệu mẫu CHEM-MAP 2.1; cần kiểm duyệt lại'
# no duplication with 32, distinct IDs
final=new+src
print('New',len(new),'total',len(final),'distribution',{t:sum(q['type']==t for q in new) for t in ['mcq','tf','short','essay']})
(p/'questions.json').write_text(json.dumps(final,ensure_ascii=False,indent=2))
