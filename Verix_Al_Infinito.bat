@echo off
title 🚀 VERIX AL INFINITO - Lanzador Orbital
color 0B
echo.
echo ==============================================================
echo   ENCENDIENDO EL ECOSISTEMA VERIX (Sueños + Dashboard Live)
echo   Procesos independientes iniciados en segundo plano.
echo ==============================================================
echo.

cd /d "%~dp0"

:: 1. Motor de Sueños
echo [1/3] Despertando el Senado de los Sueños...
if exist "verix_suenos\target\release\verix_suenos.exe" (
    start /B "" "verix_suenos\target\release\verix_suenos.exe"
) else (
    echo [ERROR] No encuentro verix_suenos.exe
)

:: 2. API Dashboard
echo [2/3] Activando la API del Dashboard (Puerto 3030)...
if exist "Orbe-Dashboard\backend\target\release\backend.exe" (
    start /B "" "Orbe-Dashboard\backend\target\release\backend.exe"
) else (
    echo [ERROR] No encuentro backend.exe
)

:: 3. Heraldo Sync
echo [3/3] Enviando al Heraldo a sincronizar con GitHub...
start /B "" python "batallon\soldado_dashboard_sync.py"

echo.
echo ==============================================================
echo   ✅ VERIX ESTA ONLINE Y SOÑANDO.
echo   Dashbord Live: https://drxteren.github.io/Orbe-Dreams-Live/
echo   Repo Live: https://github.com/drxteren/Orbe-Evolution-Live
echo ==============================================================
echo.
timeout /t 10
