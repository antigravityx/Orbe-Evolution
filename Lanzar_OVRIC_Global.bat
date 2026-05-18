@echo off
title OVRIC God Mode — Colmena Completa
color 0B

echo ==================================================
echo  ██████╗ ██╗   ██╗██████╗ ██╗ ██████╗
echo ██╔═══██╗██║   ██║██╔══██╗██║██╔════╝
echo ██║   ██║██║   ██║██████╔╝██║██║
echo ██║   ██║╚██╗ ██╔╝██╔══██╗██║██║
echo ╚██████╔╝ ╚████╔╝ ██║  ██║██║╚██████╗
echo  ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝ ╚═════╝
echo         GOD MODE — COLMENA DE INTELIGENCIA
echo ==================================================
echo.

echo [1/5] Iniciando Orquestador con Hipocampo (Puerto 3050)...
start /min "OVRIC Orquestador + Hipocampo" cmd /c "cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe && bun run ovric_orchestrator.ts"

echo Esperando 4 segundos para que el Orquestador este listo...
timeout /t 4 /nobreak > nul

echo [2/5] Iniciando Verix_NextGen API (Puerto 3000)...
start /min "Verix_NextGen API" cmd /c "cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_NextGen_API && cargo run"

echo [3/5] Iniciando OVRIC-Nexus Backend Rust (Puerto 3030)...
start /min "OVRIC Backend Rust" cmd /c "cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\backend && cargo run"

echo Esperando 5 segundos para que los motores Rust arranquen...
timeout /t 5 /nobreak > nul

echo [4/5] Iniciando Verix Soul Frontend (Puerto 1420)...
start /min "Verix Soul" cmd /c "cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_NextGen && npm run dev"

echo [5/5] Iniciando OVRIC-Nexus Tauri (God Mode Nativo)...
start /min "OVRIC-Nexus Tauri" cmd /c "cd /d C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\OVRIC-Nexus && npm run tauri dev"

echo Esperando 8 segundos para que todo este en linea...
timeout /t 8 /nobreak > nul

echo.
echo ==================================================
echo  [OVRIC] SISTEMA COMPLETAMENTE EN LINEA - GOD MODE
echo  Orquestador: http://localhost:3050
echo  API Rust:    http://localhost:3030
echo  Frontend:    http://localhost:5173
echo ==================================================
echo.
start "" "http://localhost:5173"

timeout /t 5 > nul
exit
