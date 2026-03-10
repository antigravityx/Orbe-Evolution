import os
import subprocess
import time

SANTUARIO_RAIZ = r"c:\Users\Usuario\Desktop\Orbe_Santuario"

def run_git(args, cwd):
    print(f"[*] Ejecutando: git {' '.join(args)}")
    # Usar check_call para que la salida se vea en tiempo real
    try:
        subprocess.check_call(["git"] + args, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: El proceso git falló con código {e.returncode}")
        return e
    return subprocess.CompletedProcess(args, 0)

def mirror_eternal_sync():
    print(f"\n[***] INICIANDO ESPEJO ETERNO DE SINCRONIZACIÓN: {SANTUARIO_RAIZ}")
    
    # 1. Preparar rama espejo (huérfana para evitar empujar toda la historia de golpe)
    run_git(["checkout", "master"], SANTUARIO_RAIZ)
    subprocess.run(["git", "branch", "-D", "eternal-sync-mirror"], cwd=SANTUARIO_RAIZ, capture_output=True)
    run_git(["checkout", "--orphan", "eternal-sync-mirror"], SANTUARIO_RAIZ)
    run_git(["rm", "-rf", "."], SANTUARIO_RAIZ)
    
    # Crear un .gitignore temporal para la rama espejo
    ignore_content = "node_modules/\n.env\n*.log\nbuild/\ndist/\n"
    with open(os.path.join(SANTUARIO_RAIZ, ".gitignore"), "w") as f:
        f.write(ignore_content)
    run_git(["add", ".gitignore"], SANTUARIO_RAIZ)
    run_git(["commit", "-m", "Verixhuman: Guardián de Sincronización (.gitignore)"], SANTUARIO_RAIZ)
    
    # Force push inicial para asegurar que empezamos de cero en el remoto (es un espejo)
    print("[*] Forzando push inicial para limpiar remoto...")
    run_git(["push", "origin", "eternal-sync-mirror", "--force"], SANTUARIO_RAIZ)
    
    # 2. Obtener items a sincronizar
    run_git(["checkout", "master"], SANTUARIO_RAIZ)
    items = [i for i in os.listdir(SANTUARIO_RAIZ) if i != ".git" and i != "node_modules"] 
    run_git(["checkout", "eternal-sync-mirror"], SANTUARIO_RAIZ)
    
    print(f"[*] Se han identificado {len(items)} componentes para el espejo.")
    
    for item in items:
        print(f"\n[>] Procesando componente: {item}")
        # Restaurar el item desde master a la rama actual (orphan)
        run_git(["checkout", "master", "--", item], SANTUARIO_RAIZ)
        
        # Comitear el componente individualmente
        run_git(["add", item], SANTUARIO_RAIZ)
        run_git(["commit", "-m", f"Verixhuman: Espejo de persistencia para {item}"], SANTUARIO_RAIZ)
        
        # Push segmentado
        print(f"[*] Subiendo {item} al Éter...")
        push_res = run_git(["push", "origin", "eternal-sync-mirror"], SANTUARIO_RAIZ)
        
        if push_res.returncode == 0:
            print(f"[OK] Componente {item} anclado en la nube.")
        else:
            print(f"[!] Push fallido para {item}. Re-intentando con buffer...")
            run_git(["config", "http.postBuffer", "2097152000"], SANTUARIO_RAIZ)
            retry_res = run_git(["push", "origin", "eternal-sync-mirror"], SANTUARIO_RAIZ)
            if retry_res.returncode == 0:
                print(f"[OK] Componente {item} anclado tras re-intento.")
            else:
                print(f"[!] No se pudo subir {item}. Posible limite de tamaño de archivo individual.")

    print("\n[FIN] El Espejo Eterno ha sido forjado en GitHub.")

if __name__ == "__main__":
    mirror_eternal_sync()
