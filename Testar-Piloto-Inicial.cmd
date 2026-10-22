@echo off
cd /d "%~dp0"
python tools\start_test.py --iso pilot
if errorlevel 1 pause
