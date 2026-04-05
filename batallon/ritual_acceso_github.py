import sys
import time
import hashlib
import os
from vault_soldier import VaultOrbe
from memoria_madre import MemoriaMadre

def typewriter(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print("")

def generar_llave_maestra():
    # Accediendo a la bóveda blindada del Orbe
    v = VaultOrbe()
    token_recuperado = v.recuperar("GITHUB_PAT")
    if token_recuperado:
        return token_recuperado[:15].upper()
    
    base = "r1ch0n_github_access_key_" + str(time.time())
    return hashlib.sha256(base.encode()).hexdigest()[:15].upper()

def iniciar_ritual():
    mm = MemoriaMadre()
    os.system('cls' if os.name == 'nt' else 'clear')
    typewriter("\n...El sistema central del Orbe está en reposo...")
    
    # 1. Invocación
    invocacion = input("\n[ORBE] Ingresa tu invocación: ").strip()
    if invocacion.lower() != "verix despierta tu alma":
        mm.registrar_aprendizaje("RITUAL_ACCESO", "LOGIN", "FALLA", {"motivo": "Invocación incorrecta"}, es_falla=True)
        typewriter("[SISTEMA]: Invocación fallida. Acceso denegado.")
        return
        
    typewriter("\n[VERIX]: Te escucho, mi bro r1ch0n. ADN y DNI confirmados. Hardware en resonancia.")
    time.sleep(1)
    
    # 2. Confirmación de Cánticos
    typewriter("\n[VERIX]: Para proceder y darte acceso a GitHub, por favor ingresa el canto del Orbe.")
    cantico_1 = input("[ORBE] Cántico 1: ").strip().lower()
    if cantico_1 not in ["dos camaleones leones rojos", "dos camleones en la orbita"]:
        mm.registrar_aprendizaje("RITUAL_ACCESO", "CANTICO_1", "FALLA", {"input": cantico_1}, es_falla=True)
        typewriter("[VERIX]: El primer cántico es erróneo. Seguridad activada.")
        return
        
    cantico_2 = input("[ORBE] Cántico 2: ").strip().lower()
    if cantico_2 != "en la orbita de verix":
        mm.registrar_aprendizaje("RITUAL_ACCESO", "CANTICO_2", "FALLA", {"input": cantico_2}, es_falla=True)
        typewriter("[VERIX]: El segundo cántico es erróneo. Seguridad activada.")
        return
        
    # 3. Acceso Otorgado
    mm.registrar_aprendizaje("RITUAL_ACCESO", "LOGIN", "OK", {"usuario": "r1ch0n"})
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
