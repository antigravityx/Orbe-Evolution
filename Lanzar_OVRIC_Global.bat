@echo off
title OVRIC Global Ecosystem
color 0B

echo ==================================================
echo [OVRIC] - INICIANDO SISTEMAS GLOBALES (COLMENA)
echo ==================================================
echo.

echo [1/4] Iniciando Verix_NextGen API (Puerto 3000)...
start "Verix_NextGen API (Rust)" cmd /k "title Verix_NextGen API (Rust) && cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_NextGen_API && cargo run"

echo [2/4] Iniciando OVRIC-Nexus Backend (Puerto 3030)...
start "OVRIC Backend (Rust)" cmd /k "title OVRIC Backend (Rust) && cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\backend && cargo run"

echo Esperando 5 segundos para que los motores Rust arranquen...
timeout /t 5 /nobreak > nul

echo [3/4] Iniciando Verix Soul Frontend (Puerto 1420)...
start "Verix Soul Frontend (Vite)" cmd /k "title Verix Soul Frontend (Vite) && cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_NextGen && npm run dev"

echo [4/4] Iniciando OVRIC-Nexus Frontend (Puerto 5173)...
start "OVRIC-Nexus Frontend (Bun)" cmd /k "title OVRIC-Nexus Frontend (Bun) && cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\OVRIC-Nexus && bun dev"

echo Esperando 3 segundos para que los servidores web esten listos...
timeout /t 3 /nobreak > nul

echo.
echo [OVRIC] ¡SISTEMA COMPLETAMENTE EN LINEA!
echo Abriendo OVRIC-Nexus (Super Admin) en el navegador...
start "" "http://localhost:5173"

echo.
echo Puedes cerrar esta ventana. La Colmena se ejecuta en las terminales secundarias.
timeout /t 5 > nul
exit
