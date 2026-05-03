$startupFolder = [Environment]::GetFolderPath('Startup')
$shortcutPath = Join-Path -Path $startupFolder -ChildPath "Orbe_Verix_Inicio.lnk"
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Al_Infinito.ps1`""
$Shortcut.WorkingDirectory = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
$Shortcut.Save()
Write-Host "Acceso directo de inicio creado en: $shortcutPath"
