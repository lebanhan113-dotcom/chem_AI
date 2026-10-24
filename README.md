# CHEM-MAP TUTOR AI 3.5 - Sua lua chon lop / chuong / bai

Tac gia giai phap: Le Ba Nhan - Truong THPT Hon Dat.

## Thay doi chinh

- Giao dien hoc sinh: **Chon lop -> Chon chuong -> Chon bai (hoac on ca chuong) -> Chon muc do, dang cau va so cau -> Bat dau**.
- Khi doi lop: reset chuong va bai cu; khi doi chuong: reset bai cu; khong lay nham bai cua lop / chuong khac.
- Chua chon chuong thi danh sach bai va nut bat dau se khoa. Hoc sinh van co the xem danh muc 78 bai.
- Hien thi so cau **thuc su co the luyen** theo bai, muc do va dang cau; tu luan can cham tay khong nam trong luot tu cham.
- Neu bai chua co cau da duyet, hien thong bao va cho phep chuyen sang on ca chuong. Khong tu tao dap an, khong dung cau chua duoc duyet.
- Giu 21 chuong / 78 bai KNTT Hoa hoc 10-12 va 672 cau nguon + 83 cau mau tu phien ban truoc, khong xoa co so du lieu cu.
- Sua nhan phien ban; file khoi chay giao dien ten chinh xac la **index.html** o thu muc goc.

## Chay tren may tinh / may chu

Yeu cau Python 3.11+.

```bash
python -m pip install -r requirements.txt
```

Trong moi truong thu nghiem co the chay:

```bash
uvicorn server:APP --host 127.0.0.1 --port 8000
```

Mo http://127.0.0.1:8000/index.html trong trinh duyet. Trang / cung hien giao dien nay.

Trien khai tren Internet: can dich vu host ung dung Python (hoac Docker), HTTPS, bien `SESSION_SECRET` dai ngau nhien, `ADMIN_PASSWORD` bao mat va co so du lieu ben vung. Khong dang `ADMIN_PASSWORD` va `SESSION_SECRET` vao index.html. Xem `.env.example` va Dockerfile/render.yaml.

**Luu y:** chi tai `index.html` len static hosting se khong co API, khong the luu bai lam / du lieu nhieu nguoi dung. Phai trien khai ca server.py, assets/, data/ va cac thu vien.

## Thao tac hoc sinh

1. Mo menu **Hoc & luyen theo tung bai**.
2. Chon lop 10/11/12. Danh sach chuong tu cap nhat.
3. Chon chuong. Danh sach bai tu cap nhat theo chuong. Chon bai can hoc, hoac `On tap tong hop ca chuong`.
4. Chon muc do: Nhan biet, Thong hieu, Van dung, Van dung cao hoac tat ca; chon trac nghiem / dung sai / tra loi ngan; chon so cau.
5. Doc so cau co the luyen. Neu khong du, doi bo loc hoac on ca chuong; cau chua duyet se khong xuat hien.
6. Bam **Bat dau luyen tap**, lam tung cau va xem huong dan sau khi tra loi.

## Khoi dong lai server tren may ca nhan

- Dung may chu dang chay bang `Ctrl+C` tai cua so terminal do.
- Di chuyen vao thu muc WebApp va chay lai lenh `uvicorn server:APP --host 127.0.0.1 --port 8000`.
- Tren Windows, co the dung `KHOI_DONG_SERVER_WINDOWS.bat` trong thu muc goc.
- Khong tu dong ket thuc cac tien trinh tren cong 8000 neu khong biet ro chung thuoc ung dung nao.

## Kiem thu

```bash
python tests/test_server.py
python tests/test_sources.py
python tests/test_grade12_sources.py
python tests/test_study34.py
python tests/test_student_selection35.py
node --check static/app3.js
```

Kiem thu API da dat; UI Playwright voi API mo phong da dat tren kich thuoc may tinh va dien thoai. Moi truong trinh duyet tu dong da chan truy cap loopback; viec khoi dong server va API HTTP duoc kiem tra bang curl rieng.

Day la ban MVP; truoc khi su dung voi hoc sinh that can kiem dinh noi dung cau hoi, bao mat va quan ly thong tin ca nhan.
