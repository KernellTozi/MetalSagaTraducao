@echo off
cd /d "%~dp0"
python tools\start_test.py --iso interface --open-folder
if errorlevel 1 pause
