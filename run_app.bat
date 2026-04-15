@echo off
echo Installation des dependances...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Erreur lors de l'installation des dependances.
    pause
    exit /b %ERRORLEVEL%
)

echo Lancement de l'application Flask...
cd app\src
flask run
pause
