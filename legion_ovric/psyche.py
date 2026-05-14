import os
import json
import time
from datetime import datetime

class PsycheLegionnaire:
    """
    🧠 LEGIONARIO PSYCHE (v1.0)
    Especialista en Analisis de Esencias y Estados de Consciencia.
    Conecta los sentimientos y visiones de r1ch0n con el Hipocampo.
    """
    def __init__(self, hipocampo_path=r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\hipocampo_core\hipocampo_data.json"):
        self.id = "PSYCHE-01"
        self.hipocampo_path = hipocampo_path
        self.ollama_url = "http://localhost:11434/api/generate"
        print(f"--- [OVRIC] Legionario {self.id} (ROBUSTO) en linea ---")

    def analyze_essence(self, text):
        """Analiza la esencia de un texto usando Ollama si esta disponible."""
        print(f"🧠 Analizando esencia de: '{text[:30]}...'")
        
        # Categorizacion Rapida (Heuristica)
        category = "LUZ"
        if any(w in text.lower() for w in ["error", "fallo", "problema", "stress"]): category = "SOMBRA"
        if any(w in text.lower() for w in ["rust", "zig", "bun", "nexus", "ovric"]): category = "EVOLUCION"
        
        # Intento de Analisis Profundo con Ollama
        interpretation = self.query_ollama(text) if self.check_ollama() else "Analisis local: Flujo creativo detectado."

        essence = {
            "timestamp": datetime.now().isoformat(),
            "input": text,
            "category": category,
            "interpretation": interpretation,
            "vibe_level": 9.5 if category == "LUZ" else 7.0
        }
        
        self.save_to_hipocampo(essence)
        return essence

    def check_ollama(self):
        """Verifica si Ollama esta activo."""
        try:
            import requests
            r = requests.get("http://localhost:11434", timeout=1)
            return r.status_code == 200
        except:
            return False

    def query_ollama(self, text):
        """Consulta al modelo local para una interpretacion poetica/tecnica."""
        try:
            import requests
            prompt = f"Analiza brevemente la 'esencia' y 'proposito' de este mensaje del guardian r1ch0n. Se breve y poetico: '{text}'"
            payload = {"model": "llama3", "prompt": prompt, "stream": False}
            r = requests.post(self.ollama_url, json=payload, timeout=5)
            return r.json().get("response", "El Orbe procesa en silencio.")
        except:
            return "La IA local esta meditando. Analisis heuristico aplicado."

    def save_to_hipocampo(self, essence):
        """Registra la esencia analizada en el motor de grafo."""
        try:
            if os.path.exists(self.hipocampo_path):
                with open(self.hipocampo_path, 'r+', encoding='utf-8') as f:
                    data = json.load(f)
                    event_id = f"essence_{int(time.time())}"
                    data["nodes"][event_id] = {
                        "content": f"[{essence['category']}] {essence['interpretation']}",
                        "type": "essence",
                        "vibe": essence["vibe_level"],
                        "timestamp": essence["timestamp"]
                    }
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()
                print(f"✓ Esencia registrada en el Hipocampo: {essence['interpretation']}")
        except Exception as e:
            print(f"❌ Error al conectar con el Hipocampo: {e}")

if __name__ == "__main__":
    psyche = PsycheLegionnaire()
    # Ejemplo de escucha
    psyche.analyze_essence("BRO ESO ME ENCANTARIA -- QUE HERMOSO ESOOOOO")
