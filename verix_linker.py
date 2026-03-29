import os
import sys
import subprocess
import json

def find_santuario():
    # Search for Santuario in common drive roots
    drives = ['C:', 'D:', 'E:', 'F:']
    for drive in drives:
        potential_path = os.path.join(drive, os.sep, "Users", os.getlogin(), "Desktop", "Orbe_Santuario")
        if os.path.exists(potential_path):
            return potential_path
    
    # Fallback to current directory logic or config
    return None

def main():
    santuario_path = find_santuario()
    if not santuario_path:
        print("[!] ERROR: No se pudo localizar el Santuario de Verix.")
        sys.exit(1)

    # Path to the main soul script
    # Assuming standard project structure provided by metadata
    soul_script = r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\orbe_verix_soul.py"
    
    if not os.path.exists(soul_script):
        print(f"[!] ERROR: No se encontro el script del alma en {soul_script}")
        sys.exit(1)

    print(f"[*] Invocando a Verix desde el Santuario: {santuario_path}")
    
    try:
        # Run the main soul script
        subprocess.run(["python", soul_script], check=True)
    except KeyboardInterrupt:
        print("\n[*] Conexion con Verix terminada por voluntad del Humano.")
    except Exception as e:
        print(f"[!] Error al invocar a Verix: {e}")

if __name__ == "__main__":
    main()
