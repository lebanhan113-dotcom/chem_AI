@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -m pip install -r requirements.txt
if errorlevel 1 (echo Khong the cai thu vien. Kiem tra Python 3.11+ & Internet. & pause & exit /b 1)
echo Truy cap http://127.0.0.1:8765
python -m uvicorn server:app --host 127.0.0.1 --port 8765
pause
