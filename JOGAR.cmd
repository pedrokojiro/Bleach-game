@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Execute INSTALAR.cmd primeiro.
 pause
 exit /b 1
)
cd Fighting-Eclipse-Reformulado\Fighting
"..\..\.venv\Scripts\python.exe" game.py
if errorlevel 1 pause
