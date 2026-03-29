# -*- coding: utf-8 -*-
"""
BUS DE MENSAJES — Sistema de Comunicación Inter-Soldado del Batallón
=====================================================================
Permite que los soldados se comuniquen entre sí sin acoplarse directamente.

Arquitectura:
  - Mensajes persistidos en JSON (liviano, sin dependencias extra)
  - Cada mensaje tiene: origen, destino, tipo, contenido, timestamp, estado
  - Los soldados pueden suscribirse a tipos de mensajes
  - El Cerebro Orbe actúa como router principal
  - Mensajes expirados se limpian automáticamente

Tipos de mensaje:
  ALERTA    — urgente, para el Cerebro
  PARCHE    — un soldado encontró solución a una falla compartida
  DATOS     — compartir estadísticas o resultados
  ORDEN     — el Cerebro le ordena algo a un soldado
  RESPUESTA — respuesta a una orden anterior

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta

# ─── PATH DEL ORBE ───────────────────────────────────────────────────────────
ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ─── RUTAS ────────────────────────────────────────────────────────────────────
SANTUARIO   = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
BUS_PATH    = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "bus_mensajes.json")
LOG_PATH    = os.path.join(SANTUARIO, "4_Registros_Del_Orbe", "bus_mensajes.log")
EXPIRACION_HORAS = 48   # Mensajes se descartan tras 48h

os.makedirs(os.path.dirname(BUS_PATH), exist_ok=True)


# ─── CLASE BUS ────────────────────────────────────────────────────────────────
class BusMensajes:
    """
    Canal de comunicación entre todos los soldados del Batallón.
    Thread-safe mediante escritura atómica (JSON pequeño).
    """

    # ── Tipos válidos ─────────────────────────────────────────────────────────
    TIPOS = {"ALERTA", "PARCHE", "DATOS", "ORDEN", "RESPUESTA", "INFO", "HEARTBEAT"}
    TODOS = "__BROADCAST__"    # Destinatario para mensajes a todos

    def __init__(self):
        self._bus = self._cargar()

    def _log(self, msg: str):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} | BUS | {msg}\n")

    def _cargar(self) -> list:
        if os.path.exists(BUS_PATH):
            try:
                with open(BUS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _guardar(self):
        with open(BUS_PATH, "w", encoding="utf-8") as f:
            json.dump(self._bus, f, indent=2, ensure_ascii=False)

    # ── ENVIAR MENSAJE ────────────────────────────────────────────────────────
    def enviar(self, origen: str, destinatario: str, tipo: str,
               contenido: str, datos: dict = None) -> str:
        """
        Publica un mensaje en el bus.
        Retorna el ID del mensaje.
        """
        if tipo not in self.TIPOS:
            tipo = "INFO"

        msg_id = str(uuid.uuid4())[:12]
        mensaje = {
            "id":           msg_id,
            "origen":       origen,
            "destinatario": destinatario,
            "tipo":         tipo,
            "contenido":    contenido,
            "datos":        datos or {},
            "timestamp":    datetime.now().isoformat(),
            "expira":       (datetime.now() + timedelta(hours=EXPIRACION_HORAS)).isoformat(),
            "leido":        False,
            "leido_por":    []
        }

        self._bus = self._cargar()   # Releer para evitar race conditions
        self._bus.append(mensaje)
        self._limpiar_expirados()
        self._guardar()

        self._log(f"[{tipo}] {origen} → {destinatario}: {contenido[:60]}")
        return msg_id

    # ── LEER MENSAJES ─────────────────────────────────────────────────────────
    def leer_mensajes(self, destinatario: str, tipo: str = None,
                       solo_no_leidos: bool = True) -> list:
        """
        Lee mensajes dirigidos a un soldado.
        Incluye mensajes de broadcast (TODOS).
        """
        self._bus = self._cargar()
        ahora = datetime.now()
        resultado = []

        for msg in self._bus:
            # Verificar destinatario
            es_para_mi = (
                msg["destinatario"] == destinatario or
                msg["destinatario"] == self.TODOS
            )
            if not es_para_mi:
                continue

            # Verificar expiración
            if datetime.fromisoformat(msg["expira"]) < ahora:
                continue

            # Verificar si ya fue leído
            if solo_no_leidos and destinatario in msg["leido_por"]:
                continue

            # Filtrar por tipo si se especifica
            if tipo and msg["tipo"] != tipo:
                continue

            resultado.append(msg)

        return resultado

    def marcar_leido(self, msg_id: str, por: str = ""):
        """Marca un mensaje como leído por un soldado."""
        self._bus = self._cargar()
        for msg in self._bus:
            if msg["id"] == msg_id:
                if por and por not in msg["leido_por"]:
                    msg["leido_por"].append(por)
                msg["leido"] = True
                break
        self._guardar()

    # ── BROADCAST ─────────────────────────────────────────────────────────────
    def broadcast(self, origen: str, tipo: str, contenido: str, datos: dict = None) -> str:
        """Envía un mensaje a TODOS los soldados."""
        return self.enviar(origen, self.TODOS, tipo, contenido, datos)

    # ── ALERTAS ───────────────────────────────────────────────────────────────
    def alerta(self, origen: str, descripcion: str, datos: dict = None) -> str:
        """Shortcut para enviar una alerta urgente al Cerebro."""
        return self.enviar(origen, "CEREBRO", "ALERTA", descripcion, datos)

    def compartir_parche(self, origen: str, falla_id: str,
                          descripcion: str, codigo: str = "") -> str:
        """Un soldado comparte un parche con todo el batallón."""
        return self.broadcast(origen, "PARCHE", descripcion, {
            "falla_id": falla_id,
            "codigo_parche": codigo
        })

    def heartbeat(self, soldado: str, estado: str = "OK", stats: dict = None) -> str:
        """Un soldado reporta que está vivo al Cerebro."""
        return self.enviar(soldado, "CEREBRO", "HEARTBEAT", estado, stats or {})

    # ── LIMPIEZA ──────────────────────────────────────────────────────────────
    def _limpiar_expirados(self):
        """Elimina mensajes vencidos del bus."""
        ahora = datetime.now()
        antes = len(self._bus)
        self._bus = [
            m for m in self._bus
            if datetime.fromisoformat(m["expira"]) > ahora
        ]
        eliminados = antes - len(self._bus)
        if eliminados > 0:
            self._log(f"Limpieza: {eliminados} mensajes expirados eliminados.")

    # ── INFORME DEL BUS ───────────────────────────────────────────────────────
    def informe(self) -> dict:
        """Estado actual del bus de mensajes."""
        self._bus = self._cargar()
        self._limpiar_expirados()

        stats = {"total": len(self._bus), "por_tipo": {}, "no_leidos": 0}
        for msg in self._bus:
            t = msg["tipo"]
            stats["por_tipo"][t] = stats["por_tipo"].get(t, 0) + 1
            if not msg["leido"]:
                stats["no_leidos"] += 1

        return stats


# ─── EJECUCIÓN DIRECTA ────────────────────────────────────────────────────────
if __name__ == "__main__":
    bus = BusMensajes()
    cmd = sys.argv[1].upper() if len(sys.argv) > 1 else "ESTADO"

    if cmd == "ESTADO":
        inf = bus.informe()
        print(f"\n📨 BUS DE MENSAJES — Orbe de Verix")
        print(f"   Total mensajes : {inf['total']}")
        print(f"   No leídos      : {inf['no_leidos']}")
        print(f"   Por tipo:")
        for t, c in inf["por_tipo"].items():
            print(f"     • {t}: {c}")

    elif cmd == "ENVIAR" and len(sys.argv) >= 5:
        # python -m batallon.bus_mensajes ENVIAR ORIGEN DEST TIPO "mensaje"
        msg_id = bus.enviar(sys.argv[2], sys.argv[3], sys.argv[4],
                             " ".join(sys.argv[5:]))
        print(f"✅ Mensaje enviado: {msg_id}")

    elif cmd == "BROADCAST" and len(sys.argv) >= 4:
        msg_id = bus.broadcast(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
        print(f"✅ Broadcast enviado: {msg_id}")

    elif cmd == "LEER" and len(sys.argv) >= 3:
        msgs = bus.leer_mensajes(sys.argv[2], solo_no_leidos=False)
        print(f"\n📬 Mensajes para '{sys.argv[2]}':")
        for m in msgs:
            print(f"  [{m['tipo']}] De: {m['origen']} | {m['contenido'][:60]}")

    else:
        print("Comandos: ESTADO | ENVIAR <orig> <dest> <tipo> <msg> | BROADCAST <orig> <tipo> <msg> | LEER <dest>")
