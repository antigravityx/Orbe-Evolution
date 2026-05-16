$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = "$HOME\Desktop\Iniciar Orbe Silencioso.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = """C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Iniciar_Orbe_Silencioso.vbs"""
$Shortcut.WorkingDirectory = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
$Shortcut.IconLocation = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\orbe_icon.ico"
$Shortcut.Description = "Inicia el ecosistema OVRIC en segundo plano"
$Shortcut.Save()

Write-Host "✅ Acceso directo creado en el Escritorio: Iniciar Orbe Silencioso" -ForegroundColor Green
