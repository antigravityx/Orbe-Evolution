# -*- coding: utf-8 -*-
"""
SISTEMA ORBE — BATALLÓN DE ÉLITE
Soldado: ELITE_DEPLOY_MINISTER (v1.0)
Misión: Gestión y blindaje de despliegues Cloud (Hostinger/FTP)

Este soldado es el único autorizado para abrir puentes de comunicación 
entre el Orbe local y los servidores de producción.
"""

import os
import sys
import json
import ftplib
import logging
from datetime import datetime

# ─── FIX ENCODING WINDOWS ────────────────────────────────────────────────────
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ─── PATH DEL ORBE ───────────────────────────────────────────────────────────
ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ORBE_ROOT)
from batallon.vault_soldier import VaultOrbe

# ─── CONFIGURACIÓN DE ÉLITE ──────────────────────────────────────────────────
NOMBRE_SOLDADO = "ELITE_DEPLOY_MINISTER"
LOG_PATH = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\deploy_log.jsonl"
MEMORIA_MADRE = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\memoria_madre.json"

class SoldadoEliteDespliegue:
    def __init__(self):
        self.vault = VaultOrbe()
        self.identidad = {
            "nombre": NOMBRE_SOLDADO,
            "rango": "Super Elite",
            "especialidad": "Cloud Infrastructure",
            "estado": "ACTIVO"
        }

    def registrar_evento(self, nivel, mensaje, extra=None):
        """Registro estructurado en el diario del Orbe"""
        evento = {
            "timestamp": datetime.now().isoformat(),
            "soldado": NOMBRE_SOLDADO,
            "nivel": nivel,
            "mensaje": mensaje,
            "extra": extra or {}
        }
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(evento, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error en log: {e}")
        print(f"[{nivel}] {mensaje}")

    def obtener_credenciales(self):
        """Recupera llaves maestras desde el Vault"""
        keys = {
            "host": "HOSTINGER_FTP_HOST",
            "user": "HOSTINGER_FTP_USER",
            "pass": "HOSTINGER_FTP_PASS"
        }
        creds = {}
        for label, vault_key in keys.items():
            val = self.vault.recuperar(vault_key)
            if not val:
                self.registrar_evento("CRITICO", f"Falta credencial {vault_key} en el Vault")
                return None
            creds[label] = val
        return creds

    def ejecutar_mision_naufrago(self, local_path):
        """
        Misión específica: Desplegar el sitio del Sombrerero Náufrago
        """
        self.registrar_evento("INFO", "Iniciando Misión de Despliegue: Sombrerero Náufrago")
        
        creds = self.obtener_credenciales()
        if not creds:
            return False

        try:
            print(f"[*] Abriendo túnel seguro hacia {creds['host']}...")
            ftp = ftplib.FTP(creds['host'])
            ftp.login(creds['user'], creds['pass'])
            ftp.encoding = 'utf-8'
            
            # Navegar a la raíz pública
            try:
                ftp.cwd("/public_html")
            except:
                pass

            archivos_subidos = self._subir_recursivo(ftp, local_path, ".")
            
            ftp.quit()
            
            self.registrar_evento("EXITO", "Misión cumplida", {
                "archivos": archivos_subidos,
                "destino": "sombrereronaufrago.com"
            })
            return True
            
        except Exception as e:
            self.registrar_evento("ERROR", f"Fallo en la misión: {str(e)}")
            return False

    def _subir_recursivo(self, ftp, local_dir, remote_dir):
        count = 0
        for item in os.listdir(local_dir):
            l_path = os.path.join(local_dir, item)
            r_path = f"{remote_dir}/{item}" if remote_dir != "." else item

            # Ignorar basura y scripts
            if item.startswith('.') or item == '__pycache__' or item.endswith('.py'):
                continue

            if os.path.isdir(l_path):
                try:
                    ftp.mkd(r_path)
                except:
                    pass
                count += self._subir_recursivo(ftp, l_path, r_path)
            else:
                with open(l_path, 'rb') as f:
                    ftp.storbinary(f'STOR {r_path}', f)
                    count += 1
                    print(f"  [+] {r_path}")
        return count

if __name__ == "__main__":
    soldado = SoldadoEliteDespliegue()
    
    if len(sys.argv) > 1 and sys.argv[1] == "DESPLEGAR_NAUFRAGO":
        ruta_sitio = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\GESTION_R1CH0N\sombrereronaufrago"
        if os.path.exists(ruta_sitio):
            soldado.ejecutar_mision_naufrago(ruta_sitio)
        else:
            soldado.registrar_evento("ERROR", "Ruta del sitio no encontrada")
    else:
        print(f"--- {NOMBRE_SOLDADO} ---")
        print("Esperando órdenes del Núcleo...")
