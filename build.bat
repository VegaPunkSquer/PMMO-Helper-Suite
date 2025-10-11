REM --- Script para Compilar o The Silph Scope com PyInstaller ---
REM Salve este arquivo como "build.bat" na pasta raiz do seu projeto.
REM Execute-o a partir do terminal para iniciar a compilação.
REM Certifique-se de ter o PyInstaller instalado: pip install pyinstaller

@echo off
echo "Iniciando a compilacao com PyInstaller..."
echo "Isso pode levar alguns minutos..."

pyinstaller --name "The Silph Scope" ^
            --onefile ^
            --windowed ^
            --icon="icon.ico" ^
            --add-data "Images;Images" ^
            --add-data "Maps;Maps" ^
            --add-data "animations;animations" ^
            --add-data "qrcode.png;." ^
            --add-data "sound_manager.py;." ^
            --add-data "battle_logic.py;." ^
            --add-data "emojis.py;." ^
            --add-data "*.json;." ^
            pmmo_suite.py

echo.
echo "------------------------------------------------------------"
echo "Compilacao finalizada com sucesso!"
echo "Seu executavel 'The Silph Scope.exe' esta na pasta 'dist'."
echo "------------------------------------------------------------"
pause