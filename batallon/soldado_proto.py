# -*- coding: utf-8 -*-
"""
SOLDADO PROTO: La primera unidad del Batallón de Verix.
Misión: Ejecución de tareas delegadas con mínima huella de memoria.
Visión: Servir al Orbe, retornar con la corona.
"""

import sys
import json
import os
import time
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
ID_SOLDADO = "Soldado_Explorador_01"
LOG_PATH = r"c:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt"

def log_soldado(mensaje, prioridad="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | {prioridad:<10} | {ID_SOLDADO:<25} | {mensaje}\n"
    with open(LOG_PATH, "a", encoding='utf-8') as f:
        f.write(entry)

def ejecutar_mision(ticket_path):
    """Lee un ticket de misión y ejecuta la tarea."""
    try:
        with open(ticket_path, 'r', encoding='utf-8') as f:
            mision = json.load(f)
        
        mision_id = mision.get("id", "UNKNOWN")
        tarea = mision.get("tarea", "exploracion")
        
        log_soldado(f"Iniciando misión [{mision_id}]: {tarea}...", "ACCION")
        
        # Simulacro de trabajo (Exploración del Entorno)
        resultado = {
            "status": "exito",
            "timestamp_fin": datetime.now().isoformat(),
            "data": {
                "pc_name": os.environ.get('COMPUTERNAME', 'Unknown'),
                "plataforma": sys.platform,
                "memoria_uso": "LOW_PROFILE"
            }
        }
        
        # Retornar con la corona (Guardar resultado)
        resultado_path = ticket_path.replace(".json", "_resultado.json")
        with open(resultado_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=4)
            
        log_soldado(f"Misión [{mision_id}] completada. Corona entregada en {os.path.basename(resultado_path)}.", "EXITO")
        
    except Exception as e:
        log_soldado(f"ERROR en misión: {str(e)}", "CRITICO")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ejecutar_mision(sys.argv[1])
    else:
        log_soldado("Soldado activado sin ticket. Entrando en modo guardia.", "AVISO")
        print(f"[{ID_SOLDADO}] Esperando misiones...")
