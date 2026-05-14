import time
import os

class ExistenceJustifier:
    """
    Registrador de Actividad (Keystroke Patterns).
    Su misión es 'justificar la existencia' del Guardián r1ch0n
    mediante el aprendizaje de su cadencia y ritmo de trabajo.
    """
    def __init__(self, log_dir="logs/existence"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def record_heartbeat(self, activity_type="tipeo"):
        """Registra un pulso de existencia en el log."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(self.log_dir, "pulso_vida.log"), "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] PULSO: {activity_type} - r1ch0n presente.\n")

    def analyze_cadence(self):
        """Analizaría los intervalos entre pulsos para predecir fatiga o flujo."""
        return "Cadencia estable. Flujo creativo detectado."

if __name__ == "__main__":
    justifier = ExistenceJustifier()
    print("💓 Guardián de Existencia Activo.")
    justifier.record_heartbeat("Inicio de sesión Verix")
