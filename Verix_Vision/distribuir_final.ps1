$sourceExe = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision\src-tauri\target\release\verix_vision.exe"
$explanationFile = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision\LEER_ANTES_DE_ABRIR.txt"

$desktopFolder = "c:\Users\Usuario\Desktop\Verix_Vision_App"
$orbeFolder = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Vision_App"
$tallerFolder = "c:\Users\Usuario\Desktop\Taller_Orbe_Verix\Verix_Vision_App"

Write-Host "Distribuyendo a las ubicaciones..."

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

Write-Host "Lanzando Verix Vision..."
Start-Process -FilePath "$desktopFolder\verix_vision.exe"

# Enviar Notificación Toast
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$template = "<toast><visual><binding template='ToastText02'><text id='1'>Orbe Autónomo</text><text id='2'>Verix Vision ha sido distribuido y lanzado exitosamente.</text></binding></visual></toast>"
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Verix Orbe").Show($toast)

Write-Host "Distribución y ejecución completadas."
