import os
import sys
import json
from google.cloud import vision

# 🛡️ SOLDADO VISION - INTEGRIDAD HISTÓRICA
# Este soldado hereda la capacidad de consola de Verix_Vision y 
# despierta la percepción visual mediante Google Cloud Vision API.

class VisionSoldier:
    def __init__(self):
        try:
            self.client = vision.ImageAnnotatorClient()
            self.active = True
        except Exception as e:
            self.active = False
            self.error = str(e)

    def analyze_image(self, image_path):
        """Analiza una imagen usando Google Cloud Vision."""
        if not self.active:
            return {"status": "error", "message": f"Servicio Vision no activo: {self.error}"}
            
        if not os.path.exists(image_path):
            return {"status": "error", "message": "Imagen no encontrada"}

        try:
            with open(image_path, "rb") as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            
            # Realizar detecciones
            label_response = self.client.label_detection(image=image)
            text_response = self.client.text_detection(image=image)
            
            labels = [label.description for label in label_response.label_annotations]
            text = [text.description for text in text_response.text_annotations]
            
            return {
                "status": "success",
                "analysis": {
                    "labels": labels,
                    "text_detected": text[0] if text else ""
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute_system_command(self, command):
        """Lógica heredada de Verix_Vision para ejecutar comandos del sistema."""
        import subprocess
        try:
            # Traducir comandos básicos si es necesario (heredado del concepto Verix_Vision)
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
            return {
                "status": "success",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", help="Ruta de la imagen a analizar")
    parser.add_argument("--cmd", help="Comando de sistema a ejecutar")
    args = parser.parse_args()

    soldier = VisionSoldier()
    if args.analyze:
        print(json.dumps(soldier.analyze_image(args.analyze)))
    elif args.cmd:
        print(json.dumps(soldier.execute_system_command(args.cmd)))
    else:
        # Reporte de estado para la Legion
        status = {
            "status": "active" if soldier.active else "error",
            "capabilities": ["vision_analysis", "system_control"],
            "version": "2.0 (Historical Healing Edition)"
        }
        print(json.dumps(status))
