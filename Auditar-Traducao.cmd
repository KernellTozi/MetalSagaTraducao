@echo off
setlocal
cd /d "%~dp0"
python tools\audit_translation_coverage.py --build-dir work\interface-v030 %*
set "audit_result=%errorlevel%"
echo.
pause
exit /b %audit_result%
