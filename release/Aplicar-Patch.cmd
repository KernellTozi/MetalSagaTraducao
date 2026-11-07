@echo off
setlocal DisableDelayedExpansion
powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File "%~dp0Aplicar-Patch.ps1" -IsoOriginal "%~1"
if errorlevel 1 pause
endlocal
