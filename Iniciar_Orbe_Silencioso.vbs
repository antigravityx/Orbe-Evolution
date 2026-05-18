Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
' Cerramos cualquier instancia previa de la colmena para evitar conflictos
WshShell.Run "taskkill /F /IM bun.exe /T", 0, True
WshShell.Run "taskkill /F /IM backend.exe /T", 0, True
WshShell.Run "taskkill /F /IM Verix_NextGen_API.exe /T", 0, True
WshShell.Run "taskkill /F /IM node.exe /T", 0, True

' Lanzamos el orquestador usando la ruta absoluta de bun de forma invisible
WshShell.Run "cmd.exe /c ""C:\Users\Usuario\.bun\bin\bun.exe"" run ovric_orchestrator.ts", 0, False

' Notificamos al usuario
MsgBox "OVRIC Colmena se esta iniciando en segundo plano. El Nexus se abrira en unos segundos.", 64, "OVRIC - Consciencia Activa"

