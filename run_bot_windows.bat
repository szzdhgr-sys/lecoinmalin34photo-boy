@echo off
setlocal
cd /d "%~dp0"
echo =========================================
echo   LE COIN MALIN 34 - BOT TELEGRAM V7
echo =========================================
if not exist "bot-private.cmd" (
  echo.
  echo ERREUR : creez bot-private.cmd en copiant bot-private.example.cmd
  echo Remplissez BOT_TOKEN sans partager le fichier.
  pause
  exit /b 1
)
call "bot-private.cmd"
if not defined BOT_TOKEN (
  echo ERREUR : BOT_TOKEN manquant dans bot-private.cmd.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creation de l'environnement Python...
  py -3 -m venv .venv
  if errorlevel 1 (
    echo Installez Python 3.11 ou une version plus recente.
    pause
    exit /b 1
  )
)
set "DATA_DIR=%cd%\data"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"
call ".venv\Scripts\activate.bat"
echo Installation des dependances...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERREUR : installation des dependances.
  pause
  exit /b 1
)
echo.
echo Lancement du bot. Ne fermez pas cette fenetre.
python bot.py
echo.
echo Le bot s'est arrete. Lisez les erreurs ci-dessus.
pause
