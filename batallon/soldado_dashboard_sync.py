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
FRONTEND_PATH = r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend"
JSON_OUT = os.path.join(FRONTEND_PATH, "dreams.json")

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
    
    # 2. Guardar en local del dashboard
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(all_dreams, f, indent=2, ensure_ascii=False)
    
    # 3. Git Push al repo Live
    try:
        subprocess.run(["git", "add", "dreams.json"], cwd=FRONTEND_PATH)
        res = subprocess.run(["git", "commit", "-m", f"Verix Update: {len(all_dreams)} sueños sincronizados"], cwd=FRONTEND_PATH, capture_output=True)
        if b"nothing to commit" in res.stdout:
            print("   [SYNC] Sin cambios nuevos en el Dashboard.")
            return

        subprocess.run(["git", "push", "origin", "main"], cwd=FRONTEND_PATH)
        print(f"   [SYNC] ✓ Dashboard Online actualizado con {len(all_dreams)} sueños.")
    except Exception as e:
        print(f"   [SYNC] ❌ Error en el ritual de Git: {e}")

if __name__ == "__main__":
    while True:
        sync_live()
        # Verificamos cada 2 minutos (ciclo REM aproximado)
        time.sleep(120)
