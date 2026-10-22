@echo off
setlocal
cd /d "%~dp0"
python tools\reinsert_dialogues.py %*
set "reinsert_result=%errorlevel%"
echo.
pause
exit /b %reinsert_result%
