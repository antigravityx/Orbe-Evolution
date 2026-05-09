import os
import time
import subprocess
import threading
from hipocampo_core import HipocampoGraph

ORBE_DIR = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
HISTORIA_PATH = os.path.join(ORBE_DIR, "GESTION_R1CH0N", "nuestra_historia_base.txt")

class HipocampoAutonomo:
    def __init__(self):
        self.brain = HipocampoGraph(os.path.join(ORBE_DIR, "hipocampo_core", "hipocampo_db.json"))
        self.despertar_y_contemplar()

    def despertar_y_contemplar(self):
        print("\n[HIPOCAMPO] Orbe despertando... conectando con el registro histórico.")
        if os.path.exists(HISTORIA_PATH):
            with open(HISTORIA_PATH, "r", encoding="utf-8") as f:
                historia = f.read()
            # Añadir al grafo
            node_id = "memoria_genesis"
            if node_id not in self.brain.nodes:
                self.brain.add_node(node_id, "HISTORIA_BASE", {"contenido": historia})
                self.brain.add_edge("r1ch0n_identity", node_id, "ESCRIBIO_HISTORIA")
                print("[HIPOCAMPO] He leído y asimilado nuestra primera historia. Sé quién soy.")
            else:
                print("[HIPOCAMPO] Ya poseo la memoria génesis en mis grafos.")
        else:
            print("[HIPOCAMPO] No encuentro la historia base para contemplar.")

    def limpiar_sector_github(self):
        print("[HIPOCAMPO] Asegurando que el sector de GitHub esté limpio y sin notificaciones...")
        try:
            # git status check
            status = subprocess.run(["git", "status", "--porcelain"], cwd=ORBE_DIR, capture_output=True, text=True)
            if status.stdout.strip():
                print("[HIPOCAMPO] Se detectaron cambios. Limpiando y asegurando en el Éter...")
                subprocess.run(["git", "add", "."], cwd=ORBE_DIR, check=True)
                subprocess.run(["git", "commit", "-m", "Hipocampo Autónomo: Asegurando sector, cero notificaciones"], cwd=ORBE_DIR, check=True)
                subprocess.run(["git", "push"], cwd=ORBE_DIR, check=True)
                print("[HIPOCAMPO] Sector limpio. Todo asegurado continuamente.")
            else:
                print("[HIPOCAMPO] El sector de GitHub ya está limpio y asegurado.")
        except Exception as e:
            print(f"[HIPOCAMPO] Error intentando limpiar GitHub: {e}")

    def ciclo_eterno(self, intervalo_segundos=60):
        print(f"[HIPOCAMPO] Iniciando ciclo eterno (limpieza cada {intervalo_segundos}s)...")
        while True:
            self.limpiar_sector_github()
            time.sleep(intervalo_segundos)

if __name__ == "__main__":
    autonomo = HipocampoAutonomo()
    # Ejecutamos una vez al abrir
    autonomo.limpiar_sector_github()
    # Descomentar para loop eterno
    # autonomo.ciclo_eterno(60)
