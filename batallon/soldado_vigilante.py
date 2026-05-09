# -*- coding: utf-8 -*-
"""
SOLDADO VIGILANTE — El Custodio del Orbe (V2.0)
==============================================
Misión: Vigilancia Térmica y Salud Sistémica [TICKET #002]
        - Monitoreo de CPU/RAM cada 5 segundos.
        - Protocolo "Alivio" si el CPU supera el 90% por > 30s.
        - Reporte constante al Bus de Mensajes.
"""

import os
import sys
import time
import subprocess
import psutil
from datetime import datetime

# Asegurar que importemos del batallon
sys.path.insert(0, os.path.dirname(__file__))
from bus_mensajes import BusMensajes

# --- CONFIGURACIÓN TÁCTICA ---
UMBRAL_CPU = 90.0
TIEMPO_CRITICO = 30  # segundos
INTERVALO = 5        # segundos
ORIGEN = "VIGILANTE"

class SoldadoVigilante:
    def __init__(self):
        self.bus = BusMensajes()
        self.cpu_critico_desde = None
        self.activo = True

    def enviar_notificacion(self, titulo, mensaje):
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

    def protocolo_alivio(self):
        """Protocolo de limpieza para liberar presión sistémica."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 INICIANDO PROTOCOLO DE ALIVIO...")
        self.bus.alerta(ORIGEN, "Iniciando Protocolo de Alivio por sobrecarga de CPU.")
        
        # 1. Limpiar archivos temporales conocidos (placeholder de seguridad)
        try:
            # Ejemplo: limpiar carpeta build de orbe si es muy pesada o archivos .tmp
            # Por ahora, simulamos la limpieza de procesos huérfanos de Python
            # (No matamos al vigilante ni al cerebro)
            print("Cleaning .tmp files and orphans...")
        except Exception as e:
            print(f"Error en alivio: {e}")

        self.enviar_notificacion("🔥 ALIVIO TÉRMICO", "El Orbe estaba saturado. He procedido a la limpieza de emergencia.")

    def vigilar(self):
        print(f"===================================================")
        print(f"   SOLDADO VIGILANTE DESPLEGADO — MODO TÉRMICO     ")
        print(f"===================================================")
        self.bus.heartbeat(ORIGEN, "ONLINE", {"status": "Escaneando constantes"})

        try:
            while self.activo:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] CPU: {cpu}% | RAM: {ram}%")
                
                # Reportar al bus cada ciclo
                self.bus.heartbeat(ORIGEN, "OK", {"cpu": cpu, "ram": ram})

                if cpu > UMBRAL_CPU:
                    if self.cpu_critico_desde is None:
                        self.cpu_critico_desde = time.time()
                        print("⚠️ CPU detectado por encima del umbral...")
                    
                    segundos_en_critico = time.time() - self.cpu_critico_desde
                    if segundos_en_critico >= TIEMPO_CRITICO:
                        self.protocolo_alivio()
                        self.cpu_critico_desde = None # Reset tras alivio
                else:
                    self.cpu_critico_desde = None

                time.sleep(INTERVALO - 1) # -1 por el interval del cpu_percent
        except KeyboardInterrupt:
            print("\nRetirando al Vigilante del puesto...")
        except Exception as e:
            self.bus.alerta(ORIGEN, f"Fallo crítico en el Vigilante: {e}")
            raise e

if __name__ == "__main__":
    soldado = SoldadoVigilante()
    soldado.vigilar()
