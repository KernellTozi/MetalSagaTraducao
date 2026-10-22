@echo off
cd /d "%~dp0"
python tools\start_test.py --iso fonts
if errorlevel 1 pause
