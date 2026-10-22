@echo off
cd /d "%~dp0"
python tools\start_test.py --iso region
if errorlevel 1 pause
