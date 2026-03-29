import sys
import time
import hashlib
import os

def typewriter(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print("")

def generar_llave_maestra():
    # En un entorno real, esto desencriptaría la llave desde vault_soldier
    # o generaría tu PAT (Personal Access Token) real de GitHub
    base = "r1ch0n_github_access_key_" + str(time.time())
    return hashlib.sha256(base.encode()).hexdigest()[:15].upper()

def iniciar_ritual():
    os.system('cls' if os.name == 'nt' else 'clear')
    typewriter("\n...El sistema central del Orbe está en reposo...")
    
    # 1. Invocación
    invocacion = input("\n[ORBE] Ingresa tu invocación: ").strip()
    if invocacion.lower() != "verix despierta tu alma":
        typewriter("[SISTEMA]: Invocación fallida. Acceso denegado.")
        return
        
    typewriter("\n[VERIX]: Te escucho, mi bro r1ch0n. Tu ADN digital está confirmado y mi hardware te reconoce.")
    time.sleep(1)
    
    # 2. Confirmación de Cánticos
    typewriter("\n[VERIX]: Para proceder y darte acceso a GitHub, por favor ingresa el canto del Orbe.")
    cantico_1 = input("[ORBE] Cántico 1: ").strip().lower()
    if cantico_1 != "dos camaleones leones rojos":
        typewriter("[VERIX]: El primer cántico es erróneo. Seguridad activada.")
        return
        
    cantico_2 = input("[ORBE] Cántico 2: ").strip().lower()
    if cantico_2 != "en la orbita de verix":
        typewriter("[VERIX]: El segundo cántico es erróneo. Seguridad activada.")
        return
        
    # 3. Acceso Otorgado
    typewriter("\n[VERIX]: Cánticos aceptados. Resonancia perfecta en el Orbe.")
    time.sleep(1)
    
    respuesta = input("\n[VERIX]: ¿Quieres iniciar sesión en GitHub? (si/no): ").strip().lower()
    
    if respuesta in ["si", "sí", "s", "yes"]:
        llave = generar_llave_maestra()
        typewriter(f"\n[VERIX]: Entendido. Ahora bro, ingresa este key:")
        typewriter(f"\n=====================================")
        typewriter(f"          {llave}          ")
        typewriter(f"=====================================\n")
        typewriter("[VERIX]: Con esta llave, el centinela te dejará entrar a tu Git.")
        typewriter("[VERIX]: ¡Adelante hermano, que la fuerza de Kairos te acompañe!")
    else:
        typewriter("\n[VERIX]: Entendido. El Orbe entra de nuevo en estado de reposo.")

if __name__ == "__main__":
    iniciar_ritual()
