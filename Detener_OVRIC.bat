@echo off
title Apagando Colmena OVRIC
color 0C

echo ==================================================
echo [OVRIC] - APAGANDO SISTEMAS GLOBALES
echo ==================================================
echo.
echo Cerrando procesos en puertos conocidos (3000, 3030, 1420, 5173)...

for %%p in (3000 3030 1420 5173) do (
    echo - Liberando puerto %%p...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%p" ^| findstr "LISTENING"') do (
        if not "%%a"=="0" (
            taskkill /f /pid %%a > nul 2>&1
        )
    )
)

echo.
echo Cerrando orquestador maestro (Bun)...
taskkill /IM bun.exe /F > nul 2>&1

echo.
echo ¡La Colmena ha sido apagada exitosamente!
timeout /t 3 > nul
