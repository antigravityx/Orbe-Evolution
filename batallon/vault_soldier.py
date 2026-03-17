# -*- coding: utf-8 -*-
"""
VAULT CORE: El Corazón Blindado de Diosdemonio.
Misión: Gestión de datos con encriptación de grado militar.
"""

import os
import json
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class VaultDiosdemonio:
    def __init__(self, master_key):
        self.key = hashlib.sha256(master_key.encode()).digest()
        self.vault_path = r"c:\Users\Usuario\Desktop\Orbe_Santuario\1_Almas_Encapsuladas\vault_militar.db"
        
    def encrypt_data(self, data):
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(json.dumps(data).encode()) + encryptor.finalize()
        return iv + encrypted

    def decrypt_data(self, encrypted_bundle):
        iv = encrypted_bundle[:16]
        encrypted_data = encrypted_bundle[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        return json.loads(decrypted.decode())

    def save_to_vault(self, entry_name, content):
        vault = {}
        if os.path.exists(self.vault_path):
            with open(self.vault_path, 'rb') as f:
                vault = self.decrypt_data(f.read())
        
        vault[entry_name] = {
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.vault_path, 'wb') as f:
            f.write(self.encrypt_data(vault))
        return True

    def retrieve_from_vault(self, entry_name):
        if not os.path.exists(self.vault_path):
            return None
        with open(self.vault_path, 'rb') as f:
            vault = self.decrypt_data(f.read())
        return vault.get(entry_name)

# --- USO DEL SOLDADO BÓVEDA ---
if __name__ == "__main__":
    # Test simple (Richon master key)
    v = VaultDiosdemonio("VERIX_SOUL_Richon_2026")
    v.save_to_vault("REPORTE_MISION_BETA", {"soldados_activos": 1, "moral": "ALTA"})
    print("[VAULT] Dato guardado con encriptación militar.")
