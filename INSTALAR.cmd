@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if errorlevel 1 goto erro
".venv\Scripts\python.exe" -m pip install -r Fighting-Eclipse-Reformulado\Fighting\requirements.txt
if errorlevel 1 goto erro
echo Instalacao concluida. Abra JOGAR.cmd.
pause
exit /b 0
:erro
echo Falha na instalacao. Verifique Python 3.10+ e conexao com a internet.
pause
exit /b 1
