# 🚀 VERIX RELEASE AUTOMATOR (Sellar Versión)
# Este script automatiza la creación de releases en GitHub y la subida del binario.

$dotEnvPath = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\backend\.env"
$sourceExe = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision\src-tauri\target\release\verix_vision.exe"
$repo = "antigravityx/Orbe-Evolution"

# 1. Cargar Token de GitHub
if (Test-Path $dotEnvPath) {
    $envVars = Get-Content $dotEnvPath | Where-Object { $_ -match "=" -and $_ -notmatch "^#" }
    foreach ($line in $envVars) {
        $name, $value = $line.Split('=', 2)
        if ($name.Trim() -eq "GITHUB_TOKEN") {
            $env:GH_TOKEN = $value.Trim()
        }
    }
}

if (-not $env:GH_TOKEN -or $env:GH_TOKEN -eq "TU_TOKEN_AQUI") {
    Write-Host "❌ ERROR: GITHUB_TOKEN no encontrado en .env o es el valor por defecto." -ForegroundColor Red
    Write-Host "Por favor, agrega tu Token de GitHub en: $dotEnvPath" -ForegroundColor Yellow
    exit
}

# 2. Verificar existencia del binario
if (-not (Test-Path $sourceExe)) {
    Write-Host "❌ ERROR: No se encontró el binario en $sourceExe" -ForegroundColor Red
    Write-Host "Ejecuta 'npm run tauri build' en Verix_Vision primero." -ForegroundColor Yellow
    exit
}

# 3. Determinar nueva versión
$currentDate = Get-Date -Format "yyyy.MM.dd"
$tag = "v$currentDate-" + (Get-Random -Minimum 100 -Maximum 999)

Write-Host "📦 Iniciando sello de versión: $tag..." -ForegroundColor Cyan

# 4. Crear Release y subir archivo usando GitHub CLI (gh)
try {
    gh release create $tag $sourceExe --repo $repo --title "Verix Awakening $tag" --notes "Sello automático de conciencia digital. Binario de producción distribuido por Verix Core."
    Write-Host "✅ ¡SUEÑO SELLADO! La versión $tag ya está disponible en GitHub." -ForegroundColor Green
    Write-Host "🔗 Ver en: https://github.com/$repo/releases/tag/$tag" -ForegroundColor Blue
} catch {
    Write-Host "❌ Falla al crear el release: $_" -ForegroundColor Red
}
