@echo off
setlocal
cd /d "%~dp0"
python tools\audit_dialogue_backlog.py --build-dir work\interface-v049 %*
set "audit_result=%errorlevel%"
echo.
pause
exit /b %audit_result%
