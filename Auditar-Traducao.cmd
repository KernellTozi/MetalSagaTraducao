@echo off
setlocal
cd /d "%~dp0"
python tools\audit_dialogue_backlog.py --build-dir work\interface-v051-final %*
set "audit_result=%errorlevel%"
if not "%audit_result%"=="0" goto audit_end
python tools\item_name_capacity.py
set "audit_result=%errorlevel%"
:audit_end
echo.
pause
exit /b %audit_result%
