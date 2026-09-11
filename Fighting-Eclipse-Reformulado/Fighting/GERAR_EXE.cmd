@echo off
cd /d "%~dp0"
if not exist "..\..\.venv\Scripts\python.exe" call "..\..\INSTALAR.cmd"
if errorlevel 1 goto erro
"..\..\.venv\Scripts\python.exe" -m pip install pyinstaller
if errorlevel 1 goto erro
"..\..\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name BleachSpiritualCrossroads --distpath "..\..\dist" --workpath "..\..\build\pyinstaller" --specpath "..\..\build" --add-data "%CD%\assets;assets" game.py
if errorlevel 1 goto erro
echo.
echo Executavel criado em dist\BleachSpiritualCrossroads.exe.
pause
exit /b 0
:erro
echo Falha na instalacao ou no empacotamento. Veja a mensagem acima.
pause
exit /b 1
