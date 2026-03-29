@echo off
echo =======================================================
echo    ORBE VERIX CORE - FORJA DE APK (ANDROID)
echo =======================================================
echo.
echo Para forjar el APK nativamente en tu PC, Tauri requiere que tengas
echo instalado Android Studio, el SDK y el NDK en tus variables de entorno.
echo.
echo Si ya tienes eso configurado, el Orbe iniciara la forja.
echo.
pause

cd %~dp0
call npm run tauri android init
call npm run tauri android build

echo.
echo Si finalizo exitosamente, tu APK estara en:
echo src-tauri\gen\android\app\build\outputs\apk\universal\release\
pause
