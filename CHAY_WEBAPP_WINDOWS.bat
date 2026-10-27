@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON_CMD=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo CHUA TIM THAY PYTHON. Cai Python 3.11+ va chon Add Python to PATH.
    pause
    exit /b 1
  )
  set "PYTHON_CMD=python"
)
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
  echo Khong cai duoc thu vien. Kiem tra Python va Internet.
  pause
  exit /b 1
)
echo WebApp: http://127.0.0.1:8765
%PYTHON_CMD% -m uvicorn server:app --host 127.0.0.1 --port 8765
pause
