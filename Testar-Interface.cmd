@echo off
cd /d "%~dp0"
python tools\start_test.py --iso interface
if errorlevel 1 pause
