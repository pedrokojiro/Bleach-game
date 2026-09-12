@echo off
cd /d "%~dp0"
py -3 game.py
if errorlevel 1 (
 echo.
 echo Verifique se o Python esta instalado e execute INSTALAR.cmd primeiro.
 pause
)
