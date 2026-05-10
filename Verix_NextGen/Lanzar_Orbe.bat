@echo off
title Orbe Verix Soul - Arquitecto Cronos
echo.
echo ==================================================
echo [VERIX SOUL] - INICIANDO SISTEMAS NATIVOS NEXTGEN
echo ==================================================
echo.
echo Compilando e iniciando API de Rust (Puerto 3000)...
cd /d "%~dp0..\Verix_NextGen_API"
start "Rust API Server" cmd /c "cargo run"

echo.
echo Iniciando Interfaz en Vite (Puerto 1420)...
cd /d "%~dp0"
start "Vite Frontend Server" cmd /c "npm run dev"

echo.
echo Esperando unos segundos para levantar servicios...
timeout /t 5 /nobreak >nul

echo Abriendo el Santuario en el navegador...
start http://localhost:1420/
