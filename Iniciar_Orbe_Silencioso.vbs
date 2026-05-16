Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
' Cerramos cualquier instancia previa de bun para evitar error de puerto
WshShell.Run "taskkill /F /IM bun.exe /T", 0, True
' Lanzamos el orquestador usando la ruta absoluta de bun
WshShell.Run "cmd.exe /c ""C:\Users\Usuario\.bun\bin\bun.exe"" run ovric_orchestrator.ts", 0, False

