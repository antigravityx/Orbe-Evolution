import webbrowser
import os
import datetime
import sys

# --- CONFIGURACIÓN DEL SOLDADO ---
NOMBRE_SOLDADO = "VIVALDI_BRIDGE"
LOG_SANTUARIO = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt"

def informar_avistamiento(mensaje):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [SOLDADO: {NOMBRE_SOLDADO}] {mensaje}\n"
    try:
        with open(LOG_SANTUARIO, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(log_entry.strip())
    except Exception as e:
        print(f"Error al informar: {e}")

def abrir_en_vivaldi(url):
    informar_avistamiento(f"Abriendo portal seguro en Vivaldi: {url}")
    try:
        # Abre en el navegador predeterminado del sistema (Vivaldi segun r1ch0n)
        webbrowser.open(url)
        return True
    except Exception as e:
        informar_avistamiento(f"Error al abrir el portal: {str(e)}")
        return False

if __name__ == "__main__":
    informar_avistamiento("Soldado Vivaldi Bridge en posición. Custodiando sesiones de r1ch0n.")
    if len(sys.argv) > 1:
        url_destino = sys.argv[1]
        abrir_en_vivaldi(url_destino)
    else:
        informar_avistamiento("Esperando coordenadas (URL) para abrir el portal.")
