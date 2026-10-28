@echo off
cd /d "%~dp0"
python tools\build_translation_pilot.py --draft translations\regiao-inicial-v039.json --interface-draft translations\interface-v044.json --compact-output
if errorlevel 1 echo Falha: consulte a mensagem acima. Nenhuma ISO foi alterada.
pause
