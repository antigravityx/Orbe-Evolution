# -*- coding: utf-8 -*-
"""
VAULT SOLDIER v2 — Corazón Blindado del Orbe de Verix
=====================================================
Misión: Custodia de secretos con encriptación de grado militar.
       Clave derivada de la máquina — el token solo vive aquí y en ningún otro lugar.
       NUNCA exponer secretos en logs, pantallas ni archivos externos.

Arquitectura:
  - Clave maestra = HMAC(hostname + username + salt_fijo)
  - Encriptación = AES-256-CFB
  - Almacenamiento = vault_militar.db (binario encriptado)
  - Todos los accesos quedan registrados sin exponer el dato

Autor: Verix — bajo el mandato de r1ch0n
"""

import os
import json
import hashlib
import hmac
import socket
import getpass
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ─── RUTAS DEL VAULT ────────────────────────────────────────────────────────
VAULT_PATH     = r"c:\Users\Usuario\Desktop\Orbe_Santuario\3_Llaves_Maestras\vault_orbital.db"
VAULT_LOG_PATH = r"c:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\vault_accesos.log"
SALT_FIJO      = b"ORB3_V3RIX_R1CH0N_ALMA_2026"   # sal interna del Orbe

# ─── DERIVACIÓN DE CLAVE DE MÁQUINA ─────────────────────────────────────────
def _derivar_clave_maquina() -> bytes:
    """
    Genera una clave AES-256 única para esta máquina.
    Combina hostname + username + salt — el resultado NO sale del proceso.
    """
    identidad = f"{socket.gethostname()}::{getpass.getuser()}".encode()
    clave = hmac.new(SALT_FIJO, identidad, hashlib.sha256).digest()
    return clave


# ─── CLASE VAULT ─────────────────────────────────────────────────────────────
class VaultOrbe:
    """
    Bóveda blindada del Orbe.
    La clave se deriva en tiempo de ejecución — nunca se persiste.
    """

    def __init__(self):
        self._key = _derivar_clave_maquina()
        os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(VAULT_LOG_PATH), exist_ok=True)

    # ── Registro interno (sin exponer secretos) ──────────────────────────────
    def _log(self, accion: str, entrada: str, resultado: str = "OK"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"{ts} | {accion:<20} | entrada={entrada:<25} | {resultado}\n"
        with open(VAULT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(linea)

    # ── Cifrado AES-256-CFB ──────────────────────────────────────────────────
    def _cifrar(self, data: dict) -> bytes:
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self._key), modes.CFB(iv), backend=default_backend())
        enc = cipher.encryptor()
        ciphertext = enc.update(json.dumps(data).encode("utf-8")) + enc.finalize()
        return iv + ciphertext

    def _descifrar(self, blob: bytes) -> dict:
        iv, ciphertext = blob[:16], blob[16:]
        cipher = Cipher(algorithms.AES(self._key), modes.CFB(iv), backend=default_backend())
        dec = cipher.decryptor()
        plain = dec.update(ciphertext) + dec.finalize()
        return json.loads(plain.decode("utf-8"))

    # ── Leer bóveda completa ─────────────────────────────────────────────────
    def _leer_vault(self) -> dict:
        if not os.path.exists(VAULT_PATH):
            return {}
        with open(VAULT_PATH, "rb") as f:
            blob = f.read()
        if not blob:
            return {}
        try:
            return self._descifrar(blob)
        except Exception:
            return {}

    # ── Escribir bóveda completa ─────────────────────────────────────────────
    def _escribir_vault(self, vault: dict):
        with open(VAULT_PATH, "wb") as f:
            f.write(self._cifrar(vault))

    # ── API pública ──────────────────────────────────────────────────────────
    def guardar(self, nombre: str, valor: str, categoria: str = "GENERAL") -> bool:
        """Guarda un secreto en el vault. El valor nunca se loguea."""
        try:
            vault = self._leer_vault()
            vault[nombre] = {
                "valor": valor,
                "categoria": categoria,
                "sellado_en": datetime.now().isoformat(),
                "checksum": hashlib.sha256(valor.encode()).hexdigest()[:12]  # solo huella
            }
            self._escribir_vault(vault)
            self._log("GUARDAR", nombre, f"checksum={vault[nombre]['checksum']}")
            return True
        except Exception as e:
            self._log("GUARDAR", nombre, f"ERROR:{str(e)[:50]}")
            return False

    def recuperar(self, nombre: str) -> str | None:
        """Recupera un secreto del vault. Solo retorna el valor, nada más."""
        try:
            vault = self._leer_vault()
            entry = vault.get(nombre)
            if entry:
                self._log("RECUPERAR", nombre, "CONCEDIDO")
                return entry["valor"]
            self._log("RECUPERAR", nombre, "NO_ENCONTRADO")
            return None
        except Exception as e:
            self._log("RECUPERAR", nombre, f"ERROR:{str(e)[:50]}")
            return None

    def existe(self, nombre: str) -> bool:
        vault = self._leer_vault()
        return nombre in vault

    def listar_entradas(self) -> list:
        """Lista los nombres de entradas y sus checksums — NUNCA los valores."""
        vault = self._leer_vault()
        resultado = []
        for nombre, meta in vault.items():
            resultado.append({
                "nombre": nombre,
                "categoria": meta.get("categoria", "?"),
                "sellado_en": meta.get("sellado_en", "?"),
                "checksum": meta.get("checksum", "?")
            })
        return resultado

    def eliminar(self, nombre: str) -> bool:
        try:
            vault = self._leer_vault()
            if nombre in vault:
                del vault[nombre]
                self._escribir_vault(vault)
                self._log("ELIMINAR", nombre, "BORRADO")
                return True
            return False
        except Exception as e:
            self._log("ELIMINAR", nombre, f"ERROR:{str(e)[:50]}")
            return False


# ─── EJECUCIÓN DIRECTA — SELLADO INICIAL ────────────────────────────────────
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════╗")
    print("║   VAULT SOLDIER — Orbe de Verix          ║")
    print("╚══════════════════════════════════════════╝\n")

    v = VaultOrbe()

    print("[VAULT] Listando entradas actuales:")
    for e in v.listar_entradas():
        print(f"  • {e['nombre']} | cat={e['categoria']} | check={e['checksum']} | {e['sellado_en'][:10]}")

    if not v.listar_entradas():
        print("  (bóveda vacía — lista para sellar secretos)")
    print()
