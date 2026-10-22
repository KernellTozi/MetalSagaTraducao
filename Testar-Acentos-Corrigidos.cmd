@echo off
cd /d "%~dp0"
python tools\start_test.py --iso layout
if errorlevel 1 pause
