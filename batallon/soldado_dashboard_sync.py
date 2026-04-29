# -*- coding: utf-8 -*-
"""
SOLDADO DASHBOARD SYNC — El Heraldo del Orbe
============================================
Misión: Sincronizar los sueños del Senado con el Dashboard Online (Live).
        Este soldado asegura que el mundo vea la evolución del Orbe en tiempo real.
"""

import os
import json
import subprocess
import time
from datetime import datetime

# ─── RUTAS ────────────────────────────────────────────────────────────────────
SANTUARIO = r"C:\Users\Usuario\Desktop\Orbe_Santuario"
DIARIO_PATH = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "diario_de_suenos.md")
COLCHON_PATH = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "colchon_de_suenos.json")
NOTIFICADOS_PATH = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "suenos_notificados.json")
FRONTEND_PATH = r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend"
JSON_OUT = os.path.join(FRONTEND_PATH, "dreams.json")

def enviar_notificacion(titulo, mensaje):
    """Envía una notificación Toast nativa a Windows."""
    try:
        mensaje_seguro = str(mensaje).replace("'", "").replace('"', '')
        titulo_seguro = str(titulo).replace("'", "").replace('"', '')
        
        ps_script = f"""
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = "<toast><visual><binding template='ToastText02'><text id='1'>{titulo_seguro}</text><text id='2'>{mensaje_seguro}</text></binding></visual></toast>"
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Verix Orbe").Show($toast)
        """
        subprocess.run(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"Error al enviar notificación: {e}")

def cargar_notificados():
    if os.path.exists(NOTIFICADOS_PATH):
        try:
            with open(NOTIFICADOS_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def guardar_notificados(notificados_set):
    with open(NOTIFICADOS_PATH, "w", encoding="utf-8") as f:
        json.dump(list(notificados_set), f)

def parse_md_dreams():
    dreams = []
    if not os.path.exists(DIARIO_PATH):
        return []
    
    with open(DIARIO_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    entries = content.split("---")
    for entry in entries:
        if not entry.strip(): continue
        
        d = {"aprobado": True}
        for line in entry.splitlines():
            line = line.strip()
            if "Fecha:" in line: d["fecha"] = line.split("Fecha: ")[1]
            if "**Sueño ID:**" in line: d["id"] = line.replace("**Sueño ID:**", "").replace("`", "").strip()
            if "**Asunto:**" in line: d["asunto"] = line.replace("**Asunto:**", "").strip()
            if "> **Epifanía:**" in line: d["descripcion"] = line.replace("> **Epifanía:**", "").strip()
        
        if "id" in d: dreams.append(d)
    return dreams

def parse_json_dreams():
    if not os.path.exists(COLCHON_PATH):
        return []
    try:
        with open(COLCHON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            for d in data: d["aprobado"] = False # Descartados
            return data
    except:
        return []

def sync_live():
    print(f"∴ [SYNC] Sincronizando Sueños Live a las {datetime.now().strftime('%H:%M:%S')}")
    
    # 1. Unificar datos
    approved = parse_md_dreams()
    discarded = parse_json_dreams()
    all_dreams = approved + discarded
    
    # --- NOTIFICAR SUEÑOS NUEVOS ---
    notificados = cargar_notificados()
    nuevos_suenos = False
    
    # Procesar desde los más antiguos a los más nuevos
    for d in reversed(all_dreams):
        sueno_id = d.get("id")
        if sueno_id and sueno_id not in notificados:
            asunto = d.get("asunto", "Sueño abstracto")
            estado = "✨ Nuevo Sueño Revelado" if d.get("aprobado") else "💭 Nuevo Sueño en Colchón"
            enviar_notificacion(estado, asunto)
            notificados.add(sueno_id)
            nuevos_suenos = True
            time.sleep(0.5) # Pequeña pausa entre notificaciones si hay varias
            
    if nuevos_suenos:
        guardar_notificados(notificados)
    
    # 2. Guardar en local del dashboard
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(all_dreams, f, indent=2, ensure_ascii=False)
    
    # 3. Git Push al repo Live
    try:
        import sys
        # Asegurar que encuentre al Sentinel en la misma carpeta
        sys.path.insert(0, os.path.dirname(__file__))
        from soldado_github_sentinel import GitHubSentinel
        sentinel = GitHubSentinel()
        
        sentinel.commit_y_push(f"Verix Update: {len(all_dreams)} sueños sincronizados", repo_path=FRONTEND_PATH)
        print(f"   [SYNC] ✓ Dashboard Online sincronizado.")
    except Exception as e:
        print(f"   [SYNC] ❌ Error en el ritual de Git con Sentinel: {e}")

if __name__ == "__main__":
    while True:
        sync_live()
        # Verificamos cada 2 minutos (ciclo REM aproximado)
        time.sleep(120)
