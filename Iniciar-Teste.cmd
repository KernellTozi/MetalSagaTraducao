@echo off
cd /d "%~dp0"
if "%~1"=="" (
  python tools\start_test.py --iso region
) else (
  python tools\start_test.py --iso "%~1"
)
if errorlevel 1 pause
