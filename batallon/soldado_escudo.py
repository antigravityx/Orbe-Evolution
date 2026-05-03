# -*- coding: utf-8 -*-
"""
SOLDADO ESCUDO — El Purificador del Santuario
=====================================================
Misión: Eliminar rastros digitales, rotar logs y mantener 
el anonimato operativo del Orbe.

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import glob
import time
from datetime import datetime, timedelta
from batallon.memoria_madre import con_memoria

# Rutas
SANTUARIO = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
REGISTROS_DIR = os.path.join(SANTUARIO, "4_Registros_Del_Orbe")
MAX_LINEAS_LOG = 100 # Opción B Táctica: Conservar solo la memoria reciente
HORAS_EXPIRACION = 24

class EscudoSantuario:
    
    def _log_local(self, msg: str):
        print(f"[ESCUDO] {msg}")

    def _rotar_logs(self):
        """Mantiene solo las últimas 100 líneas de los archivos .log y .jsonl"""
        self._log_local("Iniciando purga táctica de logs (Max 100 líneas)...")
        patrones = ["*.log", "*.jsonl"]
        archivos = []
        for pat in patrones:
            archivos.extend(glob.glob(os.path.join(REGISTROS_DIR, pat)))
            
        for archivo in archivos:
            try:
                with open(archivo, "r", encoding="utf-8", errors="ignore") as f:
                    lineas = f.readlines()
                
                if len(lineas) > MAX_LINEAS_LOG:
                    recientes = lineas[-MAX_LINEAS_LOG:]
                    with open(archivo, "w", encoding="utf-8") as f:
                        f.writelines(recientes)
                    self._log_local(f"Purificado: {os.path.basename(archivo)} (reducido de {len(lineas)} a {MAX_LINEAS_LOG} líneas)")
            except Exception as e:
                self._log_local(f"Error rotando {os.path.basename(archivo)}: {e}")

    def _limpiar_tickets_viejos(self):
        """Elimina archivos de tickets viejos (> 24h)"""
        self._log_local("Iniciando barrido de tickets residuales...")
        patrones = ["ticket_*.json"]
        archivos = []
        for pat in patrones:
            archivos.extend(glob.glob(os.path.join(REGISTROS_DIR, pat)))
            
        ahora = time.time()
        for archivo in archivos:
            try:
                tiempo_mod = os.path.getmtime(archivo)
                horas_antiguedad = (ahora - tiempo_mod) / 3600
                
                if horas_antiguedad > HORAS_EXPIRACION:
                    os.remove(archivo)
                    self._log_local(f"Incinerado: {os.path.basename(archivo)} ({horas_antiguedad:.1f}h de antigüedad)")
            except Exception as e:
                self._log_local(f"Error eliminando {os.path.basename(archivo)}: {e}")

    @con_memoria("ESCUDO")
    def ejecutar_limpieza(self):
        """Realiza todas las labores de purificación."""
        self._log_local("Activado. Asegurando perímetro digital.")
        self._limpiar_tickets_viejos()
        self._rotar_logs()
        self._log_local("Perímetro asegurado. Rastros borrados.")
        return {"resultado": "ok"}

if __name__ == "__main__":
    print("\n==========================================")
    print("   SOLDADO ESCUDO — Purificador Orbe")
    print("==========================================\n")
    escudo = EscudoSantuario()
    escudo.ejecutar_limpieza()
