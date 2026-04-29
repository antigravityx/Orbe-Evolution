# -*- coding: utf-8 -*-
"""
DEPLOY NÁUFRAGO — Script de despliegue FTP a Hostinger
======================================================
Sube los archivos del sitio a sombrereronaufrago.com via FTP.
Credenciales se obtienen del VaultOrbe (AES-256).

Uso: python deploy_naufrago.py
"""

import os
import sys
import ftplib

ORBE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ORBE_ROOT)

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
REMOTE_DIR = "/public_html"

VAULT_KEYS = {
    "host": "HOSTINGER_FTP_HOST",
    "user": "HOSTINGER_FTP_USER",
    "pass": "HOSTINGER_FTP_PASS"
}

def get_credentials():
    try:
        from batallon.vault_soldier import VaultOrbe
        vault = VaultOrbe()
        creds = {}
        for key, vault_key in VAULT_KEYS.items():
            val = vault.recuperar(vault_key)
            if not val:
                print(f"[!] Credencial {vault_key} no encontrada en el Vault.")
                return None
            creds[key] = val
        return creds
    except Exception as e:
        print(f"[!] Error accediendo al Vault: {e}")
        return None

def upload_dir(ftp, local_dir, remote_dir):
    count = 0
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"

        if item.startswith('.') or item == '__pycache__' or item.endswith('.py'):
            continue

        if os.path.isdir(local_path):
            try:
                ftp.mkd(remote_path)
            except ftplib.error_perm:
                pass
            count += upload_dir(ftp, local_path, remote_path)
        else:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
                print(f"  -> {remote_path}")
                count += 1
    return count

def main():
    print("\n" + "=" * 50)
    print("  DEPLOY NÁUFRAGO -> sombrereronaufrago.com")
    print("=" * 50 + "\n")

    creds = get_credentials()
    if not creds:
        print("\n[!] Sellá las credenciales FTP primero:")
        print("    python -c \"from batallon.vault_soldier import VaultOrbe; v=VaultOrbe(); v.guardar('HOSTINGER_FTP_HOST','tu_host','FTP'); v.guardar('HOSTINGER_FTP_USER','tu_user','FTP'); v.guardar('HOSTINGER_FTP_PASS','tu_pass','FTP')\"")
        return

    print(f"[*] Conectando a {creds['host']}...")
    try:
        ftp = ftplib.FTP(creds['host'])
        ftp.login(creds['user'], creds['pass'])
        ftp.encoding = 'utf-8'
        print(f"[OK] Conectado como {creds['user']}")

        try:
            ftp.cwd(REMOTE_DIR)
        except:
            pass

        print(f"[*] Subiendo archivos desde {SITE_DIR}...")
        count = upload_dir(ftp, SITE_DIR, ".")
        ftp.quit()
        print(f"\n[OK] {count} archivos desplegados exitosamente.")
        print(f"[OK] Sitio live en: https://sombrereronaufrago.com")
    except Exception as e:
        print(f"\n[ERROR] {e}")

if __name__ == "__main__":
    main()
