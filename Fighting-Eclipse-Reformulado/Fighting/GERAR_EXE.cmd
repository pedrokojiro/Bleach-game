@echo off
cd /d "%~dp0"
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto erro
py -3 -m pip install pyinstaller
if errorlevel 1 goto erro
py -3 -m PyInstaller --noconfirm --clean --onedir --windowed --name EclipseSpiritClash --add-data "assets;assets" game.py
if errorlevel 1 goto erro
echo.
echo Distribuicao criada em dist\EclipseSpiritClash.
echo Compartilhe a pasta inteira, nao apenas o .exe.
pause
exit /b 0
:erro
echo Falha na instalacao ou no empacotamento. Veja a mensagem acima.
pause
exit /b 1
