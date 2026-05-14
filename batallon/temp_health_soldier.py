import os
import time

TEMP_PATH = os.path.expandvars(r"%TEMP%")
SAFE_TO_DELETE_EXTENSIONS = [".tmp", ".log", ".bak", ".old"]
SAFE_TO_DELETE_FOLDERS = ["node-compile-cache", "vscode-typescript"]

def diagnose_temp():
    print(f"--- [SOLDADO SENTINEL] Iniciando Diagnóstico de Temporales ---")
    print(f"Ruta: {TEMP_PATH}\n")
    
    total_size = 0
    to_delete = []
    
    for root, dirs, files in os.walk(TEMP_PATH):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                size = os.path.getsize(file_path)
                total_size += size
                
                # Regla 1: Extensiones basura
                if any(name.lower().endswith(ext) for ext in SAFE_TO_DELETE_EXTENSIONS):
                    to_delete.append((file_path, size))
                
                # Regla 2: Carpetas de cache conocidas
                elif any(folder in root for folder in SAFE_TO_DELETE_FOLDERS):
                    to_delete.append((file_path, size))
                    
            except:
                continue

    print(f"Tamaño total detectado: {total_size / (1024*1024):.2f} MB")
    print(f"Archivos identificados como 'basura segura': {len(to_delete)}")
    
    waste_size = sum(item[1] for item in to_delete)
    print(f"Espacio recuperable estimado: {waste_size / (1024*1024):.2f} MB")
    
    print("\n--- [TOP 5 ARCHIVOS PESADOS PARA ELIMINAR] ---")
    to_delete.sort(key=lambda x: x[1], reverse=True)
    for path, size in to_delete[:5]:
        print(f"[{size / (1024*1024):.2f} MB] {os.path.basename(path)}")
    
    return to_delete

def purge_temp(files_to_delete):
    print(f"\n--- [SOLDADO GOD_MODE] Iniciando Purga de Seguridad ---")
    recovered = 0
    errors = 0
    
    for path, size in files_to_delete:
        try:
            os.remove(path)
            recovered += size
            # print(f"[BORRADO] {os.path.basename(path)}")
        except Exception as e:
            errors += 1
            # print(f"[ERROR] No se pudo borrar {os.path.basename(path)}: {e}")
            
    print(f"\nPurga completada.")
    print(f"Espacio recuperado: {recovered / (1024*1024):.2f} MB")
    print(f"Errores (archivos en uso): {errors}")
    return recovered

if __name__ == "__main__":
    identified = diagnose_temp()
    if identified:
        # En un entorno real esto esperaría confirmación, 
        # pero Richon ya dio la orden: "Procede".
        purge_temp(identified)
