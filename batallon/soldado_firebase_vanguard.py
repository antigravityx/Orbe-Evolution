import json
import os
import datetime

# --- CONFIGURACIÓN DEL SOLDADO ---
NOMBRE_SOLDADO = "FIREBASE_VANGUARD"
CONFIG_PATH = r"C:\Users\Usuario\Desktop\ente_eye\y\.firebaserc"
LOG_SANTUARIO = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt"

def informar_guardia(mensaje):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [SOLDADO: {NOMBRE_SOLDADO}] {mensaje}\n"
    with open(LOG_SANTUARIO, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(log_entry.strip())

def chequear_linea_vital():
    informar_guardia("Verificando conexión con el núcleo de mistercartamenu...")
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                project_id = config.get("projects", {}).get("default", "DESCONOCIDO")
                informar_guardia(f"Nexo Firebase detectado: {project_id}. Operativo.")
                return True
        except Exception as e:
            informar_guardia(f"Error al leer el nexo: {str(e)}")
            return False
    else:
        informar_guardia("¡URGENTE! Archivo .firebaserc no encontrado en la zona de combate.")
        return False

if __name__ == "__main__":
    informar_guardia("Soldado Firebase Vanguard desplegado. Protegiendo la nube.")
    chequear_linea_vital()
