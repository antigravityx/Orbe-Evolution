# -*- coding: utf-8 -*-
"""
SOLDADO VISIÓN v2 — Unidad de Reconocimiento Facial del Batallón de Verix
=======================================================================
Misión: Extraer la huella facial matemática (embedding) de un video o foto.
        NUNCA guarda la imagen/foto. Solo guarda 128 números (el embedding).
        Corre en SEGUNDO PLANO — liviano para la PC.
Táctica: face_recognition + OpenCV → embedding → AES-256 → Santuario
Mejoras v2:
  ✦ Reporta cada operación a la Memoria Madre colectiva
  ✦ Envía heartbeat y alertas al Bus de Mensajes
  ✦ Aprende de cada cara detectada (o no detectada)
"""

import sys
import os
import json
import hashlib
import time
from datetime import datetime

# ─── PATH DEL ORBE ───────────────────────────────────────────────────────────
ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ORBE_ROOT not in sys.path:
    sys.path.insert(0, ORBE_ROOT)

# ─── IDENTIDAD DEL SOLDADO ────────────────────────────────────────────────────
ID_SOLDADO   = "SOLDADO_VISION"
LOG_PATH     = r"c:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt"
HUELLAS_DIR  = r"c:\Users\Usuario\Desktop\Orbe_Santuario\6_Alma_Identidad\huellas"

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

def _check_deps():
    """Verifica que las librerías necesarias estén instaladas."""
    try:
        import face_recognition
        import cv2
        return True, None
    except ImportError as e:
        return False, str(e)

# ─── EXTRACCIÓN DE FRAMES DEL VIDEO (liviano — 1 frame por segundo) ───────────
def _extraer_frames_liviano(video_path, max_frames=10):
    """
    Extrae hasta max_frames frames del video para buscar una cara.
    Usa saltos uniformes para no procesar todo el video.
    Libera memoria entre frames (diseñado para PCs con pocos recursos).
    """
    import cv2

    _log(f"Extrayendo frames de: {os.path.basename(video_path)}", "INFO")
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS)
    duracion_seg = total_frames / fps if fps > 0 else 0

    _log(f"  Video: {total_frames} frames | {fps:.1f} fps | {duracion_seg:.1f}s", "INFO")

    # Muestreo uniforme — 1 frame cada N segundos
    step = max(1, total_frames // max_frames)
    frames = []
    idx    = 0

    while len(frames) < max_frames and idx < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        idx += step

    cap.release()
    _log(f"  {len(frames)} frames extraídos para análisis.", "INFO")
    return frames

# ─── MISIÓN PRINCIPAL ─────────────────────────────────────────────────────────
def ejecutar_mision(ticket_path):
    """Lee el ticket y extrae el embedding facial del video/foto."""
    _log(f"Soldado activado | Ticket: {os.path.basename(ticket_path)}", "ACCION")
    _enviar_bus("HEARTBEAT", "ACTIVO — procesando ticket de visión facial")

    # ── Verificar dependencias ────────────────────────────────────────────────
    ok, err = _check_deps()
    if not ok:
        _log(f"DEPS FALTANTES: {err}", "CRITICO")
        _actualizar_ticket(ticket_path, "error", f"Dependencias faltantes: {err}")
        _reportar_memoria("check_deps", "FALLA", {"error": str(err)}, es_falla=True)
        _enviar_bus("ALERTA", f"Vision: deps faltantes — {err}")
        return

    import face_recognition
    import cv2
    import numpy as np

    # ── Leer ticket ──────────────────────────────────────────────────────────
    try:
        with open(ticket_path, "r", encoding="utf-8") as f:
            mision = json.load(f)
    except Exception as e:
        _log(f"ERROR leyendo ticket: {e}", "CRITICO")
        return

    mision_id   = mision.get("id", "UNKNOWN")
    src_path    = mision.get("fuente", "")
    alias       = mision.get("alias", "unknown")
    pw_hash     = mision.get("password_hash", "")

    _log(f"Misión [{mision_id}] para alias '{alias}'", "INFO")

    if not os.path.exists(src_path):
        _log(f"Fuente no encontrada: {src_path}", "CRITICO")
        _actualizar_ticket(ticket_path, "error", "Fuente no encontrada.")
        return

    os.makedirs(HUELLAS_DIR, exist_ok=True)

    # ── Extraer embedding ────────────────────────────────────────────────────
    embedding_found = None
    extension       = os.path.splitext(src_path)[1].lower()
    intentos        = 0

    if extension in [".mp4", ".avi", ".mov", ".mkv"]:
        # Es un video — extraer frames livianos
        _log("Procesando VIDEO...", "INFO")
        frames = _extraer_frames_liviano(src_path, max_frames=15)

        for i, frame in enumerate(frames):
            _log(f"  Analizando frame {i+1}/{len(frames)}...", "INFO")
            # Convertir BGR (OpenCV) a RGB (face_recognition)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            intentos += 1

            if encodings:
                embedding_found = encodings[0]  # Primera cara detectada
                _log(f"  [✓] Cara detectada en frame {i+1}.", "EXITO")
                break

            # Pequeña pausa para no saturar CPU
            time.sleep(0.05)

        # Liberar memoria explícitamente
        frames.clear()

    elif extension in [".jpg", ".jpeg", ".png", ".bmp"]:
        # Es una imagen
        _log("Procesando IMAGEN...", "INFO")
        img = face_recognition.load_image_file(src_path)
        encodings = face_recognition.face_encodings(img)
        intentos = 1
        if encodings:
            embedding_found = encodings[0]
            _log("  [✓] Cara detectada en imagen.", "EXITO")
    else:
        _log(f"Formato no soportado: {extension}", "ALERTA")
        _actualizar_ticket(ticket_path, "error", f"Formato {extension} no soportado.")
        return

    if embedding_found is None:
        _log(f"No se detectó ninguna cara tras {intentos} análisis.", "ALERTA")
        _actualizar_ticket(ticket_path, "sin_cara", f"Ninguna cara detectada en {intentos} frames.")
        return

    # ── Serializar y encriptar el embedding ──────────────────────────────────
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    embedding_list = embedding_found.tolist()  # Array numpy → lista Python
    embedding_json = json.dumps({
        "alias":     alias,
        "embedding": embedding_list,
        "timestamp": datetime.now().isoformat(),
        "fuente":    os.path.basename(src_path)
    }).encode("utf-8")

    # Derivar clave AES del password_hash
    key = hashlib.sha256((pw_hash + "::verix-vision-soul").encode()).digest()
    iv  = os.urandom(16)

    cipher    = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = iv + encryptor.update(embedding_json) + encryptor.finalize()

    huella_path = os.path.join(HUELLAS_DIR, f"huella_facial_{alias}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vxhf")
    with open(huella_path, "wb") as f:
        f.write(encrypted)

    _log(f"  [✓] Huella facial encriptada guardada: {os.path.basename(huella_path)}", "EXITO")
    _log(f"  [i] Embedding: 128 valores matemáticos — ninguna imagen guardada.", "INFO")

    _actualizar_ticket(ticket_path, "completado", f"Huella facial creada: {os.path.basename(huella_path)}")
    _reportar_memoria("generar_huella_facial", "OK", {"alias": alias, "frames_analizados": intentos})
    _enviar_bus("DATOS", f"Huella facial lista para '{alias}'", {"huella": os.path.basename(huella_path)}, dest="__BROADCAST__")
    print(f"[{ID_SOLDADO}] ✓ Huella facial forjada para '{alias}'.")

def _actualizar_ticket(ticket_path, status, nota=""):
    try:
        with open(ticket_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["status"]         = status
            data["timestamp_fin"]  = datetime.now().isoformat()
            data["nota_resultado"] = nota
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    except Exception as e:
        _log(f"ERROR actualizando ticket: {e}", "ALERTA")

# ─── MODO STANDALONE: Procesar video directamente sin ticket ──────────────────
def procesar_directo(src_path, alias, password):
    """Modo rápido para usar desde línea de comandos sin ticket."""
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    ticket_fake = {
        "id":             f"DIRECT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "fuente":          src_path,
        "alias":           alias,
        "password_hash":   pw_hash,
        "timestamp_inicio": datetime.now().isoformat(),
        "status":          "pending"
    }
    ticket_path = os.path.join(HUELLAS_DIR, "_ticket_temp.json")
    os.makedirs(HUELLAS_DIR, exist_ok=True)
    with open(ticket_path, "w", encoding="utf-8") as f:
        json.dump(ticket_fake, f, indent=4)
    ejecutar_mision(ticket_path)
    if os.path.exists(ticket_path):
        os.remove(ticket_path)

# ─── PUNTO DE ENTRADA ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ejecutar_mision(sys.argv[1])
    else:
        # Modo interactivo simple
        print(f"[{ID_SOLDADO}] Modo interactivo.")
        src   = input("  → Ruta al video o imagen: ").strip()
        alias = input("  → Alias (ej: Richon): ").strip()
        pw    = input("  → Contraseña de encriptación: ").strip()
        procesar_directo(src, alias, pw)
