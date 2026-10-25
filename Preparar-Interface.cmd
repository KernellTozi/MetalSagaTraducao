@echo off
cd /d "%~dp0"
python tools\build_translation_pilot.py --draft translations\regiao-inicial-v035.json --interface-draft translations\interface-v035.json --compact-output
if errorlevel 1 echo Falha: consulte a mensagem acima. Nenhuma ISO foi alterada.
pause
