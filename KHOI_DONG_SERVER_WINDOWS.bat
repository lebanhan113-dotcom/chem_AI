@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo CHEM-MAP TUTOR AI 3.5 - Khoi dong may chu tai may tinh
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 -m pip install -r requirements.txt
    py -3 -m uvicorn server:APP --host 127.0.0.1 --port 8000
) else (
    python -m pip install -r requirements.txt
    python -m uvicorn server:APP --host 127.0.0.1 --port 8000
)
echo May chu da dung. Neu co loi, kiem tra Python va cong 8000.
pause
