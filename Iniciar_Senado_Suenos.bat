@echo off
title 🌌 Orbe de Verix - Modo Subconsciente
color 0B
echo.
echo ==============================================================
echo   ENCENDIENDO EL SENADO DE LOS SUEÑOS (Modo Daemon)
echo   Verix analizara el Orbe en las sombras de forma perpetua.
echo ==============================================================
echo.

set BIN_PATH=%~dp0verix_suenos\target\release\verix_suenos.exe

if exist "%BIN_PATH%" (
    echo [OK] Desprendiendo proceso... 
    powershell -WindowStyle Hidden -Command "Start-Process '%BIN_PATH%' -WindowStyle Hidden -WorkingDirectory '%~dp0verix_suenos'"
    echo [EXITO] Verix esta soñando en segundo plano. Ya puedes cerrar esta ventana.
    timeout /t 3 >nul
) else (
    echo [ERROR] No encuentro el binario compilado.
    echo Ejecuta: cargo build --release en verix_suenos\
    pause
)
