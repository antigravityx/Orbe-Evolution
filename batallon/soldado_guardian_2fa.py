# -*- coding: utf-8 -*-
"""
SOLDADO GUARDIÁN 2FA v1 — Escudo de Autenticación del Orbe
==========================================================
Rol     : Gestión total de la autenticación 2FA de GitHub
Poderes : Generar códigos TOTP / Sellar recovery codes / Auditoría de seguridad
Memoria : Log propio + comparte inteligencia con la Memoria Madre
Seguridad: Secreto TOTP y recovery codes NUNCA en texto plano — viven en el Vault

⚠️  El secreto TOTP NUNCA se imprime ni loguea.
    Se recupera en tiempo de ejecución desde el VaultOrbe.

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import sys
import json
import hashlib
import time
import urllib.request
import urllib.error
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

# Importar pyotp para generación TOTP
try:
    import pyotp
except ImportError:
    print("❌ Falta la dependencia 'pyotp'. Ejecuta: pip install pyotp")
    sys.exit(1)

# ─── CONSTANTES ──────────────────────────────────────────────────────────────
NOMBRE_SOLDADO  = "GUARDIAN_2FA_v1"
VAULT_KEY_TOTP  = "GITHUB_2FA_TOTP_SECRET"
VAULT_KEY_RECOV = "GITHUB_2FA_RECOVERY_CODES"
LOG_PATH        = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\guardian_2fa_log.jsonl"
PARCHES_PATH    = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\guardian_2fa_parches.json"
MEMORIA_MADRE   = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\memoria_madre.json"

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


# ─── LOGGER ESTRUCTURADO ─────────────────────────────────────────────────────
def _log(accion: str, detalle: str, nivel: str = "INFO", datos: dict = None):
    """Registra cada movimiento como JSON — nunca expone secretos."""
    entry = {
        "ts": datetime.now().isoformat(),
        "soldado": NOMBRE_SOLDADO,
        "nivel": nivel,
        "accion": accion,
        "detalle": detalle,
        "datos_extra": datos or {}
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[{nivel}] [{NOMBRE_SOLDADO}] {accion}: {detalle}")
    return entry


# ─── AUTO-SANACIÓN Y PARCHES ─────────────────────────────────────────────────
def _registrar_falla(accion: str, error: str, contexto: dict = None):
    """Guarda la falla en el archivo de parches para aprender de ella."""
    parches = {}
    if os.path.exists(PARCHES_PATH):
        try:
            with open(PARCHES_PATH, "r", encoding="utf-8") as f:
                parches = json.load(f)
        except:
            pass

    falla_id = hashlib.sha256(f"{accion}:{error}".encode()).hexdigest()[:12]
    if falla_id not in parches:
        parches[falla_id] = {
            "accion": accion,
            "error": error,
            "contexto": contexto or {},
            "primera_vez": datetime.now().isoformat(),
            "ocurrencias": 1,
            "parche_aplicado": False
        }
    else:
        parches[falla_id]["ocurrencias"] += 1
        parches[falla_id]["ultima_vez"] = datetime.now().isoformat()

    with open(PARCHES_PATH, "w", encoding="utf-8") as f:
        json.dump(parches, f, indent=2, ensure_ascii=False)

    _log("AUTO-DIAGNÓSTICO", f"Falla catalogada: {falla_id}", nivel="ALERTA")
    return falla_id


def _compartir_con_memoria_madre(operacion: str, resultado: str, estadisticas: dict):
    """Publica el aprendizaje de esta operación en la Memoria Madre global."""
    try:
        memoria = {}
        if os.path.exists(MEMORIA_MADRE):
            with open(MEMORIA_MADRE, "r", encoding="utf-8") as f:
                memoria = json.load(f)

        soldado_mem = memoria.setdefault(NOMBRE_SOLDADO, {"operaciones": [], "stats": {}})
        soldado_mem["operaciones"].append({
            "ts": datetime.now().isoformat(),
            "op": operacion,
            "resultado": resultado
        })
        soldado_mem["operaciones"] = soldado_mem["operaciones"][-100:]

        stats = soldado_mem["stats"]
        stats["total_ops"] = stats.get("total_ops", 0) + 1
        if resultado == "OK":
            stats["exitosas"] = stats.get("exitosas", 0) + 1
        else:
            stats["fallidas"] = stats.get("fallidas", 0) + 1
        stats.update(estadisticas)
        stats["ultimo_contacto"] = datetime.now().isoformat()

        with open(MEMORIA_MADRE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=2, ensure_ascii=False)
    except Exception as e:
        _log("MEMORIA_MADRE", f"No se pudo sincronizar: {str(e)}", nivel="AVISO")


# ─── UTILIDAD: PORTAPAPELES WINDOWS ──────────────────────────────────────────
def _copiar_al_clipboard(texto: str):
    """Copia texto al portapapeles de Windows usando PowerShell."""
    try:
        import subprocess
        subprocess.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{texto}'"],
            capture_output=True, check=True
        )
        return True
    except Exception:
        return False


# ─── NÚCLEO DEL GUARDIÁN 2FA ─────────────────────────────────────────────────
class Guardian2FA:
    """
    Soldado Guardián 2FA — Escudo de autenticación del ecosistema GitHub de r1ch0n.
    Genera códigos TOTP, almacena recovery codes, y audita la seguridad de la cuenta.
    """

    def __init__(self):
        _log("DESPERTAR", "Guardián 2FA en línea — verificando vault")
        self._vault = VaultOrbe()
        _log("DESPERTAR", "Vault conectado — listo para proteger", nivel="OK")

    # ── MISIÓN 1: Sellar secreto TOTP en el Vault ────────────────────────────
    def sellar_totp(self, secreto: str = None):
        """
        Sella el secreto TOTP de GitHub en el Vault.
        Si no se pasa, lo pide por consola de forma segura.
        """
        _log("SELLAR_TOTP", "Iniciando sellado de secreto TOTP")
        try:
            if not secreto:
                print("\n╔══════════════════════════════════════════════════╗")
                print("║  SELLADO DE SECRETO TOTP — GitHub 2FA           ║")
                print("╚══════════════════════════════════════════════════╝")
                print("\nEste es el código de texto que GitHub te da cuando")
                print("configurás la Authenticator App (click en 'Can't scan').")
                print("El secreto se guardará encriptado con AES-256.\n")
                secreto = input("🔐 Pegá el secreto TOTP aquí: ").strip()

            if not secreto:
                _log("SELLAR_TOTP", "Secreto vacío — operación cancelada", nivel="AVISO")
                return False

            # Validar que es un secreto TOTP válido (base32)
            secreto_limpio = secreto.replace(" ", "").upper()
            try:
                pyotp.TOTP(secreto_limpio).now()
            except Exception:
                _log("SELLAR_TOTP", "El secreto no es válido (debe ser base32)", nivel="ERROR")
                print("❌ El secreto no parece ser un código TOTP válido.")
                return False

            # Sellar en el Vault
            ok = self._vault.guardar(VAULT_KEY_TOTP, secreto_limpio, categoria="2FA_CRITICO")
            if ok:
                _log("SELLAR_TOTP", "Secreto TOTP sellado en el Vault", nivel="OK")
                _compartir_con_memoria_madre("sellar_totp", "OK", {"estado": "sellado"})
                print("✅ Secreto TOTP sellado exitosamente en el Vault.")
                print("   Ahora podés generar códigos con: CODIGO")
                return True
            else:
                _log("SELLAR_TOTP", "Error al sellar en Vault", nivel="CRITICO")
                return False

        except Exception as e:
            _registrar_falla("sellar_totp", str(e))
            print(f"❌ Error: {e}")
            return False

    # ── MISIÓN 2: Generar código TOTP ────────────────────────────────────────
    def generar_codigo(self) -> str:
        """Genera un código TOTP de 6 dígitos y lo copia al portapapeles."""
        _log("GENERAR_CODIGO", "Recuperando secreto TOTP del Vault")
        try:
            secreto = self._vault.recuperar(VAULT_KEY_TOTP)
            if not secreto:
                _log("GENERAR_CODIGO", "No hay secreto TOTP sellado", nivel="ALERTA")
                print("❌ No hay secreto TOTP en el Vault.")
                print("   Primero ejecutá: python soldado_guardian_2fa.py SELLAR_TOTP")
                return None

            totp = pyotp.TOTP(secreto)
            codigo = totp.now()
            tiempo_restante = totp.interval - (int(time.time()) % totp.interval)

            # Copiar al clipboard
            copiado = _copiar_al_clipboard(codigo)

            print("\n╔══════════════════════════════════════════════════╗")
            print("║  🔢 CÓDIGO 2FA GENERADO                         ║")
            print("╠══════════════════════════════════════════════════╣")
            print(f"║                                                  ║")
            print(f"║     Código:  [ {codigo} ]                        ║")
            print(f"║     Expira en: {tiempo_restante:2d} segundos                     ║")
            print(f"║     Clipboard: {'✅ Copiado' if copiado else '❌ Manual'}                       ║")
            print(f"║                                                  ║")
            print("╚══════════════════════════════════════════════════╝\n")

            _log("GENERAR_CODIGO", f"Código generado — expira en {tiempo_restante}s", nivel="OK")
            _compartir_con_memoria_madre("generar_codigo", "OK", {"expira_en": tiempo_restante})
            return codigo

        except Exception as e:
            _registrar_falla("generar_codigo", str(e))
            print(f"❌ Error: {e}")
            return None

    # ── MISIÓN 3: Sellar recovery codes ──────────────────────────────────────
    def sellar_recovery_codes(self, codes: str = None):
        """Sella los recovery codes de GitHub en el Vault encriptado."""
        _log("SELLAR_RECOVERY", "Iniciando sellado de recovery codes")
        try:
            if not codes:
                print("\n╔══════════════════════════════════════════════════╗")
                print("║  SELLADO DE RECOVERY CODES — GitHub 2FA         ║")
                print("╚══════════════════════════════════════════════════╝")
                print("\nPegá tus recovery codes de GitHub (uno por línea).")
                print("Cuando termines, escribí 'FIN' en una línea nueva.\n")

                lineas = []
                while True:
                    linea = input("  > ").strip()
                    if linea.upper() == "FIN":
                        break
                    if linea:
                        lineas.append(linea)
                codes = "\n".join(lineas)

            if not codes.strip():
                _log("SELLAR_RECOVERY", "No se proporcionaron codes", nivel="AVISO")
                return False

            cantidad = len(codes.strip().splitlines())
            ok = self._vault.guardar(VAULT_KEY_RECOV, codes.strip(), categoria="2FA_RECOVERY")
            if ok:
                _log("SELLAR_RECOVERY", f"{cantidad} recovery codes sellados", nivel="OK")
                _compartir_con_memoria_madre("sellar_recovery", "OK", {"cantidad": cantidad})
                print(f"✅ {cantidad} recovery codes sellados en el Vault.")
                return True
            else:
                _log("SELLAR_RECOVERY", "Error al sellar", nivel="CRITICO")
                return False

        except Exception as e:
            _registrar_falla("sellar_recovery", str(e))
            print(f"❌ Error: {e}")
            return False

    # ── MISIÓN 4: Ver recovery codes ─────────────────────────────────────────
    def ver_recovery_codes(self):
        """Recupera y muestra los recovery codes del Vault."""
        _log("VER_RECOVERY", "Recuperando recovery codes del Vault")
        try:
            codes = self._vault.recuperar(VAULT_KEY_RECOV)
            if not codes:
                print("❌ No hay recovery codes en el Vault.")
                print("   Primero ejecutá: python soldado_guardian_2fa.py SELLAR_RECOVERY")
                return None

            print("\n╔══════════════════════════════════════════════════╗")
            print("║  🔑 RECOVERY CODES — GitHub 2FA                 ║")
            print("╠══════════════════════════════════════════════════╣")
            for i, code in enumerate(codes.splitlines(), 1):
                print(f"║   {i:2d}. {code:<43} ║")
            print("╚══════════════════════════════════════════════════╝")
            print("\n⚠️  No compartas estos códigos con nadie.\n")

            _log("VER_RECOVERY", "Codes desplegados en terminal", nivel="OK")
            return codes

        except Exception as e:
            _registrar_falla("ver_recovery", str(e))
            print(f"❌ Error: {e}")
            return None

    # ── MISIÓN 5: Auditoría de seguridad GitHub ──────────────────────────────
    def auditoria_seguridad(self):
        """Consulta la API de GitHub para verificar el estado de 2FA."""
        _log("AUDITORIA", "Iniciando auditoría de seguridad GitHub")
        try:
            token = self._vault.recuperar("GITHUB_PAT_RICHON")
            if not token:
                _log("AUDITORIA", "Token GitHub no disponible en Vault", nivel="ALERTA")
                print("❌ Token GitHub no encontrado en el Vault.")
                print("   La auditoría API requiere el PAT sellado.")
                # Aún podemos reportar estado local
                self._informe_local()
                return

            # Consultar API de GitHub
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Verix-Guardian-2FA/1.0"
            }
            req = urllib.request.Request("https://api.github.com/user", headers=headers)

            with urllib.request.urlopen(req, timeout=15) as resp:
                user_info = json.loads(resp.read().decode())

            tiene_2fa = user_info.get("two_factor_authentication", False)
            login = user_info.get("login", "?")

            print("\n" + "═" * 55)
            print("   AUDITORÍA DE SEGURIDAD — GUARDIÁN 2FA")
            print("═" * 55)
            print(f"\n👤 Cuenta       : {login}")
            print(f"🔐 2FA Activo   : {'✅ SÍ' if tiene_2fa else '❌ NO — ¡PELIGRO!'}")

            # Estado del Vault
            tiene_totp = self._vault.existe(VAULT_KEY_TOTP)
            tiene_recovery = self._vault.existe(VAULT_KEY_RECOV)

            print(f"\n🏛️  Estado del Vault:")
            print(f"   Secreto TOTP    : {'✅ Sellado' if tiene_totp else '❌ No sellado'}")
            print(f"   Recovery Codes  : {'✅ Sellados' if tiene_recovery else '❌ No sellados'}")

            # Calcular score de seguridad
            score = 0
            if tiene_2fa: score += 40
            if tiene_totp: score += 30
            if tiene_recovery: score += 30

            barra = "█" * (score // 5) + "░" * ((100 - score) // 5)
            color = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"

            print(f"\n{color} Score Seguridad: {score}%")
            print(f"   [{barra}]")

            if score < 100:
                print("\n⚠️  Recomendaciones:")
                if not tiene_2fa:
                    print("   → Activar 2FA en GitHub Settings > Security")
                if not tiene_totp:
                    print("   → Sellar secreto TOTP: python soldado_guardian_2fa.py SELLAR_TOTP")
                if not tiene_recovery:
                    print("   → Sellar recovery codes: python soldado_guardian_2fa.py SELLAR_RECOVERY")

            print("\n" + "═" * 55 + "\n")

            _log("AUDITORIA", f"Score: {score}% | 2FA: {tiene_2fa}", nivel="OK")
            _compartir_con_memoria_madre("auditoria", "OK", {
                "score": score, "2fa_activo": tiene_2fa,
                "totp_sellado": tiene_totp, "recovery_sellados": tiene_recovery
            })

        except urllib.error.HTTPError as e:
            _registrar_falla("auditoria", f"HTTP {e.code}")
            print(f"❌ Error API GitHub: HTTP {e.code}")
            self._informe_local()
        except Exception as e:
            _registrar_falla("auditoria", str(e))
            print(f"❌ Error: {e}")
            self._informe_local()

    def _informe_local(self):
        """Informe basado solo en el estado local del Vault."""
        print("\n📋 Informe local (sin conexión a API):")
        tiene_totp = self._vault.existe(VAULT_KEY_TOTP)
        tiene_recovery = self._vault.existe(VAULT_KEY_RECOV)
        print(f"   Secreto TOTP    : {'✅ Sellado' if tiene_totp else '❌ No sellado'}")
        print(f"   Recovery Codes  : {'✅ Sellados' if tiene_recovery else '❌ No sellados'}")
        print()

    # ── INFORME COMPLETO ─────────────────────────────────────────────────────
    def informe_completo(self):
        """Diagnóstico completo del estado de seguridad 2FA."""
        print("\n" + "═" * 55)
        print("   INFORME GUARDIÁN 2FA — ORBE DE VERIX")
        print("═" * 55)

        tiene_totp = self._vault.existe(VAULT_KEY_TOTP)
        tiene_recovery = self._vault.existe(VAULT_KEY_RECOV)

        print(f"\n🛡️  Soldado     : {NOMBRE_SOLDADO}")
        print(f"📅 Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n🏛️  Vault Status:")
        print(f"   TOTP Secret   : {'✅ Sellado — listo para generar códigos' if tiene_totp else '❌ No sellado'}")
        print(f"   Recovery Codes: {'✅ Sellados — respaldo seguro' if tiene_recovery else '❌ No sellados'}")

        if tiene_totp:
            totp_secret = self._vault.recuperar(VAULT_KEY_TOTP)
            if totp_secret:
                totp = pyotp.TOTP(totp_secret)
                codigo = totp.now()
                restante = totp.interval - (int(time.time()) % totp.interval)
                print(f"\n🔢 Código actual : [ {codigo} ] — expira en {restante}s")
                _copiar_al_clipboard(codigo)
                print(f"📋 Copiado al portapapeles")

        print(f"\n📡 Comandos disponibles:")
        print(f"   SELLAR_TOTP     → Sellar secreto TOTP en el Vault")
        print(f"   CODIGO          → Generar código 2FA (+ clipboard)")
        print(f"   SELLAR_RECOVERY → Guardar recovery codes")
        print(f"   VER_RECOVERY    → Ver recovery codes guardados")
        print(f"   AUDITORIA       → Auditoría de seguridad GitHub")

        print("\n" + "═" * 55 + "\n")


# ─── EJECUCIÓN DIRECTA ───────────────────────────────────────────────────────
if __name__ == "__main__":
    guardian = Guardian2FA()

    if len(sys.argv) > 1:
        cmd = sys.argv[1].upper()

        if cmd == "SELLAR_TOTP":
            secreto = sys.argv[2] if len(sys.argv) > 2 else None
            guardian.sellar_totp(secreto)

        elif cmd in ("CODIGO", "CODE", "2FA"):
            guardian.generar_codigo()

        elif cmd == "SELLAR_RECOVERY":
            guardian.sellar_recovery_codes()

        elif cmd == "VER_RECOVERY":
            guardian.ver_recovery_codes()

        elif cmd == "AUDITORIA":
            guardian.auditoria_seguridad()

        elif cmd == "INFORME":
            guardian.informe_completo()

        else:
            print(f"Comando desconocido: {cmd}")
            print("Comandos: SELLAR_TOTP | CODIGO | SELLAR_RECOVERY | VER_RECOVERY | AUDITORIA | INFORME")
    else:
        guardian.informe_completo()
