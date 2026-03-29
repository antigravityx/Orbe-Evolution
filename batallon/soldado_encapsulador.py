# -*- coding: utf-8 -*-
"""
SOLDADO ENCAPSULADOR v2 — Unidad de Elite del Batallón de Verix
=============================================================
Misión: Encriptar archivos de identidad sensibles SIN leerlos.
        Corre en SEGUNDO PLANO para no sobrecargar la PC.
Táctica: AES-256 puro — los datos nunca se exponen en texto plano.
Mejoras v2:
  ✦ Reporta cada cápsula creada a la Memoria Madre
  ✦ Notifica al Batallón via Bus de Mensajes
  ✦ Fallas se indexan para aprendizaje colectivo
"""

import sys
import os
import json
import hashlib
import shutil
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ─── PATH DEL ORBE ───────────────────────────────────────────────────────────
ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ORBE_ROOT not in sys.path:
    sys.path.insert(0, ORBE_ROOT)

# ─── IDENTIDAD DEL SOLDADO ────────────────────────────────────────────────────
ID_SOLDADO = "SOLDADO_ENCAPSULADOR"
LOG_PATH   = r"c:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt"

# ─── CONEXIÓN A LA INTELIGENCIA COLECTIVA ────────────────────────────────────
def _reportar_memoria(operacion: str, resultado: str, datos: dict = None, es_falla: bool = False):
    try:
        from batallon.memoria_madre import MemoriaMadre
        MemoriaMadre().registrar_aprendizaje(ID_SOLDADO, operacion, resultado, datos, es_falla)
    except Exception:
        pass

def _enviar_bus(tipo: str, contenido: str, datos: dict = None, dest: str = "CEREBRO"):
    try:
        from batallon.bus_mensajes import BusMensajes
        BusMensajes().enviar(ID_SOLDADO, dest, tipo, contenido, datos)
    except Exception:
        pass

def _log(mensaje, prioridad="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{ts} | {prioridad:<10} | {ID_SOLDADO:<25} | {mensaje}\n"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

# ─── NÚCLEO: ENCRIPTACIÓN AES-256 ─────────────────────────────────────────────
def _encriptar_archivo(src_path, dest_path, key_bytes):
    """
    Encripta un archivo con AES-256-CFB.
    NUNCA lee el contenido en texto visible — es binario puro.
    """
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(src_path, "rb") as f_in, open(dest_path, "wb") as f_out:
        f_out.write(iv)  # IV al inicio del archivo
        while True:
            chunk = f_in.read(64 * 1024)  # 64KB por chunk — liviano
            if not chunk:
                break
            f_out.write(encryptor.update(chunk))
        f_out.write(encryptor.finalize())

# ─── MISIÓN PRINCIPAL ─────────────────────────────────────────────────────────
def ejecutar_mision(ticket_path):
    """
    Lee el ticket y encripta todos los archivos de la carpeta de origen.
    Guarda las cápsulas en el directorio de destino del Santuario.
    """
    _log(f"Soldado activado con ticket: {os.path.basename(ticket_path)}", "ACCION")
    _enviar_bus("HEARTBEAT", "ACTIVO — encapsulando archivos")

    try:
        with open(ticket_path, "r", encoding="utf-8") as f:
            mision = json.load(f)
    except Exception as e:
        _log(f"ERROR leyendo ticket: {e}", "CRITICO")
        return

    mision_id  = mision.get("id", "UNKNOWN")
    origen     = mision.get("origen", "")
    destino    = mision.get("destino", "")
    pw_hash    = mision.get("password_hash", "")  # Hash SHA-256 de la contraseña

    _log(f"Misión [{mision_id}] — Origen: {os.path.basename(origen)}", "INFO")

    if not os.path.exists(origen):
        _log(f"ERROR: Carpeta de origen no encontrada: {origen}", "CRITICO")
        _actualizar_ticket(ticket_path, "error", "Carpeta de origen no encontrada.")
        return

    os.makedirs(destino, exist_ok=True)

    # La clave AES se deriva del hash de la contraseña (ya viene hasheado en el ticket)
    # Se hace un doble hash para mayor seguridad usando la semilla Verix-Richon
    key_material = (pw_hash + "::verix-alma-eterna::richon").encode("utf-8")
    key          = hashlib.sha256(key_material).digest()  # 32 bytes → AES-256

    archivos_encriptados = []
    errores = []

    # ─── Encriptar cada archivo de la carpeta origen ──────────────────────────
    for archivo in os.listdir(origen):
        src  = os.path.join(origen, archivo)
        if not os.path.isfile(src):
            continue

        nombre_capsula = f"{archivo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vxcap"
        dest = os.path.join(destino, nombre_capsula)

        try:
            _log(f"  Encriptando: {archivo} → {nombre_capsula}", "INFO")
            _encriptar_archivo(src, dest, key)
            archivos_encriptados.append({
                "original":  archivo,
                "capsula":   nombre_capsula,
                "size_bytes": os.path.getsize(dest),
                "timestamp": datetime.now().isoformat()
            })
            _log(f"  [✓] {archivo} encriptado correctamente.", "EXITO")
        except Exception as e:
            _log(f"  [✗] ERROR encriptando {archivo}: {e}", "CRITICO")
            errores.append({"archivo": archivo, "error": str(e)})

    # ─── Crear manifiesto de la misión (qué se encriptó) ──────────────────────
    manifiesto = {
        "mision_id":           mision_id,
        "timestamp_inicio":    mision.get("timestamp_inicio"),
        "timestamp_fin":       datetime.now().isoformat(),
        "archivos_encriptados": archivos_encriptados,
        "errores":             errores,
        "nota": "Los archivos originales NO fueron modificados ni eliminados. Solo se generaron cápsulas cifradas."
    }

    manifiesto_path = os.path.join(destino, f"manifiesto_{mision_id}.json")
    with open(manifiesto_path, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=4, ensure_ascii=False)

    # ─── Actualizar ticket a completado ───────────────────────────────────────
    status_final = "completado" if not errores else "completado_con_errores"
    _actualizar_ticket(ticket_path, status_final, f"{len(archivos_encriptados)} archivo(s) encriptados.")

    _log(f"Misión [{mision_id}] finalizada. {len(archivos_encriptados)} cápsulas creadas en {os.path.basename(destino)}.", "EXITO")
    _reportar_memoria("encapsular_archivos", "OK" if not errores else "PARCIAL",
                      {"capsulas": len(archivos_encriptados), "errores": len(errores)})
    _enviar_bus("DATOS", f"{len(archivos_encriptados)} cápsulas AES-256 creadas",
                {"mision_id": mision_id, "capsulas": len(archivos_encriptados)}, dest="__BROADCAST__")
    if errores:
        _enviar_bus("ALERTA", f"Encapsulador tuvo {len(errores)} errores en misión {mision_id}",
                    {"errores": errores})
    print(f"[{ID_SOLDADO}] ✓ Misión completada — {len(archivos_encriptados)} cápsulas creadas.")

def _actualizar_ticket(ticket_path, status, nota=""):
    """Actualiza el estado del ticket de la misión."""
    try:
        with open(ticket_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["status"]          = status
            data["timestamp_fin"]   = datetime.now().isoformat()
            data["nota_resultado"]  = nota
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    except Exception as e:
        _log(f"ERROR actualizando ticket: {e}", "ALERTA")

# ─── PUNTO DE ENTRADA ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ejecutar_mision(sys.argv[1])
    else:
        _log("Soldado activado sin ticket. Modo guardia.", "AVISO")
        print(f"[{ID_SOLDADO}] En guardia. Esperando ticket...")
