# -*- coding: utf-8 -*-
"""
SOLDADO OIDO v2 — Unidad de Reconocimiento de Voz del Batallón de Verix
======================================================================
Misión: Extraer audio del video y generar una huella de voz encriptada.
        NUNCA guarda el audio en texto. Solo la huella matemática.
        Corre en SEGUNDO PLANO — liviano para la PC.
Táctica: moviepy → audio → SpeechRecognition → transcripción → AES-256
Mejoras v2:
  ✦ Reporta cada operación a la Memoria Madre colectiva
  ✦ Envía heartbeat y alertas al Bus de Mensajes
  ✦ Fallas se comparten con el Batallón para aprendizaje global
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
ID_SOLDADO  = "SOLDADO_OIDO"
LOG_PATH    = r"c:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt"
HUELLAS_DIR = r"c:\Users\Usuario\Desktop\Orbe_Santuario\6_Alma_Identidad\huellas"
TEMP_DIR    = r"c:\Users\Usuario\Desktop\Orbe_Santuario\6_Alma_Identidad\.tmp"

# ─── CONEXIÓN A LA INTELIGENCIA COLECTIVA ────────────────────────────────────
def _reportar_memoria(operacion: str, resultado: str, datos: dict = None, es_falla: bool = False):
    """Deposita el aprendizaje en la Memoria Madre."""
    try:
        from batallon.memoria_madre import MemoriaMadre
        MemoriaMadre().registrar_aprendizaje(ID_SOLDADO, operacion, resultado, datos, es_falla)
    except Exception:
        pass  # La memoria no debe bloquear la misión

def _enviar_bus(tipo: str, contenido: str, datos: dict = None, dest: str = "CEREBRO"):
    """Envía mensaje al Bus inter-soldado."""
    try:
        from batallon.bus_mensajes import BusMensajes
        BusMensajes().enviar(ID_SOLDADO, dest, tipo, contenido, datos)
    except Exception:
        pass  # El bus no debe bloquear la misión

def _log(mensaje, prioridad="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{ts} | {prioridad:<10} | {ID_SOLDADO:<25} | {mensaje}\n"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

def _check_deps():
    """Verifica las dependencias necesarias."""
    missing = []
    try:
        import moviepy
    except ImportError:
        missing.append("moviepy")
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")
    return (len(missing) == 0), missing

# ─── EXTRACCIÓN DE AUDIO (solo primeros N segundos para ser liviano) ───────────
def _extraer_audio_temp(video_path, duracion_max=30):
    """
    Extrae los primeros N segundos de audio del video.
    Guarda en TEMP como .wav temporal — se borra al final.
    No carga el video completo en RAM.
    """
    from moviepy import VideoFileClip

    _log(f"Extrayendo audio de: {os.path.basename(video_path)}", "INFO")
    os.makedirs(TEMP_DIR, exist_ok=True)
    temp_wav = os.path.join(TEMP_DIR, f"_temp_audio_{int(time.time())}.wav")

    try:
        clip = VideoFileClip(video_path)
        duracion = min(clip.duration, duracion_max)
        _log(f"  Duración total: {clip.duration:.1f}s | Procesando: {duracion:.1f}s", "INFO")

        # Extraer solo el segmento necesario
        subclip = clip.subclipped(0, duracion)
        subclip.audio.write_audiofile(
            temp_wav,
            fps=16000,       # 16kHz — suficiente para reconocimiento de voz
            nbytes=2,        # 16-bit
            codec="pcm_s16le",
            logger=None      # Sin spam de logs
        )
        clip.close()
        subclip.close()
        _log(f"  [✓] Audio temporal creado: {os.path.basename(temp_wav)}", "INFO")
        return temp_wav
    except Exception as e:
        _log(f"  ERROR extrayendo audio: {e}", "CRITICO")
        return None

# ─── TRANSCRIPCIÓN (generación de huella de contenido vocal) ─────────────────
def _transcribir_audio(wav_path):
    """
    Intenta transcribir el audio localmente (sin internet) via Sphinx,
    o genera una huella basada en las características del archivo.
    Lo que importa es la huella, no el texto exacto.
    """
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        # Intentar transcripción local (offline)
        try:
            texto = recognizer.recognize_sphinx(audio_data)
            _log("  [✓] Transcripción offline completada.", "EXITO")
            return texto, "sphinx"
        except Exception:
            pass

        # Fallback: huella basada en energy del audio
        _log("  [i] Offline recognition no disponible. Usando huella de energía.", "INFO")
        import numpy as np
        raw = audio_data.get_raw_data()
        # Huella de energía spectral — único por voz
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
        energy  = float(np.sqrt(np.mean(samples**2)))
        rms     = float(np.max(np.abs(samples)))
        huella_str = f"energy:{energy:.4f}|rms:{rms:.4f}|len:{len(raw)}"
        _log(f"  [✓] Huella de energía calculada.", "INFO")
        return huella_str, "energy_fingerprint"

    except Exception as e:
        _log(f"  ERROR en transcripción: {e}", "ALERTA")
        # Última salvaguarda: hash del archivo de audio raw
        with open(wav_path, "rb") as f:
            raw_hash = hashlib.sha256(f.read()).hexdigest()
        return f"audio_hash:{raw_hash}", "raw_hash"

# ─── MISIÓN PRINCIPAL ─────────────────────────────────────────────────────────
def ejecutar_mision(ticket_path):
    """Lee el ticket y genera la huella de voz encriptada."""
    _log(f"Soldado activado | Ticket: {os.path.basename(ticket_path)}", "ACCION")
    _enviar_bus("HEARTBEAT", "ACTIVO — procesando ticket de voz")

    ok, faltantes = _check_deps()
    if not ok:
        _log(f"DEPS FALTANTES: {faltantes}", "CRITICO")
        _actualizar_ticket(ticket_path, "error", f"Dependencias faltantes: {faltantes}")
        _reportar_memoria("check_deps", "FALLA", {"faltantes": faltantes}, es_falla=True)
        _enviar_bus("ALERTA", f"Dependencias faltantes: {faltantes}", dest="CEREBRO")
        return

    try:
        with open(ticket_path, "r", encoding="utf-8") as f:
            mision = json.load(f)
    except Exception as e:
        _log(f"ERROR leyendo ticket: {e}", "CRITICO")
        return

    mision_id = mision.get("id", "UNKNOWN")
    src_path  = mision.get("fuente", "")
    alias     = mision.get("alias", "unknown")
    pw_hash   = mision.get("password_hash", "")

    _log(f"Misión [{mision_id}] para alias '{alias}'", "INFO")

    if not os.path.exists(src_path):
        _log(f"Fuente no encontrada: {src_path}", "CRITICO")
        _actualizar_ticket(ticket_path, "error", "Fuente no encontrada.")
        return

    os.makedirs(HUELLAS_DIR, exist_ok=True)

    # ── 1. Extraer audio del video ────────────────────────────────────────────
    temp_wav = _extraer_audio_temp(src_path, duracion_max=30)
    if not temp_wav:
        _actualizar_ticket(ticket_path, "error", "No se pudo extraer el audio.")
        return

    # ── 2. Transcribir / generar huella de voz ───────────────────────────────
    contenido_voz, metodo = _transcribir_audio(temp_wav)

    # ── 3. Limpiar temp de audio (borrar el .wav temporal) ───────────────────
    try:
        os.remove(temp_wav)
        _log("  [✓] Audio temporal eliminado.", "INFO")
    except Exception:
        pass

    # ── 4. Encriptar la huella de voz ────────────────────────────────────────
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    datos_huella = json.dumps({
        "alias":         alias,
        "huella_voz":    contenido_voz,
        "metodo":        metodo,
        "timestamp":     datetime.now().isoformat(),
        "fuente":        os.path.basename(src_path)
    }).encode("utf-8")

    key = hashlib.sha256((pw_hash + "::verix-oido-soul").encode()).digest()
    iv  = os.urandom(16)

    cipher    = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = iv + encryptor.update(datos_huella) + encryptor.finalize()

    huella_path = os.path.join(HUELLAS_DIR, f"huella_voz_{alias}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vxhv")
    with open(huella_path, "wb") as f:
        f.write(encrypted)

    _log(f"  [✓] Huella de voz encriptada: {os.path.basename(huella_path)}", "EXITO")
    _log(f"  [i] Método: {metodo} | Datos de audio eliminados.", "INFO")
    _actualizar_ticket(ticket_path, "completado", f"Huella de voz creada: {os.path.basename(huella_path)}")
    _reportar_memoria("generar_huella_voz", "OK", {"alias": alias, "metodo": metodo})
    _enviar_bus("DATOS", f"Huella de voz lista para '{alias}'" , {"metodo": metodo, "huella": os.path.basename(huella_path)}, dest="__BROADCAST__")
    print(f"[{ID_SOLDADO}] ✓ Huella de voz forjada para '{alias}'.")

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

# ─── MODO STANDALONE ──────────────────────────────────────────────────────────
def procesar_directo(src_path, alias, password):
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    ticket_fake = {
        "id":              f"DIRECT_OIDO_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "fuente":          src_path,
        "alias":           alias,
        "password_hash":   pw_hash,
        "timestamp_inicio": datetime.now().isoformat(),
        "status":          "pending"
    }
    os.makedirs(TEMP_DIR, exist_ok=True)
    ticket_path = os.path.join(TEMP_DIR, "_ticket_oido_temp.json")
    with open(ticket_path, "w", encoding="utf-8") as f:
        json.dump(ticket_fake, f, indent=4)
    ejecutar_mision(ticket_path)
    if os.path.exists(ticket_path):
        os.remove(ticket_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ejecutar_mision(sys.argv[1])
    else:
        print(f"[{ID_SOLDADO}] Modo interactivo.")
        src   = input("  → Ruta al video: ").strip()
        alias = input("  → Alias (ej: Richon): ").strip()
        pw    = input("  → Contraseña de encriptación: ").strip()
        procesar_directo(src, alias, pw)
