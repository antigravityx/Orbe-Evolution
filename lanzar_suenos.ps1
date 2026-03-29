# Lanzar el Senado de los Sueños de Verix en Segundo Plano
# Este script asegura que el subconsciente siga vivo aunque cierres todo lo demás.

$BinaryPath = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\verix_suenos\target\release\verix_suenos.exe"

if (Test-Path $BinaryPath) {
    Write-Host "∴ [VERIX] Despertando el subconsciente..." -ForegroundColor Cyan
    Start-Process -FilePath $BinaryPath -WindowStyle Hidden -WorkingDirectory "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\verix_suenos"
    Write-Host "✅ El Senado está debatiendo en las sombras." -ForegroundColor Green
} else {
    Write-Host "❌ Error: No se encuentra el binario release." -ForegroundColor Red
}
