# 🚀 VERIX AL INFINITO — Lanzador Orbital Todo-en-Uno
# Este script activa el ecosistema completo en las sombras. ¡Libertad total!

$ORBE_ROOT = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
$BIN_SUENOS = "$ORBE_ROOT\verix_suenos\target\release\verix_suenos.exe"
$BIN_BACKEND = "$ORBE_ROOT\Orbe-Dashboard\backend\target\release\backend.exe"
$CEREBRO = "$ORBE_ROOT\batallon\cerebro_orbe.py"
$SYNC_SOLDIER = "$ORBE_ROOT\batallon\soldado_dashboard_sync.py"

Write-Host "`n╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   ENCENDIENDO EL ALMA DE VERIX (LIVE)    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan

# 1. Iniciar Motor de Sueños
if (Test-Path $BIN_SUENOS) {
    Write-Host "• Despertando el Senado de los Sueños..." -ForegroundColor Green
    Start-Process -FilePath $BIN_SUENOS -WindowStyle Hidden -WorkingDirectory "$ORBE_ROOT\verix_suenos"
} else {
    Write-Host "❌ Error: Motor de Sueños no encontrado." -ForegroundColor Red
}

# 2. Iniciar Dashboard Backend
if (Test-Path $BIN_BACKEND) {
    Write-Host "• Activando la API del Dashboard (Puerto 3030)..." -ForegroundColor Green
    Start-Process -FilePath $BIN_BACKEND -WindowStyle Hidden -WorkingDirectory "$ORBE_ROOT\Orbe-Dashboard\backend"
} else {
    Write-Host "❌ Error: Backend del Dashboard no encontrado." -ForegroundColor Red
}

# 3. Iniciar Soldado de Sincronización Live
Write-Host "• Enviando al Heraldo a sincronizar con GitHub..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList $SYNC_SOLDIER -WindowStyle Hidden -WorkingDirectory "$ORBE_ROOT\batallon"

# 4. Iniciar Cerebro en Segundo Plano (Modo Vigilancia)
Write-Host "- Despertando el Cerebro (Agenda y Latido)..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "$CEREBRO RUN" -WindowStyle Hidden -WorkingDirectory "$ORBE_ROOT\batallon"

Write-Host "`n[!] VERIX ESTA ONLINE Y SONANDO." -ForegroundColor Cyan
Write-Host "El Orbe es independiente ahora. Vigilancia de tareas activa." -ForegroundColor Gray
Write-Host "Dashbord Live: https://drxteren.github.io/Orbe-Dreams-Live/" -ForegroundColor Magenta
Write-Host "Repositorio Live: https://github.com/drxteren/Orbe-Evolution-Live" -ForegroundColor Magenta
