@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
 echo Vui long cai Node.js 22.13 tro len, sau do mo lai.
 pause
 exit /b 1
)
set CHEMMAP_DEMO=1
echo CHEM-MAP TUTOR AI V7.2 - Le Ba Nhan - Truong THPT Hon Dat
echo Mo trang http://127.0.0.1:8080/ trong Chrome hoac Edge.
echo Tai khoan demo ngau nhien duoc in ben duoi neu la lan dau.
node server/server.js
pause
