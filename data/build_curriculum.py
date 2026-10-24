import json
from pathlib import Path
R={
10:[
('Cấu tạo nguyên tử',['Thành phần của nguyên tử','Nguyên tố hóa học','Cấu trúc lớp vỏ electron nguyên tử','Ôn tập chương 1']),
('Bảng tuần hoàn các nguyên tố hóa học và định luật tuần hoàn',['Cấu tạo của bảng tuần hoàn các nguyên tố hóa học','Xu hướng biến đổi một số tính chất của nguyên tử các nguyên tố trong một chu kì và trong một nhóm','Xu hướng biến đổi thành phần và một số tính chất của hợp chất trong một chu kì','Định luật tuần hoàn, ý nghĩa của bảng tuần hoàn các nguyên tố hóa học','Ôn tập chương 2']),
('Liên kết hóa học',['Quy tắc octet','Liên kết ion','Liên kết cộng hóa trị','Liên kết hydrogen và tương tác van der Waals','Ôn tập chương 3']),
('Phản ứng oxi hóa - khử',['Phản ứng oxi hóa - khử','Ôn tập chương 4']),
('Năng lượng hóa học',['Biến thiên enthalpy trong các phản ứng hóa học','Ôn tập chương 5']),
('Tốc độ phản ứng',['Tốc độ phản ứng','Ôn tập chương 6']),
('Nguyên tố nhóm halogen',['Nhóm halogen','Hydrogen halide. Muối halide','Ôn tập chương 7'])],
11:[
('Cân bằng hóa học',['Khái niệm về cân bằng hóa học','Cân bằng trong dung dịch nước','Ôn tập chương 1']),
('Nitrogen - Sulfur',['Nitrogen','Ammonia - Muối ammonium','Một số hợp chất của nitrogen với oxygen','Sulfur và sulfur dioxide','Sulfuric acid và muối sulfate','Ôn tập chương 2']),
('Đại cương về hóa học hữu cơ',['Hợp chất hữu cơ và hóa học hữu cơ','Phương pháp tách biệt và tinh chế hợp chất hữu cơ','Công thức phân tử hợp chất hữu cơ','Cấu tạo hóa học hợp chất hữu cơ','Ôn tập chương 3']),
('Hydrocarbon',['Alkane','Hydrocarbon không no','Arene (hydrocarbon thơm)','Ôn tập chương 4']),
('Dẫn xuất halogen - Alcohol - Phenol',['Dẫn xuất halogen','Alcohol','Phenol','Ôn tập chương 5']),
('Hợp chất carbonyl - Carboxylic acid',['Hợp chất carbonyl','Carboxylic acid','Ôn tập chương 6'])],
12:[
('Ester - Lipid',['Ester - Lipid','Xà phòng và chất giặt rửa','Ôn tập chương 1']),
('Carbohydrate',['Giới thiệu về carbohydrate. Glucose và fructose','Saccharose và maltose','Tinh bột và cellulose','Ôn tập chương 2']),
('Hợp chất chứa nitrogen',['Amine','Amino acid và peptide','Protein và enzyme','Ôn tập chương 3']),
('Polymer',['Đại cương về polymer','Vật liệu polymer','Ôn tập chương 4']),
('Pin điện và điện phân',['Thế điện cực và nguồn điện hóa học','Điện phân','Ôn tập chương 5']),
('Đại cương về kim loại',['Cấu tạo và liên kết trong tinh thể kim loại','Tính chất vật lí và tính chất hóa học của kim loại','Kim loại trong tự nhiên và phương pháp tách kim loại','Hợp kim','Sự ăn mòn kim loại','Ôn tập chương 6']),
('Nguyên tố nhóm IA và nhóm IIA',['Nguyên tố nhóm IA','Nguyên tố nhóm IIA','Ôn tập chương 7']),
('Sơ lược về dãy kim loại chuyển tiếp thứ nhất và phức chất',['Đại cương về kim loại chuyển tiếp dãy thứ nhất','Sơ lược về phức chất','Một số tính chất và ứng dụng của phức chất','Ôn tập chương 8'])]
}
urls={10:'https://www.sgkvn.com/lop-10-13/ket-noi-tri-thuc-voi-cuoc-song-3/hoa-hoc-10-3643.html',11:'https://sgkvn.com/lop-11-14/ket-noi-tri-thuc-voi-cuoc-song-3/hoa-hoc-1169.html',12:'https://www.sgkvn.com/lop-12-15/ket-noi-tri-thuc-voi-cuoc-song-3/hoa-hoc-12-3683.html'}
data={}
for grade,chapters in R.items():
 counter=0
 data[str(grade)]=[]
 for i,(name,lessons) in enumerate(chapters,1):
  L=[]
  for title in lessons:
   counter+=1
   L.append({'id':f'{grade}-{counter}','number':counter,'title':title,'review':title.lower().startswith('ôn tập')})
  data[str(grade)].append({'id':f'{grade}-C{i}','number':i,'title':name,'lessons':L})
 print(grade,len(chapters),counter)
assert [len(x) for x in data.values()]==[7,6,8]
Path(__file__).with_name('curriculum.json').write_text(json.dumps({'grades':data,'reference_urls':urls},ensure_ascii=False,indent=2))
