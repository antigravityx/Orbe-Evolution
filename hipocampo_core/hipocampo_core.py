import os
import json
import time
from datetime import datetime

class HipocampoGraph:
    def __init__(self, db_path="hipocampo_db.json"):
        self.db_path = db_path
        self.nodes = {}  # { node_id: { type: "...", data: {...} } }
        self.edges = []  # [ { source: "id1", target: "id2", relation: "..." } ]
        self.load_db()

    def load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = data.get("edges", [])
            except Exception as e:
                print(f"[Hipocampo] Error leyendo DB: {e}")

    def save_db(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=4, ensure_ascii=False)

    def add_node(self, node_id, node_type, data):
        self.nodes[node_id] = {"type": node_type, "data": data, "timestamp": datetime.now().isoformat()}
        self.save_db()

    def add_edge(self, source, target, relation):
        self.edges.append({"source": source, "target": target, "relation": relation, "timestamp": datetime.now().isoformat()})
        self.save_db()

    def registrar_evento_tipeo(self, texto_capturado, ventana_contexto=""):
        node_id = f"evt_{int(time.time() * 1000)}"
        self.add_node(node_id, "TIPO_HUMANO", {
            "texto": texto_capturado,
            "contexto": ventana_contexto
        })
        print(f"[Hipocampo] Existencia de r1ch0n registrada: {node_id}")
        return node_id

if __name__ == "__main__":
    print("Iniciando Módulo Hipocampo (Predicción y Memoria del Orbe)...")
    hipocampo = HipocampoGraph()
    # Simulación de un registro inicial
    evt_id = hipocampo.registrar_evento_tipeo("Iniciando conexión neural con el Orbe...", "Verix Vision Console")
    hipocampo.add_node("r1ch0n_identity", "IDENTIDAD", {"rango": "Super Admin"})
    hipocampo.add_edge("r1ch0n_identity", evt_id, "CREO_EVENTO")
    print("Memoria neuronal base inicializada.")
