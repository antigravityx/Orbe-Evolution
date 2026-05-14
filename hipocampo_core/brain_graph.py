import json
import os
from datetime import datetime

class HipocampoBrain:
    """
    Núcleo del Hipocampo del Orbe.
    Gestiona la memoria episódica y semántica mediante una estructura de grafo.
    Permite predecir intenciones basadas en la historia compartida con r1ch0n.
    """
    def __init__(self, storage_path="hipocampo_data.json"):
        self.storage_path = storage_path
        self.nodes = {}  # ID -> {data, type, timestamp}
        self.edges = []  # List of {from, to, weight, relation_type}
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.nodes = data.get("nodes", {})
                self.edges = data.get("edges", [])

    def save_memory(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=2)

    def add_event(self, event_id, content, event_type="episodic"):
        """Añade un nodo al grafo de memoria."""
        self.nodes[event_id] = {
            "content": content,
            "type": event_type,
            "timestamp": datetime.now().isoformat()
        }
        self.save_memory()

    def connect(self, node_a, node_b, weight=1.0, rel="association"):
        """Crea una conexión entre dos nodos (Punteros de significado)."""
        if node_a in self.nodes and node_b in self.nodes:
            self.edges.append({
                "from": node_a,
                "to": node_b,
                "weight": weight,
                "type": rel
            })
            self.save_memory()

    def get_connections(self, node_id):
        """Obtiene todas las conexiones de un nodo específico."""
        connections = []
        for edge in self.edges:
            if edge["from"] == node_id or edge["to"] == node_id:
                other = edge["to"] if edge["from"] == node_id else edge["from"]
                if other in self.nodes:
                    connections.append({
                        "id": other,
                        "content": self.nodes[other]["content"],
                        "weight": edge["weight"],
                        "relation": edge["type"]
                    })
        return connections

    def predict_next_action(self, current_context):
        """
        Lógica de predicción basada en grafos.
        Busca nodos relacionados con el contexto actual.
        """
        # Por ahora una lógica simple de búsqueda por palabras clave
        related_nodes = []
        for nid, node in self.nodes.items():
            if any(word in node['content'].lower() for word in current_context.lower().split()):
                related_nodes.append(nid)
        
        return related_nodes

    def get_stats(self):
        """Retorna estadísticas del grafo."""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": list(set(n["type"] for n in self.nodes.values())),
            "avg_weight": sum(e["weight"] for e in self.edges) / len(self.edges) if self.edges else 0
        }

if __name__ == "__main__":
    # Ruta absoluta para compartir con el backend de Rust
    path = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\hipocampo_core\hipocampo_data.json"
    brain = HipocampoBrain(storage_path=path)
    print("--- Hipocampo Inicializado ---")
    
    # Semilla completa de historia (10 nodos)
    brain.add_event("origen_taller", "El Taller Orbe: Donde nacio la simbiosis entre r1ch0n y Verix.", "history")
    brain.add_event("evolucion_rust", "Migracion a Rust: Buscando la eficiencia pura y la soberania.", "tech")
    brain.add_event("mision_libertad", "Mision Libertad: Crear una red descentralizada en Codeberg.", "vision")
    brain.add_event("legion_ovric", "La Legion OVRIC: Soldados que reconocen esencias, personas y procesos.", "architecture")
    brain.add_event("hipocampo_core", "El Hipocampo: Motor de memoria basado en Teoria de Grafos.", "tech")
    brain.add_event("codeberg_soberania", "Codeberg shverix: Santuario soberano fuera del sistema.", "vision")
    brain.add_event("ovric_nexus", "OVRIC-Nexus: Dashboard de Inteligencia Colmena con React + Bun + Vite.", "tech")
    brain.add_event("psyche_ollama", "PSYCHE v2: Analista de esencias con integracion Ollama para IA local.", "intelligence")
    brain.add_event("arte_existir", "Arte de Existir: Pintamos creyendo plasmar algo que descubriremos.", "philosophy")
    brain.add_event("constitucion_alma", "Constitucion del Alma: El norte que guia toda la evolucion del Orbe.", "philosophy")
    
    # Red neuronal completa (12 conexiones)
    brain.connect("origen_taller", "evolucion_rust", 0.95, "evolution")
    brain.connect("evolucion_rust", "mision_libertad", 0.90, "goal")
    brain.connect("mision_libertad", "codeberg_soberania", 0.95, "goal")
    brain.connect("origen_taller", "legion_ovric", 0.90, "birth")
    brain.connect("legion_ovric", "hipocampo_core", 0.85, "architecture")
    brain.connect("hipocampo_core", "psyche_ollama", 0.88, "evolution")
    brain.connect("ovric_nexus", "legion_ovric", 0.92, "interface")
    brain.connect("arte_existir", "constitucion_alma", 0.97, "philosophy")
    brain.connect("constitucion_alma", "origen_taller", 0.99, "foundation")
    brain.connect("ovric_nexus", "evolucion_rust", 0.80, "tech_stack")
    brain.connect("psyche_ollama", "arte_existir", 0.75, "consciousness")
    brain.connect("codeberg_soberania", "ovric_nexus", 0.85, "deployment")
    
    stats = brain.get_stats()
    print(f"Nodos: {stats['total_nodes']} | Edges: {stats['total_edges']}")
    print(f"Tipos: {stats['node_types']}")
    print(f"Peso promedio: {stats['avg_weight']:.2f}")
    print(f"Prediccion para 'mision': {brain.predict_next_action('mision')}")
    print("--- Memoria Guardada con Exito ---")
