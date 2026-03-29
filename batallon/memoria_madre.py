# -*- coding: utf-8 -*-
"""
MEMORIA MADRE — Inteligencia Global del Batallón Verix
======================================================
El cerebro colectivo que une a todos los soldados.

Arquitectura:
  - Cada soldado escribe sus aprendizajes, fallas y parches aquí
  - La Memoria Madre indexa patrones, estadísticas y sabiduría colectiva
  - Los soldados pueden consultar la sabiduría de sus hermanos
  - Se auto-compacta para no consumir demasiado disco

Funciones clave:
  - registrar_aprendizaje(soldado, evento, datos)
  - consultar_patrones(tipo_falla)
  - obtener_sabiduría_colectiva()
  - compactar_memoria()

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional

# ─── RUTAS ───────────────────────────────────────────────────────────────────
SANTUARIO = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
MEMORIA_PATH    = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "memoria_madre.json")
PATRONES_PATH   = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "patrones_globales.json")
SABIDURÍA_PATH  = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "sabiduria_colectiva.json")
LOG_PATH        = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "memoria_madre.log")

MAX_EVENTOS_POR_SOLDADO = 200   # límite para no inflar la memoria
MAX_PATRONES_GLOBALES   = 500   # patrones de fallas/éxitos indexados

os.makedirs(os.path.join(SANTUARIO, "4_Registros_Del_Orbe"), exist_ok=True)


# ─── ESTRUCTURA DE LA MEMORIA ─────────────────────────────────────────────────
ESTRUCTURA_BASE = {
    "version": "2.0",
    "creada": datetime.now().isoformat(),
    "ultima_compactacion": None,
    "soldados": {},          # Historia de cada soldado
    "stats_globales": {
        "total_operaciones": 0,
        "total_exitosas": 0,
        "total_fallas": 0,
        "soldados_activos": []
    }
}


# ─── CLASE MEMORIA MADRE ─────────────────────────────────────────────────────
class MemoriaMadre:
    """
    El cerebro colectivo del Batallón.
    Todos los soldados depositan aquí su sabiduría.
    """

    def __init__(self):
        self._memoria = self._cargar()

    def _log(self, msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} | [MEMORIA_MADRE] {msg}\n")

    def _cargar(self) -> dict:
        if os.path.exists(MEMORIA_PATH):
            try:
                with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Migración: si es formato viejo (del sentinel anterior), convertir
                if "stats_globales" not in data:
                    migrada = dict(ESTRUCTURA_BASE)
                    migrada["creada"] = datetime.now().isoformat()
                    # Intentar rescatar datos de soldados en formato viejo
                    for key, val in data.items():
                        if isinstance(val, dict) and "operaciones" in val:
                            migrada["soldados"][key] = {
                                "primera_activacion": datetime.now().isoformat(),
                                "eventos": val.get("operaciones", []),
                                "stats": val.get("stats", {"ops": 0, "ok": 0, "fallas": 0}),
                                "fallas_conocidas": {},
                                "parches_aplicados": []
                            }
                    self._log("MIGRACIÓN: formato legado detectado y convertido")
                    return migrada
                return data
            except:
                pass
        return dict(ESTRUCTURA_BASE)


    def _guardar(self):
        with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
            json.dump(self._memoria, f, indent=2, ensure_ascii=False)

    # ── API principal ─────────────────────────────────────────────────────────

    def registrar_aprendizaje(self, soldado: str, operacion: str,
                               resultado: str, datos: dict = None,
                               es_falla: bool = False):
        """
        Un soldado deposita un aprendizaje en la memoria colectiva.
        resultado: "OK" | "FALLA" | "ADVERTENCIA"
        """
        ts = datetime.now().isoformat()
        evento = {
            "ts": ts,
            "operacion": operacion,
            "resultado": resultado,
            "datos": datos or {},
            "es_falla": es_falla
        }

        # Registro por soldado
        soldado_data = self._memoria["soldados"].setdefault(soldado, {
            "primera_activacion": ts,
            "eventos": [],
            "stats": {"ops": 0, "ok": 0, "fallas": 0},
            "fallas_conocidas": {},
            "parches_aplicados": []
        })

        soldado_data["eventos"].append(evento)
        soldado_data["ultima_actividad"] = ts
        soldado_data["stats"]["ops"] += 1

        if resultado == "OK":
            soldado_data["stats"]["ok"] += 1
        elif es_falla or resultado == "FALLA":
            soldado_data["stats"]["fallas"] += 1
            # Indexar la falla para consulta futura
            falla_hash = hashlib.sha256(operacion.encode()).hexdigest()[:12]
            soldado_data["fallas_conocidas"][falla_hash] = {
                "operacion": operacion,
                "ultima_vez": ts,
                "datos": datos or {}
            }

        # Límite de eventos por soldado (auto-compactación suave)
        if len(soldado_data["eventos"]) > MAX_EVENTOS_POR_SOLDADO:
            soldado_data["eventos"] = soldado_data["eventos"][-MAX_EVENTOS_POR_SOLDADO:]

        # Stats globales
        stats = self._memoria["stats_globales"]
        stats["total_operaciones"] += 1
        if resultado == "OK":
            stats["total_exitosas"] += 1
        elif es_falla:
            stats["total_fallas"] += 1
        if soldado not in stats["soldados_activos"]:
            stats["soldados_activos"].append(soldado)

        self._guardar()
        self._log(f"{soldado} | {operacion} | {resultado}")
        return evento

    def consultar_fallas_conocidas(self, operacion: str = None) -> dict:
        """
        Todos los soldados comparten sus fallas.
        Si operacion es None, retorna TODAS las fallas conocidas del batallón.
        """
        todas_las_fallas = {}
        for soldado, data in self._memoria["soldados"].items():
            for fid, falla in data.get("fallas_conocidas", {}).items():
                if operacion is None or operacion.lower() in falla["operacion"].lower():
                    todas_las_fallas[fid] = {
                        "soldado": soldado,
                        **falla
                    }
        return todas_las_fallas

    def registrar_parche(self, soldado: str, falla_id: str,
                          descripcion: str, codigo_parche: str = ""):
        """Un soldado crea un parche — queda disponible para todos."""
        parche = {
            "falla_id": falla_id,
            "descripcion": descripcion,
            "codigo_parche": codigo_parche,
            "creado_por": soldado,
            "ts": datetime.now().isoformat(),
            "adoptado_por": [soldado]
        }

        soldado_data = self._memoria["soldados"].get(soldado, {})
        soldado_data.setdefault("parches_aplicados", []).append(parche)
        self._guardar()

        # Indexar en sabiduría colectiva
        sabiduria = {}
        if os.path.exists(SABIDURÍA_PATH):
            try:
                with open(SABIDURÍA_PATH, "r", encoding="utf-8") as f:
                    sabiduria = json.load(f)
            except:
                pass

        sabiduria[falla_id] = parche
        with open(SABIDURÍA_PATH, "w", encoding="utf-8") as f:
            json.dump(sabiduria, f, indent=2, ensure_ascii=False)

        self._log(f"PARCHE CREADO por {soldado}: {descripcion}")
        return parche

    def obtener_sabiduria_colectiva(self) -> dict:
        """Todos los parches disponibles para cualquier soldado."""
        if os.path.exists(SABIDURÍA_PATH):
            try:
                with open(SABIDURÍA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def informe_batallón(self) -> dict:
        """Estado completo de toda la inteligencia acumulada."""
        stats = self._memoria["stats_globales"]
        informe = {
            "total_operaciones": stats["total_operaciones"],
            "tasa_exito": round(
                stats["total_exitosas"] / max(stats["total_operaciones"], 1) * 100, 1
            ),
            "total_fallas": stats["total_fallas"],
            "soldados_activos": stats["soldados_activos"],
            "detalle_soldados": {}
        }
        for soldado, data in self._memoria["soldados"].items():
            s = data["stats"]
            informe["detalle_soldados"][soldado] = {
                "ops": s["ops"],
                "ok": s["ok"],
                "fallas": s["fallas"],
                "eficiencia": round(s["ok"] / max(s["ops"], 1) * 100, 1),
                "fallas_catalogadas": len(data.get("fallas_conocidas", {})),
                "parches_creados": len(data.get("parches_aplicados", [])),
                "ultima_actividad": data.get("ultima_actividad", "nunca")
            }
        return informe

    def compactar_memoria(self):
        """
        Reduce el tamaño descartando eventos viejos exitosos
        y preservando TODAS las fallas y parches.
        """
        for soldado, data in self._memoria["soldados"].items():
            eventos = data.get("eventos", [])
            # Preservar todas las fallas, comprimir los éxitos
            fallas = [e for e in eventos if e.get("es_falla")]
            exitos = [e for e in eventos if not e.get("es_falla")]
            # Mantener últimos 50 éxitos y todas las fallas (max 100)
            data["eventos"] = exitos[-50:] + fallas[-100:]

        self._memoria["ultima_compactacion"] = datetime.now().isoformat()
        self._guardar()
        self._log("MEMORIA COMPACTADA — fallas preservadas, éxitos podados")


# ─── DECORADOR PARA SOLDADOS ──────────────────────────────────────────────────
def con_memoria(soldado_nombre: str):
    """
    Decorador que cualquier soldado puede usar para auto-reportar
    a la Memoria Madre sin escribir código extra.

    Uso:
        @con_memoria("MI_SOLDADO")
        def mi_operacion(parametros):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            mm = MemoriaMadre()
            try:
                resultado = func(*args, **kwargs)
                mm.registrar_aprendizaje(
                    soldado_nombre, func.__name__, "OK",
                    {"args_count": len(args)}
                )
                return resultado
            except Exception as e:
                mm.registrar_aprendizaje(
                    soldado_nombre, func.__name__, "FALLA",
                    {"error": str(e)[:200]}, es_falla=True
                )
                raise
        return wrapper
    return decorator


# ─── EJECUCIÓN DIRECTA ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    mm = MemoriaMadre()
    cmd = sys.argv[1].upper() if len(sys.argv) > 1 else "INFORME"

    if cmd == "INFORME":
        informe = mm.informe_batallón()
        print("\n" + "═"*60)
        print("   MEMORIA MADRE — INTELIGENCIA COLECTIVA DEL BATALLÓN")
        print("═"*60)
        print(f"\n📊 Total operaciones : {informe['total_operaciones']}")
        print(f"   Tasa de éxito     : {informe['tasa_exito']}%")
        print(f"   Fallas totales    : {informe['total_fallas']}")
        print(f"   Soldados activos  : {len(informe['soldados_activos'])}")

        print(f"\n👥 Detalle por soldado:")
        for nombre, s in informe["detalle_soldados"].items():
            barra = "█" * int(s["eficiencia"] / 10) + "░" * (10 - int(s["eficiencia"] / 10))
            print(f"\n   ⚔️  {nombre}")
            print(f"      Eficiencia: [{barra}] {s['eficiencia']}%")
            print(f"      Ops: {s['ops']} | OK: {s['ok']} | Fallas: {s['fallas']}")
            print(f"      Fallas catalogadas: {s['fallas_catalogadas']}")
            print(f"      Parches creados   : {s['parches_creados']}")
            print(f"      Último reporte    : {s['ultima_actividad'][:19]}")

        sabiduria = mm.obtener_sabiduria_colectiva()
        if sabiduria:
            print(f"\n🧠 Sabiduría colectiva: {len(sabiduria)} parches disponibles")

        print("\n" + "═"*60 + "\n")

    elif cmd == "FALLAS":
        fallas = mm.consultar_fallas_conocidas()
        print(f"\n🔴 Fallas conocidas en el batallón: {len(fallas)}")
        for fid, f in fallas.items():
            print(f"   [{fid}] {f['soldado']} — {f['operacion']} ({f['ultima_vez'][:10]})")

    elif cmd == "COMPACTAR":
        mm.compactar_memoria()
        print("✅ Memoria compactada.")

    else:
        print("Comandos: INFORME | FALLAS | COMPACTAR")
