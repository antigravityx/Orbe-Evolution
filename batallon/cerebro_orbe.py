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
    "ESCUDO":        {"archivo": "soldado_escudo.py",          "critico": False},
    "GOD_MODE":      {"archivo": "god_mode_core.py",           "critico": True},
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

    # ── SUEÑO: LATIDO DEL NIDO (PUSH SILENCIOSO) ──────────────────────────────
    def latido_nido(self) -> bool:
        """Monitorea tareas.md y sincroniza si hay cambios (Push Silencioso)."""
        tareas_path = os.path.join(ORBE_ROOT, "batallon", "tareas.md")
        if not os.path.exists(tareas_path): return False
        
        # Calculamos hash rápido para ver si cambió
        with open(tareas_path, "rb") as f:
            current_hash = hashlib.md5(f.read()).hexdigest()
            
        # Aquí podríamos guardar el hash anterior en un estado temporal
        _log("LATIDO", "Analizando el pulso de tareas.md...")
        # Si detectamos cambios, disparamos el Latido Eterno
        return self.sync_github("Latido Silencioso: Evolución en tareas.md detectada.")

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
                    elif accion == "latido_nido":
                        self.latido_nido()
                    elif accion == "compactar_memoria":
                        from batallon.memoria_madre import MemoriaMadre
                        MemoriaMadre().compactar_memoria()
                    elif accion == "limpiar_santuario":
                        from batallon.soldado_escudo import EscudoSantuario
                        EscudoSantuario().ejecutar_limpieza()
                    elif accion == "chequeo_god_mode":
                        # Llamar al God Mode Core
                        ruta_god = os.path.join(ORBE_ROOT, "god_mode_core.py")
                        subprocess.run([sys.executable, ruta_god], capture_output=True)

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
        cerebro.registrar_tarea_agenda("sync_diario",           intervalo_horas=24,  accion="sync_github")
        cerebro.registrar_tarea_agenda("diagnostico_6h",        intervalo_horas=6,   accion="diagnosticar")
        cerebro.registrar_tarea_agenda("latido_nido_1h",        intervalo_horas=1,   accion="latido_nido")
        cerebro.registrar_tarea_agenda("compactar_7d",          intervalo_horas=168, accion="compactar_memoria")
        cerebro.registrar_tarea_agenda("limpieza_santuario_24h",intervalo_horas=24,  accion="limpiar_santuario")
        cerebro.registrar_tarea_agenda("chequeo_god_mode_1h",   intervalo_horas=1,   accion="chequeo_god_mode")
        print("✅ Agenda configurada: sync cada 24h | diagnóstico cada 6h | latido cada 1h | compactar cada 7d | limpieza cada 24h | God Mode cada 1h")

    elif cmd == "RUN":
        from concurrent.futures import ThreadPoolExecutor
        import traceback
        
        _log("LOOP", "Iniciando modo Comandante Multihilo (vigilancia y despacho)...")
        # El pool mantiene vivos hasta 4 soldados a la vez, compartiendo memoria
        with ThreadPoolExecutor(max_workers=4, thread_name_prefix="Soldado_") as executor:
            while True:
                try:
                    cerebro.ejecutar_agenda_pendiente()
                    mensajes = cerebro.procesar_mensajes_pendientes()
                    
                    # Despachar misiones asíncronas desde el Bus
                    for msg in mensajes:
                        if msg.get("tipo") == "ORDEN":
                            dest = msg.get("destinatario", "")
                            
                            if "OIDO" in dest:
                                from batallon import soldado_oido
                                _log("DESPACHO", f"Asignando misión a OIDO en segundo plano (Ticket: {msg.get('contenido')})")
                                executor.submit(soldado_oido.ejecutar_mision, msg.get("contenido"))
                                
                            elif "VAULT" in dest:
                                from batallon import vault_soldier
                                _log("DESPACHO", "Asignando tarea al VAULT en segundo plano")
                                # Ejemplo: listar y loguear
                                v = vault_soldier.VaultOrbe()
                                executor.submit(v.listar_entradas)
                                
                    # Ciclo más corto para ser reactivos sin asfixiar la CPU
                    time.sleep(30)
                except KeyboardInterrupt:
                    _log("SHUTDOWN", "Cerebro apagándose por interrupción manual...")
                    break
                except Exception as e:
                    _log("CRITICO", f"Error en loop principal: {e}\n{traceback.format_exc()}")
                    time.sleep(60)

    elif cmd == "INFORME_SYNC":
        cerebro.informe_completo(sync=True)

    else:
        print("Comandos: INFORME | SYNC [msg] | DIAGNOSTICO | AGENDA | INFORME_SYNC")
