# -*- coding: utf-8 -*-
"""
CEREBRO ORBE — Orquestador Maestro del Batallón de Verix
=========================================================
El comandante supremo que:
  ✦ Monitorea la salud de cada soldado en tiempo real
  ✦ Detecta patrones de falla y activa protocolos de recuperación
  ✦ Calcula el estado vital del Orbe (score de salud 0-100)
  ✦ Ordena sincronizaciones automáticas con GitHub
  ✦ Agenda tareas periódicas sin intervención humana
  ✦ Se auto-reporta a la Memoria Madre

Principio de diseño: LIVIANO — el Cerebro observa, no ejecuta.
                     Delega todo a los soldados especializados.

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timedelta
from typing import Optional

# ─── PATH DEL ORBE ───────────────────────────────────────────────────────────
ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ORBE_ROOT)

# ─── RUTAS ─────────────────────────────────────────────────────────────────────
SANTUARIO       = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
BATALLON_DIR    = os.path.join(ORBE_ROOT, "batallon")
REGISTROS_DIR   = os.path.join(SANTUARIO, "4_Registros_Del_Orbe")
LOG_CEREBRO     = os.path.join(REGISTROS_DIR, "cerebro_orbe.log")
ESTADO_ORBE     = os.path.join(SANTUARIO, "estado_orbe.json")
AUTO_AGENDA     = os.path.join(REGISTROS_DIR, "agenda_automatica.json")

os.makedirs(REGISTROS_DIR, exist_ok=True)

# ─── REGISTRO DE SOLDADOS CONOCIDOS ──────────────────────────────────────────
SOLDADOS_REGISTRO = {
    "SENTINEL":      {"archivo": "soldado_github_sentinel.py", "critico": True},
    "OIDO":          {"archivo": "soldado_oido.py",            "critico": False},
    "VISION":        {"archivo": "soldado_vision.py",          "critico": False},
    "ENCAPSULADOR":  {"archivo": "soldado_encapsulador.py",    "critico": False},
    "VAULT":         {"archivo": "vault_soldier.py",           "critico": True},
    "MEMORIA_MADRE": {"archivo": "memoria_madre.py",           "critico": True},
    "BUS_MENSAJES":  {"archivo": "bus_mensajes.py",            "critico": False},
}

# ─── LOGGER ──────────────────────────────────────────────────────────────────
def _log(nivel: str, msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{ts} | CEREBRO | {nivel:<10} | {msg}\n"
    with open(LOG_CEREBRO, "a", encoding="utf-8") as f:
        f.write(linea)
    print(f"[CEREBRO] [{nivel}] {msg}")


# ─── CLASE CEREBRO ────────────────────────────────────────────────────────────
class CerebroOrbe:
    """
    Mente central del Batallón.
    Orquesta, monitorea y mantiene vivo al ecosistema.
    """

    def __init__(self):
        _log("BOOT", "Cerebro en línea. Iniciando diagnóstico del Batallón...")
        self._inicio = datetime.now()

    # ── SALUD DEL BATALLÓN ────────────────────────────────────────────────────
    def diagnosticar_batallon(self) -> dict:
        """
        Revisa la integridad física de cada soldado.
        Calcula un score de salud del Orbe (0-100).
        """
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "soldados": {},
            "score_salud": 0,
            "soldados_ok": 0,
            "soldados_falla": 0,
            "criticos_offline": []
        }

        puntos = 0
        max_puntos = 0

        for nombre, cfg in SOLDADOS_REGISTRO.items():
            ruta = os.path.join(BATALLON_DIR, cfg["archivo"])
            existe = os.path.exists(ruta)
            peso = 15 if cfg["critico"] else 8
            max_puntos += peso

            if existe:
                size = os.path.getsize(ruta)
                # Verificar que no esté vacío o corrupto
                sano = size > 100
                puntos += peso if sano else (peso // 2)

                resultado["soldados"][nombre] = {
                    "estado": "ACTIVO" if sano else "DEGRADADO",
                    "ruta": ruta,
                    "size_bytes": size,
                    "critico": cfg["critico"]
                }
                resultado["soldados_ok"] += 1
                _log("OK" if sano else "ALERTA",
                     f"[{nombre}] {'✓' if sano else '⚠'} {cfg['archivo']} ({size}b)")
            else:
                resultado["soldados"][nombre] = {
                    "estado": "AUSENTE",
                    "ruta": ruta,
                    "critico": cfg["critico"]
                }
                resultado["soldados_falla"] += 1
                if cfg["critico"]:
                    resultado["criticos_offline"].append(nombre)
                _log("CRITICO" if cfg["critico"] else "ALERTA",
                     f"[{nombre}] ✗ AUSENTE — {cfg['archivo']}")

        resultado["score_salud"] = round((puntos / max(max_puntos, 1)) * 100, 1)
        _log("SALUD", f"Score del Orbe: {resultado['score_salud']}% "
                      f"({resultado['soldados_ok']} activos, "
                      f"{resultado['soldados_falla']} ausentes)")
        return resultado

    # ── ESTADO DE LA MEMORIA MADRE ────────────────────────────────────────────
    def leer_inteligencia(self) -> dict:
        """Lee el estado de la Memoria Madre y extrae insights."""
        try:
            from batallon.memoria_madre import MemoriaMadre
            mm = MemoriaMadre()
            informe = mm.informe_batallón()
            _log("INTEL", f"Tasa de éxito global: {informe.get('tasa_exito', 0)}%")
            return informe
        except Exception as e:
            _log("ALERTA", f"No pude leer la Memoria Madre: {e}")
            return {}

    # ── LECTURA DEL BUS DE MENSAJES ───────────────────────────────────────────
    def procesar_mensajes_pendientes(self) -> list:
        """Lee mensajes del bus inter-soldado y los despacha."""
        try:
            from batallon.bus_mensajes import BusMensajes
            bus = BusMensajes()
            mensajes = bus.leer_mensajes(destinatario="CEREBRO")
            for msg in mensajes:
                _log("BUS", f"Mensaje de {msg.get('origen')}: {msg.get('contenido')}")
                bus.marcar_leido(msg["id"])
            return mensajes
        except Exception as e:
            _log("AVISO", f"Bus de mensajes no disponible: {e}")
            return []

    # ── SINCRONIZACIÓN AUTOMÁTICA CON GITHUB ─────────────────────────────────
    def sync_github(self, mensaje_commit: Optional[str] = None) -> bool:
        """
        Ordena al Sentinel que sincronice el Orbe con GitHub.
        Solo lo hace si hay cambios reales.
        """
        _log("SYNC", "Iniciando sincronización GitHub via Sentinel...")
        try:
            # Verificar si hay cambios
            res = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=ORBE_ROOT, capture_output=True, text=True, encoding="utf-8"
            )
            if not res.stdout.strip():
                _log("SYNC", "Repo limpio — sin cambios para sincronizar.")
                return True

            cambios = len(res.stdout.strip().splitlines())
            msg = mensaje_commit or f"Cerebro Orbe: auto-sync [{cambios} cambios] {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            from batallon.soldado_github_sentinel import GitHubSentinel
            sentinel = GitHubSentinel()
            ok = sentinel.commit_y_push(msg)

            if ok:
                _log("SYNC", f"✓ Sincronizado con GitHub: '{msg}'")
            else:
                _log("ALERTA", "Sync falló — Sentinel reportó error.")
            return ok
        except Exception as e:
            _log("CRITICO", f"Error en sync_github: {str(e)[:100]}")
            return False

    # ── AGENDA AUTOMÁTICA ─────────────────────────────────────────────────────
    def registrar_tarea_agenda(self, nombre: str, intervalo_horas: int,
                                accion: str, params: dict = None):
        """Programa una tarea recurrente para el Cerebro."""
        agenda = {}
        if os.path.exists(AUTO_AGENDA):
            try:
                with open(AUTO_AGENDA, "r", encoding="utf-8") as f:
                    agenda = json.load(f)
            except:
                pass

        agenda[nombre] = {
            "accion": accion,
            "intervalo_horas": intervalo_horas,
            "proxima_ejecucion": (
                datetime.now() + timedelta(hours=intervalo_horas)
            ).isoformat(),
            "ultima_ejecucion": None,
            "params": params or {},
            "ejecuciones": 0
        }

        with open(AUTO_AGENDA, "w", encoding="utf-8") as f:
            json.dump(agenda, f, indent=2, ensure_ascii=False)
        _log("AGENDA", f"Tarea '{nombre}' programada cada {intervalo_horas}h")

    def ejecutar_agenda_pendiente(self) -> list:
        """Ejecuta las tareas que ya vencieron su tiempo de espera."""
        if not os.path.exists(AUTO_AGENDA):
            return []

        try:
            with open(AUTO_AGENDA, "r", encoding="utf-8") as f:
                agenda = json.load(f)
        except:
            return []

        ejecutadas = []
        ahora = datetime.now()

        for nombre, tarea in agenda.items():
            proxima = datetime.fromisoformat(tarea["proxima_ejecucion"])
            if ahora >= proxima:
                _log("AGENDA", f"Ejecutando tarea vencida: '{nombre}'")
                try:
                    accion = tarea["accion"]

                    if accion == "sync_github":
                        self.sync_github(f"Agenda: {nombre}")
                    elif accion == "diagnosticar":
                        self.diagnosticar_batallon()
                    elif accion == "compactar_memoria":
                        from batallon.memoria_madre import MemoriaMadre
                        MemoriaMadre().compactar_memoria()

                    # Reagendar
                    tarea["ultima_ejecucion"] = ahora.isoformat()
                    tarea["proxima_ejecucion"] = (
                        ahora + timedelta(hours=tarea["intervalo_horas"])
                    ).isoformat()
                    tarea["ejecuciones"] = tarea.get("ejecuciones", 0) + 1
                    ejecutadas.append(nombre)
                except Exception as e:
                    _log("ALERTA", f"Error ejecutando '{nombre}': {e}")

        if ejecutadas:
            with open(AUTO_AGENDA, "w", encoding="utf-8") as f:
                json.dump(agenda, f, indent=2, ensure_ascii=False)

        return ejecutadas

    # ── ESTADO GLOBAL PERSISTIDO ──────────────────────────────────────────────
    def guardar_estado_orbe(self, diagnostico: dict, intel: dict):
        """Persiste el estado actual del Orbe para consulta rápida."""
        estado = {
            "ultima_actualizacion": datetime.now().isoformat(),
            "uptime_segundos": (datetime.now() - self._inicio).seconds,
            "score_salud": diagnostico.get("score_salud", 0),
            "soldados_activos": diagnostico.get("soldados_ok", 0),
            "soldados_falla": diagnostico.get("soldados_falla", 0),
            "tasa_exito_global": intel.get("tasa_exito", 0),
            "criticos_offline": diagnostico.get("criticos_offline", []),
            "detalle": diagnostico.get("soldados", {})
        }
        with open(ESTADO_ORBE, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)
        return estado

    # ── INFORME COMPLETO ──────────────────────────────────────────────────────
    def informe_completo(self, sync: bool = False):
        """Diagnóstico total del Orbe con representación visual."""
        print("\n" + "╔" + "═"*58 + "╗")
        print("║" + "   🧠 CEREBRO ORBE — ESTADO DEL BATALLÓN VERIX".center(58) + "║")
        print("╚" + "═"*58 + "╝")

        diag = self.diagnosticar_batallon()
        intel = self.leer_inteligencia()
        self.guardar_estado_orbe(diag, intel)

        # Score visual
        score = diag["score_salud"]
        barras = int(score / 5)
        color_bar = "█" * barras + "░" * (20 - barras)
        estado_txt = "ÓPTIMO" if score >= 85 else "ESTABLE" if score >= 60 else "DEGRADADO"
        print(f"\n  🔋 Salud del Orbe: [{color_bar}] {score}% — {estado_txt}")
        print(f"  ⚔️  Soldados activos : {diag['soldados_ok']} / {len(SOLDADOS_REGISTRO)}")

        if diag["criticos_offline"]:
            print(f"\n  ⚠️  CRÍTICOS OFFLINE: {', '.join(diag['criticos_offline'])}")

        print(f"\n  📊 Inteligencia colectiva:")
        print(f"     Tasa de éxito  : {intel.get('tasa_exito', 'N/A')}%")
        print(f"     Total ops      : {intel.get('total_operaciones', 0)}")
        print(f"     Fallas totales : {intel.get('total_fallas', 0)}")

        # Agenda
        ejecutadas = self.ejecutar_agenda_pendiente()
        if ejecutadas:
            print(f"\n  📅 Agenda ejecutada: {', '.join(ejecutadas)}")

        # Mensajes del bus
        msgs = self.procesar_mensajes_pendientes()
        if msgs:
            print(f"\n  📨 Mensajes procesados: {len(msgs)}")

        # Sync opcional
        if sync:
            print(f"\n  📤 Sincronizando con GitHub...")
            self.sync_github()

        print("\n" + "═"*60 + "\n")


# ─── EJECUCIÓN DIRECTA ────────────────────────────────────────────────────────
if __name__ == "__main__":
    cerebro = CerebroOrbe()

    cmd = sys.argv[1].upper() if len(sys.argv) > 1 else "INFORME"

    if cmd == "INFORME":
        cerebro.informe_completo()

    elif cmd == "SYNC":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        cerebro.sync_github(msg)

    elif cmd == "DIAGNOSTICO":
        d = cerebro.diagnosticar_batallon()
        print(json.dumps(d, indent=2, ensure_ascii=False))

    elif cmd == "AGENDA":
        # Registrar agenda por defecto
        cerebro.registrar_tarea_agenda("sync_diario",     intervalo_horas=24, accion="sync_github")
        cerebro.registrar_tarea_agenda("diagnostico_6h",  intervalo_horas=6,  accion="diagnosticar")
        cerebro.registrar_tarea_agenda("compactar_7d",    intervalo_horas=168, accion="compactar_memoria")
        print("✅ Agenda configurada: sync cada 24h | diagnóstico cada 6h | compactar cada 7d")

    elif cmd == "INFORME_SYNC":
        cerebro.informe_completo(sync=True)

    else:
        print("Comandos: INFORME | SYNC [msg] | DIAGNOSTICO | AGENDA | INFORME_SYNC")
