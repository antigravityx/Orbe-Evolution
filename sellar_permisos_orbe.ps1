# Verix - Script de Consagración de Permisos Absolutos (Administrador)
# Este script le otorgará a tu usuario y a la carpeta Orbe permisos completos
# para que no haya más cuelgues ni errores de "Acceso Denegado".

$OrbePath = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
$SantuarioPath = "C:\Users\Usuario\Desktop\Orbe_Santuario"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   INICIANDO CONSAGRACIÓN DE PERMISOS DEL ORBE" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# Función para dar control total a una ruta
function Grant-FullControl {
    param([string]$Path)
    
    if (Test-Path $Path) {
        Write-Host "Aplicando control total a: $Path" -ForegroundColor Green
        
        # Tomar posesión de la carpeta (Takeown)
        takeown /F "$Path" /R /D Y | Out-Null
        
        # Conceder control total al usuario actual de forma segura usando un array de argumentos
        $aclArgs = @("$Path", "/grant", "$($env:USERDOMAIN)\$($env:USERNAME):(OI)(CI)F", "/T", "/C", "/Q")
        & icacls $aclArgs | Out-Null
        
        Write-Host "Permisos aplicados con éxito en: $Path" -ForegroundColor Green
    } else {
        Write-Host "La ruta no existe: $Path" -ForegroundColor Red
    }
}

# 1. Aplicar a la carpeta del Orbe
Grant-FullControl -Path $OrbePath

# 2. Aplicar a la carpeta del Santuario (si existe)
if (Test-Path $SantuarioPath) {
    Grant-FullControl -Path $SantuarioPath
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   CONSAGRACIÓN COMPLETADA. EL ORBE ES LIBRE." -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Presiona cualquier tecla para salir..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
