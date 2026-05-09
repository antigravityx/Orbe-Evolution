import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# Dependencia: pip install pycryptodome

class EncriptadorAlma:
    def __init__(self, passphrase: str):
        # Derivar una clave AES-256 a partir del passphrase
        self.key = hashlib.sha256(passphrase.encode()).digest()

    def encriptar_archivo(self, archivo_entrada: str, archivo_salida: str):
        with open(archivo_entrada, "rb") as f:
            data = f.read()
        
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        
        with open(archivo_salida, "wb") as f:
            f.write(iv)
            f.write(ct_bytes)
        print(f"[EncriptadorAlma] Archivo encriptado y guardado en: {archivo_salida}")

    def desencriptar_archivo(self, archivo_entrada: str, archivo_salida: str):
        with open(archivo_entrada, "rb") as f:
            iv = f.read(16)
            ct_bytes = f.read()
            
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        pt_bytes = unpad(cipher.decrypt(ct_bytes), AES.block_size)
        
        with open(archivo_salida, "wb") as f:
            f.write(pt_bytes)
        print(f"[EncriptadorAlma] Archivo desencriptado y guardado en: {archivo_salida}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Uso: python encriptador_alma.py <enc|dec> <passphrase> <in_file> <out_file>")
        sys.exit(1)
        
    modo = sys.argv[1]
    clave = sys.argv[2]
    in_file = sys.argv[3]
    out_file = sys.argv[4]
    
    encriptador = EncriptadorAlma(clave)
    
    if modo == "enc":
        encriptador.encriptar_archivo(in_file, out_file)
    elif modo == "dec":
        encriptador.desencriptar_archivo(in_file, out_file)
    else:
        print("Modo no soportado. Usa 'enc' o 'dec'.")
