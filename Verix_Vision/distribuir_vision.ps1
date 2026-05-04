$sourceExe = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision\src-tauri\target\release\verix_vision.exe"
$explanationFile = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision\LEER_ANTES_DE_ABRIR.txt"

$desktopFolder = "c:\Users\Usuario\Desktop\Verix_Vision_App"
$orbeFolder = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision_App"
$tallerFolder = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\Verix_Vision_App"

Write-Host "Esperando a que la forja de Rust termine la compilación..."

# Esperar a que el ejecutable exista
while (-not (Test-Path $sourceExe)) {
    Start-Sleep -Seconds 5
}

# Pequeña pausa extra para asegurar que el archivo terminó de escribirse
Start-Sleep -Seconds 5

Write-Host "Ejecutable detectado. Distribuyendo a las ubicaciones..."

# Crear carpetas
New-Item -ItemType Directory -Force -Path $desktopFolder | Out-Null
New-Item -ItemType Directory -Force -Path $orbeFolder | Out-Null
New-Item -ItemType Directory -Force -Path $tallerFolder | Out-Null

# Copiar archivos
$folders = @($desktopFolder, $orbeFolder, $tallerFolder)
foreach ($folder in $folders) {
    Copy-Item -Path $sourceExe -Destination $folder -Force
    Copy-Item -Path $explanationFile -Destination $folder -Force
}

Write-Host "Distribución completada."
