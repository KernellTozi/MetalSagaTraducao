@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 ou superior nao encontrado. Instale Python e habilite o PATH.
  pause
  exit /b 1
)
python tools\extract_dialogues.py %*
set "extract_result=%errorlevel%"
echo.
pause
exit /b %extract_result%
