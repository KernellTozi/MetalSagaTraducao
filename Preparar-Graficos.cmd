@echo off
cd /d "%~dp0"
python tools\interface_graphics.py --recipe translations\interface-graphics-v010.json
if errorlevel 1 echo Falha na composicao. Nenhuma ISO foi alterada.
pause
