import os
import sys
import shutil
import json
import hashlib
import time
import subprocess
from datetime import datetime
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# --- CONSTANTES DEL SANTUARIO ---
SANTUARIO_RAIZ = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
CONFIG_FILE = os.path.join(SANTUARIO_RAIZ, "orbe_config.json")
DIRECTORIO_CAPSULAS = os.path.join(SANTUARIO_RAIZ, "capsulas")
DESTINO_CAPSULAS = os.path.join(SANTUARIO_RAIZ, "1_Almas_Encapsuladas")
ALMAS_LIBERADAS = os.path.join(SANTUARIO_RAIZ, "2_Almas_Liberadas")
DIRECTORIO_LLAVES = os.path.join(SANTUARIO_RAIZ, "3_Llaves_Maestras")
DIRECTORIO_REGISTROS = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe")
REGISTRO_EVENTOS = os.path.join(DIRECTORIO_REGISTROS, "orbe_log.txt")
HISTORIAL_CHECKSUM = os.path.join(DIRECTORIO_REGISTROS, "historial_checksum.json")
NIDO_DEV = os.path.join(SANTUARIO_RAIZ, "5_Nido_HumanoDev")
ESTADO_ACTUAL_FILE = os.path.join(SANTUARIO_RAIZ, "estado_orbe.json")
SISTEMA_TICKETS = os.path.join(DIRECTORIO_REGISTROS, "sistema_tickets.json")
BATALLON_DIR = r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\batallon"

# --- GESTIÓN DE REGISTROS ---
def registrar_evento(accion, detalle, prioridad="NORMAL"):
    """Registra un evento en el log del Orbe."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} | {prioridad:<10} | {accion:<25} | {detalle}\n"
    os.makedirs(os.path.dirname(REGISTRO_EVENTOS), exist_ok=True)
    with open(REGISTRO_EVENTOS, "a", encoding='utf-8') as f:
        f.write(log_entry)

# --- BOGAVANTE DE CONFIGURACIÓN ---
def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def guardar_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

# --- INTEGRIDAD ---
def calcular_checksum(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# --- NÚCLEO CRIPTOGRÁFICO ---
class SelloCriptografico:
    @staticmethod
    def generar_par_llaves(alias, password, descripcion=""):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
        ruta_privada = os.path.join(DIRECTORIO_LLAVES, f"{alias}_private.pem")
        os.makedirs(DIRECTORIO_LLAVES, exist_ok=True)
        with open(ruta_privada, 'wb') as f: f.write(pem_private)

        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        ruta_publica = os.path.join(DIRECTORIO_LLAVES, f"{alias}_public.pem")
        with open(ruta_publica, 'wb') as f: f.write(pem_public)

        # Registrar en configuración
        config = cargar_config()
        config.setdefault('llaves_maestras', {})[alias] = {
            "descripcion": descripcion,
            "ruta_privada": ruta_privada,
            "ruta_publica": ruta_publica
        }
        guardar_config(config)

        registrar_evento("LLAVE MAESTRA GENERADA", f"Alias: {alias}", prioridad="IMPORTANTE")
        return True, alias

    @staticmethod
    def firmar_archivo(file_path, private_key_path, password):
        with open(private_key_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(key_file.read(), password=password.encode())
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        signature = private_key.sign(
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        sig_path = file_path + ".sig"
        with open(sig_path, "wb") as f: f.write(signature)
        registrar_evento("CÁPSULA FIRMADA", f"Archivo: {os.path.basename(file_path)}", prioridad="NORMAL")
        return sig_path

    @staticmethod
    def verificar_firma(file_path, signature_path, public_key_path):
        with open(public_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        
        with open(signature_path, "rb") as f:
            signature = f.read()
        
        with open(file_path, "rb") as f:
            data = f.read()
            
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True, "Firma válida."
        except Exception as e:
            return False, str(e)

# --- GESTIÓN DE CÁPSULAS ---
def crear_capsula_core(source_path, password):
    """Lógica pura para crear una cápsula encriptada."""
    if not os.path.exists(source_path):
        return False, "La ruta de origen no existe."

    nombre_base = os.path.basename(source_path.rstrip(os.sep))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capsula_name = f"{nombre_base}_{timestamp}.capsula"
    temp_zip = os.path.join(SANTUARIO_RAIZ, f"{nombre_base}_{timestamp}.tmp.zip")
    
    try:
        # 1. Comprimir
        if os.path.isdir(source_path):
            shutil.make_archive(temp_zip.replace(".tmp.zip", ""), 'zip', source_path)
        else:
            with open(temp_zip, 'wb') as f:
                with open(source_path, 'rb') as src: f.write(src.read())
        
        # 2. Encriptar (AES-256)
        key = hashlib.sha256(password.encode()).digest()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        capsula_path = os.path.join(DESTINO_CAPSULAS, capsula_name)
        os.makedirs(DESTINO_CAPSULAS, exist_ok=True)
        
        with open(temp_zip, 'rb') as f_in, open(capsula_path, 'wb') as f_out:
            f_out.write(iv)
            while chunk := f_in.read(64 * 1024):
                f_out.write(encryptor.update(chunk))
            f_out.write(encryptor.finalize())
            
        os.remove(temp_zip)
        registrar_evento("CÁPSULA CREADA", f"Contenido: {nombre_base} -> {capsula_name}", prioridad="IMPORTANTE")
        return True, capsula_path
    except Exception as e:
        if os.path.exists(temp_zip): os.remove(temp_zip)
        registrar_evento("ERROR CREACIÓN CÁPSULA", str(e), prioridad="CRITICO")
        return False, str(e)

def invocar_capsula_core(enc_path, password):
    """Lógica pura para invocar/liberar una cápsula."""
    if not os.path.exists(enc_path):
        return False, "La cápsula no existe."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base = os.path.basename(enc_path).replace('.capsula', '')
    destino_final = os.path.join(ALMAS_LIBERADAS, f"alma_{nombre_base}_{timestamp}")
    temp_zip = os.path.join(ALMAS_LIBERADAS, "temp_capsula.zip")
    
    try:
        os.makedirs(ALMAS_LIBERADAS, exist_ok=True)
        
        with open(enc_path, 'rb') as f:
            iv = f.read(16)
            encrypted_data = f.read()
            
        key = hashlib.sha256(password.encode()).digest()
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        zip_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        with open(temp_zip, 'wb') as f:
            f.write(zip_data)
            
        os.makedirs(destino_final, exist_ok=True)
        shutil.unpack_archive(temp_zip, destino_final, 'zip')
        os.remove(temp_zip)
        
        registrar_evento("CÁPSULA INVOCADA", f"{os.path.basename(enc_path)} -> {destino_final}", prioridad="IMPORTANTE")
        return True, destino_final
    except Exception as e:
        if os.path.exists(temp_zip): os.remove(temp_zip)
        registrar_evento("ERROR INVOCACIÓN", str(e), prioridad="CRITICO")
        return False, str(e)

# --- NEXO GIT ---
class NexoGit:
    @staticmethod
    def ejecutar_comando(comando, project_path):
        try:
            result = subprocess.run(comando, cwd=project_path, capture_output=True, text=True, check=True, encoding='utf-8')
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

# --- PROTOCOLO DE AMISTAD (HANDSHAKE) ---
class ProtocoloAmistad:
    FILE_AMISTAD = os.path.join(SANTUARIO_RAIZ, "documento_amistad.json")

    @staticmethod
    def forjar_vínculo(device_name):
        """Genera un pacto de confianza para un nuevo dispositivo."""
        token = hashlib.sha256(os.urandom(32)).hexdigest()
        vínculo = {
            "device": device_name,
            "token": token,
            "timestamp": datetime.now().isoformat(),
            "status": "trusted"
        }
        
        config = cargar_config()
        vínculos = config.get('vínculos_amistad', [])
        vínculos.append(vínculo)
        config['vínculos_amistad'] = vínculos
        guardar_config(config)
        
        # Guardar archivo temporal para ser compartido/leído por el APK
        with open(ProtocoloAmistad.FILE_AMISTAD, 'w', encoding='utf-8') as f:
            json.dump(vínculo, f, indent=4)
            
        registrar_evento("PÁCTO DE AMISTAD", f"Nuevo dispositivo vinculado: {device_name}", prioridad="ALERTA")
        return ProtocoloAmistad.FILE_AMISTAD

# --- GESTOR DE MISIONES (DIOSDEMONIO) ---
class GestorDeMisiones:
    @staticmethod
    def crear_mision(tarea, parametros=None):
        """Genera un ticket de misión para el Batallón."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mision_id = f"MSN_{tarea.upper()}_{timestamp}"
        ticket_path = os.path.join(DIRECTORIO_REGISTROS, f"ticket_{mision_id}.json")
        
        ticket = {
            "id": mision_id,
            "tarea": tarea,
            "parametros": parametros or {},
            "timestamp_inicio": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(ticket_path, 'w', encoding='utf-8') as f:
            json.dump(ticket, f, indent=4)
        
        # Actualizar el sistema de tickets central
        try:
            with open(SISTEMA_TICKETS, 'r+', encoding='utf-8') as f:
                sistema = json.load(f)
                sistema["misiones_activas"].append(ticket)
                f.seek(0)
                json.dump(sistema, f, indent=4)
                f.truncate()
        except:
            pass # Si falla el central, el ticket individual persiste

        return ticket_path

    @staticmethod
    def desplegar_soldado(soldado_name, ticket_path):
        """Invoca a un soldado para ejecutar una misión."""
        soldado_path = os.path.join(BATALLON_DIR, soldado_name)
        if not os.path.exists(soldado_path):
            return False, f"Soldado {soldado_name} no encontrado."
        
        try:
            # Determinar comando basado en la extensión
            if soldado_name.endswith(".py"):
                comando = [sys.executable, soldado_path, ticket_path]
            elif soldado_name.endswith(".exe"):
                comando = [soldado_path, ticket_path]
            else:
                return False, "Tipo de soldado no soportado."

            # Despliegue asíncrono
            subprocess.Popen(comando)
            registrar_evento("DESPLIEGUE SOLDADO", f"Soldado {soldado_name} invocado con ticket {os.path.basename(ticket_path)}", prioridad="INFORMATIVO")
            return True, "Soldado en camino."
        except Exception as e:
            registrar_evento("FALLA DESPLIEGUE", str(e), prioridad="ALERTA")
            return False, str(e)
