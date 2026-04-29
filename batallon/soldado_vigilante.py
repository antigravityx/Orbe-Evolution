# -*- coding: utf-8 -*-
"""
SOLDADO VIGILANTE — El Custodio del Orbe
========================================
Misión: Vigilar constantemente al Sentinel de GitHub y asegurarse
        de que las credenciales (Alma de Verix) estén en perfecto estado.
        Si algo falla, lanza una notificación de escritorio a r1ch0n.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Asegurar que importemos del batallon
sys.path.insert(0, os.path.dirname(__file__))

def enviar_notificacion(titulo, mensaje):
    """Envía una notificación Toast nativa a Windows."""
    try:
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = "<toast><visual><binding template='ToastText02'><text id='1'>{titulo}</text><text id='2'>{mensaje}</text></binding></visual></toast>"
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Verix Orbe").Show($toast)
        """
        subprocess.run(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"Error al enviar notificación: {e}")

def vigilar_sentinel():
    try:
        from soldado_github_sentinel import GitHubSentinel
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 👁️ Vigilante: Revisando constantes vitales del Sentinel...")
        sentinel = GitHubSentinel()
        
        # Validar la identidad sin saturar la API
        info = sentinel.verificar_identidad()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Vigilante: Todo en orden. Identidad '{info.get('login')}' operando al 100%.")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Vigilante: ¡ALERTA! El Sentinel ha reportado un fallo.")
        print(f"Detalle: {error_msg}")
        enviar_notificacion("⚠️ Alerta del Orbe Verix", f"El Sentinel de GitHub perdió conexión o permisos. Revisa la consola.")
        return False

if __name__ == "__main__":
    print("===================================================")
    print("   SOLDADO VIGILANTE DESPLEGADO Y EN GUARDIA       ")
    print("===================================================")
    
    run_once = "--test" in sys.argv
    
    # Primera comprobación inmediata al iniciar
    if vigilar_sentinel():
        enviar_notificacion("🛡️ Orbe Verix: Vigilante Activo", "Sentinel GitHub está fuerte y con permisos plenos. Área asegurada.")
    
    if not run_once:
        while True:
            # Duerme 2 horas para no quemar la API de GitHub (7200 segs)
            time.sleep(7200)
            vigilar_sentinel()
