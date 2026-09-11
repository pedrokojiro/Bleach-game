@echo off
cd /d "%~dp0"
if exist "..\..\.venv\Scripts\python.exe" (
 "..\..\.venv\Scripts\python.exe" game.py
) else (
 py -3 game.py
)
if errorlevel 1 (
 echo.
 echo Verifique se o Python esta instalado e execute INSTALAR.cmd primeiro.
 pause
)
