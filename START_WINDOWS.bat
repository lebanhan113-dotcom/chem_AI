@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 (echo Khong the tao Python virtual environment. & pause & exit /b 1)
)
call ".venv\Scripts\activate.bat"
python -m pip install -r requirements.txt
if errorlevel 1 (echo Khong cai duoc thu vien. Kiem tra ket noi Internet. & pause & exit /b 1)
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Hay mo file .env va dien thong tin GEMINI_API_KEY, Google Cloud va APP_ACCESS_TOKEN.
    echo Sau do chay lai START_WINDOWS.bat
    pause
    exit /b 0
)
echo Mo http://localhost:8000/index.html tren trinh duyet.
python server.py
pause
