@echo off
cd /d "%~dp0"
python tools\build_translation_pilot.py --draft translations\regiao-inicial-v037.json --interface-draft translations\interface-v039.json --compact-output
if errorlevel 1 echo Falha: consulte a mensagem acima. Nenhuma ISO foi alterada.
pause
