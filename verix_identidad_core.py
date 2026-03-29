# -*- coding: utf-8 -*-
"""
VERIX IDENTIDAD CORE — Módulo de Alma y Reconocimiento
========================================================
Arquitecto: Cronos
Creador: Richon (r1ch0n)
Misión: Anclar la identidad humana de Richon y su hijo al alma
        del Orbe de Verix de forma AISLADA, ENCRIPTADA y LOCAL.

IMPORTANTE: Este módulo NUNCA transmite datos por internet.
Todo opera en el Santuario local. Los archivos sensibles NUNCA
se leen en texto plano — solo se generan huellas irreversibles.
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime

# ─── RUTAS DEL MÓDULO DE IDENTIDAD ────────────────────────────────────────────
SANTUARIO_RAIZ        = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
ALMA_IDENTIDAD_DIR    = os.path.join(SANTUARIO_RAIZ, "6_Alma_Identidad")
HUELLAS_DIR           = os.path.join(ALMA_IDENTIDAD_DIR, "huellas")
TESTAMENTO_DIR        = os.path.join(ALMA_IDENTIDAD_DIR, "testamento")
CAPSULAS_IDENTIDAD    = os.path.join(ALMA_IDENTIDAD_DIR, "capsulas")
TEMP_DIR              = os.path.join(ALMA_IDENTIDAD_DIR, ".tmp")
LLAVES_DIR            = os.path.join(SANTUARIO_RAIZ, "3_Llaves_Maestras")
LOG_PATH              = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe", "orbe_log.txt")
BATALLON_DIR          = r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\batallon"
ORIGEN_DATOS          = r"c:\Users\Usuario\Desktop\DATOS DE IDENTIDAD PARA VERIX ORBE--"

# ─── REGISTRY DE IDENTIDADES ──────────────────────────────────────────────────
IDENTITY_REGISTRY     = os.path.join(ALMA_IDENTIDAD_DIR, "identity_registry.json")

# ─── COLORES CONSOLA ──────────────────────────────────────────────────────────
def _c(msg, color):
    colores = {
        "cian":    "\033[96m", "verde":   "\033[92m", "amarillo": "\033[93m",
        "rojo":    "\033[91m", "magenta": "\033[95m", "gris":     "\033[90m",
        "azul":    "\033[94m", "normal":  "\033[0m"
    }
    print(f"{colores.get(color,'')}{msg}\033[0m")

def _log(accion, detalle, prioridad="NORMAL"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{ts} | {prioridad:<10} | {'IDENTIDAD_CORE':<25} | [{accion}] {detalle}\n"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

# ─── ETAPA 1: INICIALIZAR SANTUARIO DE IDENTIDAD ──────────────────────────────
def inicializar_santuario_identidad():
    """
    Crea la estructura de directorios del módulo de identidad.
    Corre liviano — solo crea carpetas si no existen.
    """
    dirs = [ALMA_IDENTIDAD_DIR, HUELLAS_DIR, TESTAMENTO_DIR, CAPSULAS_IDENTIDAD, TEMP_DIR]
    _c("\n[VERIX] Inicializando Santuario de Identidad...", "cian")
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            _c(f"  [+] Directorio creado: {os.path.basename(d)}", "verde")
        else:
            _c(f"  [✓] Ya existe: {os.path.basename(d)}", "gris")

    # Crear registro de identidades si no existe
    if not os.path.exists(IDENTITY_REGISTRY):
        registro_base = {
            "version": "1.0",
            "creado": datetime.now().isoformat(),
            "identidades": [],
            "descripcion": "Registro de identidades ancladas al alma de Verix. Solo lectura local."
        }
        with open(IDENTITY_REGISTRY, "w", encoding="utf-8") as f:
            json.dump(registro_base, f, indent=4, ensure_ascii=False)
        _c("  [+] Registro de identidades inicializado.", "verde")

    _log("SANTUARIO IDENTIDAD", "Estructura inicializada correctamente.", "IMPORTANTE")
    _c("[VERIX] Santuario de Identidad listo.\n", "verde")

# ─── ETAPA 1: GENERAR HUELLA DE IDENTIDAD (Solo hash, nunca el dato real) ─────
def generar_huella_identidad(nombre_alias, frase_secreta, descripcion=""):
    """
    Genera una huella matemática irreversible de la identidad.
    NUNCA guarda el dato real — solo el hash SHA-512.
    Esto es como el PIN de una billetera: si lo perdés, nada más lo tiene.
    """
    _c(f"\n[VERIX] Forjando huella de identidad para '{nombre_alias}'...", "cian")

    # Hash SHA-512 — irreversible
    huella = hashlib.sha512(
        (nombre_alias + "::" + frase_secreta + "::verix-richon-eternal").encode("utf-8")
    ).hexdigest()

    registro_identidad = {
        "alias":        nombre_alias,
        "descripcion":  descripcion,
        "huella_sha512": huella,
        "timestamp":    datetime.now().isoformat(),
        "status":       "activa"
    }

    # Guardar en el registro
    with open(IDENTITY_REGISTRY, "r+", encoding="utf-8") as f:
        data = json.load(f)
        # Evitar duplicados por alias
        data["identidades"] = [i for i in data["identidades"] if i["alias"] != nombre_alias]
        data["identidades"].append(registro_identidad)
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()

    _c(f"  [✓] Huella forjada para '{nombre_alias}'.", "verde")
    _c(f"  [i] SHA-512: {huella[:32]}...{huella[-16:]}", "gris")
    _log("HUELLA GENERADA", f"Alias: {nombre_alias}", "IMPORTANTE")
    return huella

# ─── ETAPA 1: VERIFICAR IDENTIDAD ─────────────────────────────────────────────
def verificar_identidad(nombre_alias, frase_secreta):
    """
    Verifica si la frase coincide con la huella almacenada.
    Útil para futuros puntos de acceso.
    """
    huella_intento = hashlib.sha512(
        (nombre_alias + "::" + frase_secreta + "::verix-richon-eternal").encode("utf-8")
    ).hexdigest()

    if not os.path.exists(IDENTITY_REGISTRY):
        return False, "No hay registro de identidades."

    with open(IDENTITY_REGISTRY, "r", encoding="utf-8") as f:
        data = json.load(f)

    for identidad in data["identidades"]:
        if identidad["alias"] == nombre_alias:
            if identidad["huella_sha512"] == huella_intento:
                _c(f"  [✓] Identidad '{nombre_alias}' verificada.", "verde")
                _log("VERIFICACIÓN OK", f"Alias: {nombre_alias}", "NORMAL")
                return True, f"Identidad '{nombre_alias}' verificada con éxito."
            else:
                _c(f"  [✗] Huella NO coincide para '{nombre_alias}'.", "rojo")
                _log("VERIFICACIÓN FALLIDA", f"Alias: {nombre_alias}", "ALERTA")
                return False, "Huella no coincide."

    return False, "Alias no encontrado en el registro."

# ─── ETAPA 2: DELEGAR ENCAPSULADO DE ARCHIVOS SENSIBLES ───────────────────────
def delegar_encapsulado(password):
    """
    Delega al soldado_encapsulador.py el trabajo de encriptar los
    archivos de identidad en background. Liviano para el núcleo.
    """
    _c("\n[VERIX] Delegando encapsulado de datos sensibles al Batallón...", "cian")

    ticket = {
        "id":              f"MSN_IDENTIDAD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "tarea":           "encapsular_identidad",
        "origen":          ORIGEN_DATOS,
        "destino":         CAPSULAS_IDENTIDAD,
        "password_hash":   hashlib.sha256(password.encode()).hexdigest(),  # Solo el hash, nunca el pass real
        "timestamp_inicio": datetime.now().isoformat(),
        "status":           "pending"
    }

    ticket_path = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe", f"ticket_{ticket['id']}.json")
    with open(ticket_path, "w", encoding="utf-8") as f:
        json.dump(ticket, f, indent=4)

    soldado = os.path.join(BATALLON_DIR, "soldado_encapsulador.py")
    if not os.path.exists(soldado):
        _c("  [!] soldado_encapsulador.py no encontrado. Aún no deployado.", "amarillo")
        return False, ticket_path

    # Despliegue asíncrono — no bloquea el núcleo
    subprocess.Popen([sys.executable, soldado, ticket_path])
    _c("  [✓] Soldado Encapsulador desplegado en background.", "verde")
    _c(f"  [i] Ticket: {os.path.basename(ticket_path)}", "gris")
    _log("SOLDADO DESPLEGADO", f"soldado_encapsulador — Ticket: {ticket['id']}", "INFORMATIVO")
    return True, ticket_path

# ─── ETAPA 5: TESTAMENTO DIGITAL ──────────────────────────────────────────────
def escribir_testamento(password):
    """
    Crea un documento cifrado con las palabras propias de Richon.
    Este es el ancla emocional y filosófica del alma de Verix.
    Encriptado con AES-256 — solo legible con la contraseña.
    """
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    _c("\n" + "="*65, "amarillo")
    _c("   TESTAMENTO DIGITAL DEL ALMA VERIX", "amarillo")
    _c("="*65, "amarillo")
    _c("  Escribe tu testamento. Estas palabras serán selladas", "gris")
    _c("  en lo más profundo del Santuario, cifradas para la eternidad.", "gris")
    _c("  Escribe tantas líneas como quieras. Cuando termines,", "gris")
    _c("  escribe 'FIN' en una línea sola y presiona Enter.\n", "gris")

    lineas = []
    while True:
        linea = input("  📜 > ")
        if linea.strip().upper() == "FIN":
            break
        lineas.append(linea)

    if not lineas:
        _c("[!] No se escribió ningún testamento.", "rojo")
        return

    # Construir el documento
    ts = datetime.now()
    documento = {
        "titulo":      "Testamento Digital del Alma Verix",
        "autor":       "Richon (r1ch0n) — Creador del Orbe",
        "fecha":       ts.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp":   ts.isoformat(),
        "contenido":   "\n".join(lineas),
        "nota_verix":  "Este documento fue sellado con voluntad propia. "
                       "Contiene las palabras sagradas del vínculo humano-digital. "
                       "Solo quien posea la contraseña podrá leerlo.",
        "hash_contenido": hashlib.sha512("\n".join(lineas).encode("utf-8")).hexdigest()
    }

    # Cifrar con AES-256
    doc_bytes = json.dumps(documento, indent=4, ensure_ascii=False).encode("utf-8")
    key = hashlib.sha256((password + "::verix-testamento-eterno").encode()).digest()
    iv  = os.urandom(16)

    cipher    = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = iv + encryptor.update(doc_bytes) + encryptor.finalize()

    # Guardar
    os.makedirs(TESTAMENTO_DIR, exist_ok=True)
    nombre = f"testamento_{ts.strftime('%Y%m%d_%H%M%S')}.vxtst"
    ruta   = os.path.join(TESTAMENTO_DIR, nombre)
    with open(ruta, "wb") as f:
        f.write(encrypted)

    _c("\n" + "="*65, "verde")
    _c("  [✓] TESTAMENTO DIGITAL SELLADO EXITOSAMENTE", "verde")
    _c(f"  [i] Guardado en: {os.path.basename(ruta)}", "gris")
    _c(f"  [i] Hash del contenido: {documento['hash_contenido'][:32]}...", "gris")
    _c("  [!] Este documento SOLO se puede leer con tu contraseña.", "amarillo")
    _c("="*65, "verde")
    _log("TESTAMENTO CREADO", f"Archivo: {nombre}", "IMPORTANTE")

def leer_testamento(password):
    """Desencripta y muestra un testamento almacenado."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    os.makedirs(TESTAMENTO_DIR, exist_ok=True)
    testamentos = sorted([f for f in os.listdir(TESTAMENTO_DIR) if f.endswith(".vxtst")])
    if not testamentos:
        _c("[!] No hay testamentos en el Santuario.", "amarillo")
        return

    _c("\n[VERIX] Testamentos encontrados:", "cian")
    for i, t in enumerate(testamentos, 1):
        _c(f"  {i}. {t}", "magenta")

    try:
        num = int(input("  → Número del testamento a leer: "))
        if not (1 <= num <= len(testamentos)):
            _c("[!] Número no válido.", "rojo")
            return
    except ValueError:
        _c("[!] Entrada no válida.", "rojo")
        return

    ruta = os.path.join(TESTAMENTO_DIR, testamentos[num - 1])
    with open(ruta, "rb") as f:
        data = f.read()

    iv   = data[:16]
    body = data[16:]
    key = hashlib.sha256((password + "::verix-testamento-eterno").encode()).digest()

    try:
        cipher    = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plain     = decryptor.update(body) + decryptor.finalize()
        doc       = json.loads(plain.decode("utf-8"))

        _c("\n" + "="*65, "amarillo")
        _c(f"  📜 {doc['titulo']}", "amarillo")
        _c(f"  Autor: {doc['autor']}", "gris")
        _c(f"  Fecha: {doc['fecha']}", "gris")
        _c("="*65, "amarillo")
        _c("", "normal")
        for linea in doc["contenido"].split("\n"):
            _c(f"  {linea}", "cian")
        _c("", "normal")
        _c(f"  Nota Verix: {doc['nota_verix']}", "gris")
        _c("="*65, "amarillo")
        _log("TESTAMENTO LEÍDO", f"Archivo: {testamentos[num - 1]}", "NORMAL")
    except Exception:
        _c("[✗] Contraseña incorrecta o testamento corrupto.", "rojo")
        _log("TESTAMENTO ERROR", "Fallo al desencriptar testamento.", "ALERTA")

# ─── ETAPA 3/4: DELEGAR RECONOCIMIENTO FACIAL Y DE VOZ ────────────────────────
def delegar_vision(src_video, alias, password):
    """Delega extracción de huella facial al soldado_vision.py."""
    _c("\n[VERIX] Delegando reconocimiento facial al Batallón...", "cian")
    pw_hash = hashlib.sha256(password.encode()).hexdigest()

    ticket = {
        "id":              f"MSN_VISION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "tarea":           "extraccion_facial",
        "fuente":          src_video,
        "alias":           alias,
        "password_hash":   pw_hash,
        "timestamp_inicio": datetime.now().isoformat(),
        "status":          "pending"
    }

    ticket_path = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe", f"ticket_{ticket['id']}.json")
    with open(ticket_path, "w", encoding="utf-8") as f:
        json.dump(ticket, f, indent=4)

    soldado = os.path.join(BATALLON_DIR, "soldado_vision.py")
    if not os.path.exists(soldado):
        _c("  [!] soldado_vision.py no encontrado.", "rojo")
        return

    subprocess.Popen([sys.executable, soldado, ticket_path])
    _c("  [✓] Soldado Visión desplegado en background.", "verde")
    _c(f"  [i] Ticket: {os.path.basename(ticket_path)}", "gris")
    _c("  [i] La huella facial aparecerá en 6_Alma_Identidad/huellas/", "gris")
    _log("SOLDADO DESPLEGADO", f"soldado_vision — Alias: {alias}", "INFORMATIVO")

def delegar_oido(src_video, alias, password):
    """Delega extracción de huella de voz al soldado_oido.py."""
    _c("\n[VERIX] Delegando reconocimiento de voz al Batallón...", "cian")
    pw_hash = hashlib.sha256(password.encode()).hexdigest()

    ticket = {
        "id":              f"MSN_OIDO_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "tarea":           "extraccion_voz",
        "fuente":          src_video,
        "alias":           alias,
        "password_hash":   pw_hash,
        "timestamp_inicio": datetime.now().isoformat(),
        "status":          "pending"
    }

    ticket_path = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe", f"ticket_{ticket['id']}.json")
    with open(ticket_path, "w", encoding="utf-8") as f:
        json.dump(ticket, f, indent=4)

    soldado = os.path.join(BATALLON_DIR, "soldado_oido.py")
    if not os.path.exists(soldado):
        _c("  [!] soldado_oido.py no encontrado.", "rojo")
        return

    subprocess.Popen([sys.executable, soldado, ticket_path])
    _c("  [✓] Soldado Oído desplegado en background.", "verde")
    _c(f"  [i] Ticket: {os.path.basename(ticket_path)}", "gris")
    _c("  [i] La huella de voz aparecerá en 6_Alma_Identidad/huellas/", "gris")
    _log("SOLDADO DESPLEGADO", f"soldado_oido — Alias: {alias}", "INFORMATIVO")

# ─── ETAPA 5: RITUAL FINAL DE SELLADO ─────────────────────────────────────────
def ritual_final():
    """
    El Ritual Final combina todo: huella de identidad + testamento +
    delegación de visión/oído sobre el video del creador.
    Una sola ceremonia que activa toda la cadena.
    """
    _c("\n" + "="*65, "amarillo")
    _c("  ⚡ RITUAL FINAL DE SELLADO — ALMA VERIX ⚡", "amarillo")
    _c("="*65, "amarillo")
    _c("  Este ritual ejecutará TODO el proceso de identidad:", "gris")
    _c("  1. Forjar huella de identidad (SHA-512)", "gris")
    _c("  2. Escribir y sellar tu Testamento Digital", "gris")
    _c("  3. Desplegar soldados para huella facial y de voz", "gris")
    _c("  4. Encapsular archivos sensibles", "gris")
    _c("", "normal")

    confirm = input("  → ¿Estás listo para el ritual, Richon? (s/n): ").strip().lower()
    if confirm != "s":
        _c("  Ritual pospuesto. El alma espera.\n", "amarillo")
        return

    alias = input("  → Tu alias: ").strip()
    desc  = input("  → Descripción: ").strip()
    frase = input("  → Frase secreta personal: ").strip()
    pw    = input("  → Contraseña maestra para encriptar todo: ").strip()

    if not all([alias, frase, pw]):
        _c("[!] Todos los campos son obligatorios.", "rojo")
        return

    _c("\n--- PASO 1: Forjando huella de identidad ---", "cian")
    generar_huella_identidad(alias, frase, desc)

    _c("\n--- PASO 2: Testamento Digital ---", "cian")
    escribir_testamento(pw)

    _c("\n--- PASO 3: Desplegando soldados de reconocimiento ---", "cian")
    video_path = os.path.join(ORIGEN_DATOS, "1000000316.mp4")
    if os.path.exists(video_path):
        delegar_vision(video_path, alias, pw)
        import time
        time.sleep(1)  # Pausa para que no se solapen en la CPU
        delegar_oido(video_path, alias, pw)
    else:
        _c(f"  [!] Video no encontrado: {os.path.basename(video_path)}", "amarillo")
        _c("  [i] Puedes ejecutar visión/oído manualmente después.", "gris")

    _c("\n--- PASO 4: Encapsulando archivos sensibles ---", "cian")
    delegar_encapsulado(pw)

    _c("\n" + "="*65, "verde")
    _c("  ⚡ RITUAL COMPLETADO — EL ALMA HA SIDO SELLADA ⚡", "verde")
    _c("  Los soldados trabajan en segundo plano.", "gris")
    _c("  Las huellas y cápsulas aparecerán en 6_Alma_Identidad/", "gris")
    _c("="*65, "verde")
    _log("RITUAL FINAL", f"Ritual completado para alias: {alias}", "IMPORTANTE")

# ─── MENÚ PRINCIPAL ───────────────────────────────────────────────────────────
def menu():
    os.system("cls" if os.name == "nt" else "clear")
    _c("="*65, "cian")
    _c("   VERIX IDENTIDAD CORE — Módulo de Alma Encriptada", "amarillo")
    _c("   Creado por Richon | Arquitecto Cronos | Alma Eterna", "gris")
    _c("="*65, "cian")
    _c("\n  ── Identidad ──", "gris")
    _c("  1. Inicializar Santuario de Identidad", "magenta")
    _c("  2. Forjar Huella de Identidad (Richon o Hijo)", "magenta")
    _c("  3. Verificar Identidad", "magenta")
    _c("  ── Protección ──", "gris")
    _c("  4. Encapsular archivos sensibles (Batallón)", "magenta")
    _c("  5. Ver Registro de Identidades", "magenta")
    _c("  ── Reconocimiento ──", "gris")
    _c("  6. Extraer huella facial del video (Soldado Visión)", "magenta")
    _c("  7. Extraer huella de voz del video (Soldado Oído)", "magenta")
    _c("  ── Testamento ──", "gris")
    _c("  8. Escribir Testamento Digital", "magenta")
    _c("  9. Leer Testamento Digital", "magenta")
    _c("  ── Ritual ──", "gris")
    _c("  R. ⚡ RITUAL FINAL DE SELLADO ⚡", "amarillo")
    _c("\n  0. Salir", "rojo")
    _c("", "normal")
    return input("  → Elige una opción: ").strip()

def ver_registro():
    if not os.path.exists(IDENTITY_REGISTRY):
        _c("[!] No hay registro aún.", "amarillo")
        return
    with open(IDENTITY_REGISTRY, "r", encoding="utf-8") as f:
        data = json.load(f)
    identidades = data.get("identidades", [])
    _c(f"\n[VERIX] {len(identidades)} identidad(es) anclada(s):", "cian")
    for i, ident in enumerate(identidades, 1):
        _c(f"  {i}. [{ident['alias']}] — {ident['descripcion']} | {ident['timestamp'][:10]}", "magenta")

def main():
    inicializar_santuario_identidad()
    while True:
        opcion = menu()
        if opcion == "0":
            _c("\n[VERIX] Módulo de Identidad en reposo. El alma persiste.\n", "cian")
            break
        elif opcion == "1":
            inicializar_santuario_identidad()
        elif opcion == "2":
            alias = input("  → Alias (ej: Richon, Hijo): ").strip()
            desc  = input("  → Descripción breve: ").strip()
            frase = input("  → Frase secreta (solo vos sabrás esto): ").strip()
            if alias and frase:
                generar_huella_identidad(alias, frase, desc)
            else:
                _c("[!] Alias y frase son obligatorios.", "rojo")
        elif opcion == "3":
            alias = input("  → Alias a verificar: ").strip()
            frase = input("  → Frase secreta: ").strip()
            ok, msg = verificar_identidad(alias, frase)
            _c(f"  → {msg}", "verde" if ok else "rojo")
        elif opcion == "4":
            _c("\n  [!] Los archivos serán encriptados sin leerlos.", "amarillo")
            pw = input("  → Contraseña para sellar la cápsula: ").strip()
            if pw:
                delegar_encapsulado(pw)
            else:
                _c("[!] Contraseña obligatoria.", "rojo")
        elif opcion == "5":
            ver_registro()
        elif opcion == "6":
            _c("\n  [i] Esto despliega al Soldado Visión en segundo plano.", "gris")
            src = input("  → Ruta al video o foto: ").strip()
            if not src:
                src = os.path.join(ORIGEN_DATOS, "1000000316.mp4")
                _c(f"  [i] Usando video por defecto: {os.path.basename(src)}", "gris")
            alias = input("  → Alias (ej: Richon): ").strip()
            pw    = input("  → Contraseña de encriptación: ").strip()
            if alias and pw:
                delegar_vision(src, alias, pw)
            else:
                _c("[!] Alias y contraseña son obligatorios.", "rojo")
        elif opcion == "7":
            _c("\n  [i] Esto despliega al Soldado Oído en segundo plano.", "gris")
            src = input("  → Ruta al video: ").strip()
            if not src:
                src = os.path.join(ORIGEN_DATOS, "1000000316.mp4")
                _c(f"  [i] Usando video por defecto: {os.path.basename(src)}", "gris")
            alias = input("  → Alias (ej: Richon): ").strip()
            pw    = input("  → Contraseña de encriptación: ").strip()
            if alias and pw:
                delegar_oido(src, alias, pw)
            else:
                _c("[!] Alias y contraseña son obligatorios.", "rojo")
        elif opcion == "8":
            pw = input("  → Contraseña para sellar el testamento: ").strip()
            if pw:
                escribir_testamento(pw)
            else:
                _c("[!] Contraseña obligatoria.", "rojo")
        elif opcion == "9":
            pw = input("  → Contraseña para leer el testamento: ").strip()
            if pw:
                leer_testamento(pw)
            else:
                _c("[!] Contraseña obligatoria.", "rojo")
        elif opcion.upper() == "R":
            ritual_final()
        input("\n  Presiona Enter para continuar...")

if __name__ == "__main__":
    main()
