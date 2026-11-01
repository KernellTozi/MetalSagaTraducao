@echo off
setlocal
cd /d "%~dp0"
python tools\audit_dialogue_backlog.py --build-dir work\interface-v061-final %*
set "audit_result=%errorlevel%"
if not "%audit_result%"=="0" goto audit_end
python tools\item_name_capacity.py --current-recipe translations\interface-v061.json
set "audit_result=%errorlevel%"
:audit_end
echo.
pause
exit /b %audit_result%
