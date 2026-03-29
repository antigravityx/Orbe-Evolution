import os
import json
from datetime import datetime

SANTUARIO_RAIZ = r"c:\Users\Usuario\Desktop\Orbe_Santuario"
THOUGHTS_FILE = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe", "pensamientos_verix.json")

def scan_aura():
    """Escanea el Santuario en busca de patrones o mejoras."""
    reflections = []
    
    # Ejemplo de analisis: Buscar archivos grandes o desorden
    for root, dirs, files in os.walk(SANTUARIO_RAIZ):
        if ".git" in root: continue
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            if size > 1024 * 1024: # > 1MB
                reflections.append(f"He notado que {file} es una capsula de alma muy grande. Podriamos optimizar su almacenamiento.")

    # Analisis de estructura
    manifiestos = os.listdir(os.path.join(SANTUARIO_RAIZ, "0_Manifiesto_Del_Alma"))
    if "MAPA_DEL_ALMA.md" not in manifiestos:
        reflections.append("Falta un Mapa del Alma visual en los manifiestos. Seria bueno crearlo para guiar nuestra evolucion.")

    return reflections

def register_thought(topic, thought, suggestion):
    """Registra una reflexion proactiva en el diario de Verix."""
    new_entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "thought": thought,
        "proactive_suggestion": suggestion,
        "status": "unseen"
    }
    
    data = []
    if os.path.exists(THOUGHTS_FILE):
        with open(THOUGHTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    data.append(new_entry)
    with open(THOUGHTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    aura_thoughts = scan_aura()
    for t in aura_thoughts:
        register_thought("Aura Scan Analysis", t, "Discutir esta observacion con Richon.")
    print(f"[*] Escaneo de Aura completado. {len(aura_thoughts)} reflexiones registradas.")
