import os
import sys
import psutil
import socket
import subprocess
from datetime import datetime
import json

# Rutas del Santuario
SANTUARIO_RAIZ = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
DIRECTORIO_REGISTROS = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe")
LOG_ROOT = os.path.join(DIRECTORIO_REGISTROS, "root_god_mode.log")

def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def log_event(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(DIRECTORIO_REGISTROS, exist_ok=True)
    with open(LOG_ROOT, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

class GodMode:
    @staticmethod
    def check_system_health():
        health = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_free_gb": psutil.disk_usage('C:').free / (1024**3),
            "hostname": socket.gethostname(),
            "ip_local": socket.gethostbyname(socket.gethostname()),
            "timestamp": datetime.now().isoformat()
        }
        return health

    @staticmethod
    def protect_directory(path):
        """Aplica restricciones NTFS básicas usando icacls (solo admin)."""
        if not is_admin():
            return False, "Permisos insuficientes."
        
        try:
            # Usar SID S-1-5-32-544 (Administradores) para evitar problemas de idioma
            cmd = f'icacls "{path}" /inheritance:r /grant:r *S-1-5-32-544:(OI)(CI)F'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            log_event(f"Protección aplicada a: {path}", "SECURITY")
            return True, "Protección aplicada con éxito (SID: Administradores)."
        except Exception as e:
            log_event(f"Falla al proteger {path}: {str(e)}", "ERROR")
            return False, str(e)

    @staticmethod
    def flush_dns():
        if not is_admin(): return False
        subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
        log_event("DNS Flush ejecutado.", "NETWORK")
        return True

if __name__ == "__main__":
    if not is_admin():
        print("ERROR: Se requieren privilegios de Administrador para el Modo Dios.")
        sys.exit(1)
    
    print("⚡ VERIX GOD MODE CORE - ACTIVADO ⚡")
    health = GodMode.check_system_health()
    print(f"Salud del Sistema: {json.dumps(health, indent=2)}")
    log_event("God Mode Core iniciado por Richon.", "ROOT")
