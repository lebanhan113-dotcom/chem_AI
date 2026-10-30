@echo off
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
  echo Can cai Node.js 20+ de chay server AI tuy chon.
  echo Co the mo truc tiep index.html.
  pause
  exit /b 1
)
start "" http://localhost:3000
node server.mjs
pause
