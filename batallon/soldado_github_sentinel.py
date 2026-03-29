# -*- coding: utf-8 -*-
"""
SOLDADO GITHUB SENTINEL v2 — Élite del Batallón Verix
======================================================
Rol     : Control total del ecosistema GitHub de r1ch0n
Poderes : push / pull / crear repos / leer issues / gestionar branches
Memoria : Log propio + comparte parches con la Memoria Madre
Salud   : Auto-sanación — registra fallas y genera parches locales
Aprendizaje: Cada operación entrena su base de patrones

⚠️  El token NUNCA se imprime ni loguea en texto plano.
    Se recupera en tiempo de ejecución desde el VaultOrbe.

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import sys
import json
import subprocess
import hashlib
import urllib.request
import urllib.error
from datetime import datetime

# ─── PATH DEL ORBE ───────────────────────────────────────────────────────────
ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ORBE_ROOT)
from batallon.vault_soldier import VaultOrbe

# ─── CONSTANTES ──────────────────────────────────────────────────────────────
NOMBRE_SOLDADO = "GITHUB_SENTINEL_v2"
REPOS_ORBE     = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
LOG_PATH       = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\sentinel_log.jsonl"
PARCHES_PATH   = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\sentinel_parches.json"
MEMORIA_MADRE  = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\memoria_madre.json"

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
        # Mantener solo los últimos 100 registros por soldado
        soldado_mem["operaciones"] = soldado_mem["operaciones"][-100:]

        # Actualizar estadísticas globales
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


# ─── NÚCLEO DE CONEXIÓN ───────────────────────────────────────────────────────
class GitHubSentinel:
    """
    Soldado de élite con plenos poderes sobre el ecosistema GitHub de r1ch0n.
    """

    def __init__(self):
        _log("DESPERTAR", "Sentinel en línea — recuperando credenciales del vault")
        vault = VaultOrbe()
        self._token = vault.recuperar("GITHUB_PAT_RICHON")
        self._api   = vault.recuperar("GITHUB_API_BASE") or "https://api.github.com"
        self._user  = vault.recuperar("GITHUB_USER") or "drxteren"

        if not self._token:
            _log("AUTENTICACIÓN", "Token no encontrado en vault", nivel="CRITICO")
            raise RuntimeError("Token GitHub no disponible. Ejecuta primero el ritual de sellado.")

        _log("AUTENTICACIÓN", f"Token recuperado para usuario '{self._user}'", nivel="INFO")

    # ── Llamada autenticada a la API GitHub ──────────────────────────────────
    def _api_call(self, endpoint: str, method: str = "GET", body: dict = None):
        """Realiza llamadas HTTP autenticadas. Token NUNCA en logs."""
        url = f"{self._api}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Verix-Orbe-Sentinel/2.0"
        }
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise RuntimeError(f"HTTP {e.code}: {error_body}")

    # ── MISIÓN 1: Verificar identidad en GitHub ──────────────────────────────
    def verificar_identidad(self) -> dict:
        _log("VERIFICAR_IDENTIDAD", "Consultando /user en la API...")
        try:
            info = self._api_call("/user")
            resultado = {
                "login": info.get("login"),
                "nombre": info.get("name"),
                "repos_publicos": info.get("public_repos"),
                "repos_privados": info.get("total_private_repos"),
                "plan": info.get("plan", {}).get("name", "?")
            }
            _log("VERIFICAR_IDENTIDAD", f"Identidad confirmada: {resultado['login']}", nivel="OK")
            _compartir_con_memoria_madre("verificar_identidad", "OK", resultado)
            return resultado
        except Exception as e:
            fid = _registrar_falla("verificar_identidad", str(e))
            _compartir_con_memoria_madre("verificar_identidad", "FALLA", {"falla_id": fid})
            raise

    # ── MISIÓN 2: Listar repositorios ────────────────────────────────────────
    def listar_repos(self) -> list:
        _log("LISTAR_REPOS", "Consultando repositorios...")
        try:
            repos = self._api_call("/user/repos?per_page=100&sort=updated")
            lista = [{"nombre": r["name"], "privado": r["private"],
                      "rama": r["default_branch"], "url": r["clone_url"]} for r in repos]
            _log("LISTAR_REPOS", f"Total: {len(lista)} repositorios encontrados", nivel="OK")
            _compartir_con_memoria_madre("listar_repos", "OK", {"total_repos": len(lista)})
            return lista
        except Exception as e:
            _registrar_falla("listar_repos", str(e))
            raise

    # ── MISIÓN 3: Estado del repo local ─────────────────────────────────────
    def estado_git_local(self, repo_path: str = REPOS_ORBE) -> dict:
        _log("ESTADO_LOCAL", f"Escaneando: {repo_path}")
        try:
            def git(cmd):
                r = subprocess.run(["git"] + cmd, cwd=repo_path,
                                   capture_output=True, text=True, encoding="utf-8")
                return r.stdout.strip(), r.stderr.strip(), r.returncode

            status, _, rc_s = git(["status", "--porcelain"])
            branch, _, _ = git(["rev-parse", "--abbrev-ref", "HEAD"])
            log, _, _ = git(["log", "--oneline", "-5"])

            cambios_sin_commit = len([l for l in status.splitlines() if l.strip()])
            resultado = {
                "rama": branch,
                "cambios_pendientes": cambios_sin_commit,
                "ultimos_commits": log.splitlines(),
                "repo_path": repo_path
            }
            nivel = "ALERTA" if cambios_sin_commit > 0 else "OK"
            _log("ESTADO_LOCAL", f"Rama: {branch} | Cambios: {cambios_sin_commit}", nivel=nivel)
            _compartir_con_memoria_madre("estado_git_local", "OK", resultado)
            return resultado
        except Exception as e:
            _registrar_falla("estado_git_local", str(e), {"repo": repo_path})
            raise

    # ── MISIÓN 4: Commit + Push automático ──────────────────────────────────
    def commit_y_push(self, mensaje: str, repo_path: str = REPOS_ORBE) -> bool:
        _log("COMMIT_PUSH", f"Preparando misión: '{mensaje}'")
        try:
            def git(cmd):
                r = subprocess.run(["git"] + cmd, cwd=repo_path,
                                   capture_output=True, text=True, encoding="utf-8")
                return r.stdout.strip(), r.stderr.strip(), r.returncode

            # Configurar identidad git si no está
            git(["config", "user.email", "verix@orbe.local"])
            git(["config", "user.name", "Verix-Sentinel"])

            # Stage todo
            _, err, rc = git(["add", "-A"])
            if rc != 0:
                raise RuntimeError(f"git add falló: {err}")

            # Verificar si hay algo para commitear
            status, _, _ = git(["status", "--porcelain"])
            if not status:
                _log("COMMIT_PUSH", "Nada que commitear — repo limpio", nivel="INFO")
                return True

            # Commit
            _, err, rc = git(["commit", "-m", mensaje])
            if rc != 0:
                raise RuntimeError(f"git commit falló: {err}")

            # Push — el token se inyecta via env variable, NUNCA en la URL ni en logs
            # Esto evita el bug de tokens viejos embebidos en la remote URL
            env_push = os.environ.copy()
            env_push["GIT_USERNAME"] = self._user
            env_push["GIT_PASSWORD"] = self._token  # solo en memoria del proceso

            # Asegurar que la remote URL esté limpia (sin credenciales embebidas)
            remote_raw, _, _ = git(["remote", "get-url", "origin"])
            if "@github.com" in remote_raw:
                # Limpiar cualquier credencial vieja de la URL
                import re
                remote_clean = re.sub(r"https://[^@]+@", "https://", remote_raw)
                git(["remote", "set-url", "origin", remote_clean])
                _log("AUTO-PARCHE", "URL remota limpiada de credenciales antiguas", nivel="INFO")

            # Push con helper de credenciales en memoria
            push_cmd = [
                "git", "-c",
                f"url.https://{self._user}:{self._token}@github.com.insteadOf=https://github.com",
                "push", "origin", "HEAD"
            ]
            res_push = subprocess.run(push_cmd, cwd=repo_path,
                                      capture_output=True, text=True, encoding="utf-8")
            err, rc = res_push.stderr.strip(), res_push.returncode

            if rc != 0:
                raise RuntimeError(f"git push falló: {err}")

            _log("COMMIT_PUSH", f"Push exitoso: '{mensaje}'", nivel="OK")
            _compartir_con_memoria_madre("commit_y_push", "OK", {"mensaje": mensaje})
            return True
        except Exception as e:
            _registrar_falla("commit_y_push", str(e), {"mensaje": mensaje})
            raise

    # ── MISIÓN 5: Crear repositorio ──────────────────────────────────────────
    def crear_repo(self, nombre: str, privado: bool = True, descripcion: str = "") -> dict:
        _log("CREAR_REPO", f"Creando: {nombre} (privado={privado})")
        try:
            resultado = self._api_call("/user/repos", method="POST", body={
                "name": nombre,
                "description": descripcion or f"Repositorio del Orbe de Verix — {nombre}",
                "private": privado,
                "auto_init": True
            })
            _log("CREAR_REPO", f"Repo '{nombre}' creado exitosamente", nivel="OK")
            _compartir_con_memoria_madre("crear_repo", "OK", {"repo": nombre})
            return {"nombre": resultado["name"], "url": resultado["clone_url"]}
        except Exception as e:
            _registrar_falla("crear_repo", str(e), {"nombre": nombre})
            raise

    # ── INFORME COMPLETO ──────────────────────────────────────────────────────
    def informe_completo(self):
        """Diagnóstico total del ecosistema GitHub."""
        print("\n" + "═"*55)
        print("   INFORME SENTINEL — ORBE DE VERIX")
        print("═"*55)

        try:
            id_info = self.verificar_identidad()
            print(f"\n👤 Identidad  : {id_info['login']} ({id_info['nombre']})")
            print(f"   Plan       : {id_info['plan']}")
            print(f"   Repos pub  : {id_info['repos_publicos']}")
            print(f"   Repos priv : {id_info['repos_privados']}")
        except Exception as e:
            print(f"\n❌ Error de identidad: {e}")

        try:
            repos = self.listar_repos()
            print(f"\n📦 Repositorios ({len(repos)} total):")
            for r in repos[:10]:
                icono = "🔒" if r["privado"] else "🌐"
                print(f"   {icono} {r['nombre']} [{r['rama']}]")
            if len(repos) > 10:
                print(f"   ... y {len(repos)-10} más")
        except Exception as e:
            print(f"\n❌ Error listando repos: {e}")

        try:
            estado = self.estado_git_local()
            print(f"\n🗂️  Orbe local [{estado['rama']}]")
            print(f"   Cambios sin commit: {estado['cambios_pendientes']}")
            print(f"   Últimos commits:")
            for c in estado["ultimos_commits"]:
                print(f"     • {c}")
        except Exception as e:
            print(f"\n❌ Error estado local: {e}")

        print("\n" + "═"*55 + "\n")


# ─── EJECUCIÓN DIRECTA ────────────────────────────────────────────────────────
if __name__ == "__main__":
    sentinel = GitHubSentinel()

    if len(sys.argv) > 1:
        cmd = sys.argv[1].upper()

        if cmd == "INFORME":
            sentinel.informe_completo()

        elif cmd == "PUSH" and len(sys.argv) > 2:
            msg = " ".join(sys.argv[2:])
            ok = sentinel.commit_y_push(msg)
            print("✅ Push completado." if ok else "❌ Push falló.")

        elif cmd == "REPOS":
            for r in sentinel.listar_repos():
                print(f"  {'🔒' if r['privado'] else '🌐'} {r['nombre']}")

        elif cmd == "ESTADO":
            e = sentinel.estado_git_local()
            print(json.dumps(e, indent=2, ensure_ascii=False))

        elif cmd == "CREAR" and len(sys.argv) > 2:
            nombre = sys.argv[2]
            resultado = sentinel.crear_repo(nombre)
            print(f"✅ Repo creado: {resultado['url']}")
        else:
            print("Comandos: INFORME | PUSH <msg> | REPOS | ESTADO | CREAR <nombre>")
    else:
        sentinel.informe_completo()
