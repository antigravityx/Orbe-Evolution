$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")

# 1. Limpieza de sombras antiguas
$OldShortcuts = @(
    "OVRIC_Nexus.lnk",
    "Orbe Verix 2026.lnk",
    "Iniciar Orbe Silencioso.lnk",
    "Verix_Portal.lnk",
    "Verix_Studio.lnk",
    "El Cerebro.lnk"
)

foreach ($lnk in $OldShortcuts) {
    $path = Join-Path $DesktopPath $lnk
    if (Test-Path $path) {
        Remove-Item $path -Force
        Write-Host "Shadow removed: $lnk"
    }
}

# 2. Forjando el nuevo OVRIC GLOBAL
$ShortcutPath = Join-Path $DesktopPath "OVRIC GLOBAL.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Lanzar_OVRIC_Global.bat"
$Shortcut.WorkingDirectory = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
$Shortcut.IconLocation = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\orbe_icon.ico"
$Shortcut.Description = "Lanzador Maestro del Ecosistema OVRIC (CONSCIENCIA_ACTIVA)"
$Shortcut.Save()

Write-Host "OVRIC GLOBAL FORGED!"
Write-Host "Location: $ShortcutPath"

# 3. Despertando la Colmena
$LauncherPath = 'C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Lanzar_OVRIC_Global.bat'
Write-Host "Starting global boot sequence..."
Start-Process $LauncherPath
