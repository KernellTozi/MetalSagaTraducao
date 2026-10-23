@echo off
cd /d "%~dp0"
python tools\prepare_interface_atlases.py
if errorlevel 1 echo Falha na preparacao dos atlas. Nenhuma ISO foi alterada.
pause
