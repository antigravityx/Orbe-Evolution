@echo off
title Forjador de Binarios Verix Soul
echo [!] Iniciando la forja del ejecutable nativo...
echo [*] Verificando dependencias (PyInstaller)...

pip install pyinstaller

echo [*] Compilando orbe_gui.py en un archivo unico...
pyinstaller --noconfirm --onefile --windowed --icon "orbe_icon.ico" --add-data "orbe_estado.json;." --add-data "soul_core.py;." "orbe_gui.py"

echo [OK] La forja ha concluido. Busca tu App en la carpeta 'dist'.
pause
