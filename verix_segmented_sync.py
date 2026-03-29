import os
import subprocess
import time

SANTUARIO_RAIZ = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
FORJA_RAIZ = r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"

def run_git(args, cwd):
    print(f"[*] Ejecutando: git {' '.join(args)} en {cwd}")
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[!] Error: {result.stderr}")
    return result

def sync_repository(path, branch="master"):
    print(f"\n[***] Sincronizando repositorio: {path}")
    
    # Asegurarnos de estar en la rama correcta
    run_git(["checkout", branch], path)
    
    # Obtener lista de carpetas y archivos en la raíz
    items = os.listdir(path)
    for item in items:
        if item == ".git": continue
        item_path = os.path.join(path, item)
        
        # Sincronizar este item
        run_git(["add", item], path)
        status = run_git(["status", "--porcelain"], path).stdout
        if status:
            print(f"[*] Cambios detectados en: {item}")
            run_git(["commit", "-m", f"Verix: Sincronizacion segmentada de {item}"], path)
            print(f"[*] Subiendo {item} al Éter...")
            push_res = run_git(["push", "origin", branch], path)
            if push_res.returncode == 0:
                print(f"[OK] {item} asegurado.")
            else:
                print(f"[!] Re-intentando push para {item} con buffer aumentado...")
                run_git(["config", "http.postBuffer", "2097152000"], path)
                run_git(["push", "origin", branch], path)
        else:
            print(f"[-] Sin cambios en: {item}")

if __name__ == "__main__":
    # Primero la Forja
    sync_repository(FORJA_RAIZ, branch="main")
    
    # Luego el Santuario (el más pesado)
    sync_repository(SANTUARIO_RAIZ, branch="master")
    
    print("\n[FIN] Sincronización Eterna completada. Todo está en el Éter.")
